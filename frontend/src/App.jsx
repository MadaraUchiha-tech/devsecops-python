import { useCallback, useEffect, useState } from 'react';
import { CalendarDays, Stethoscope, Users } from 'lucide-react';
import { api } from './api';
import Notice from './components/Notice';
import Schedule from './views/Schedule';
import Patients from './views/Patients';
import Doctors from './views/Doctors';

const VIEWS = [
  { id: 'schedule', label: 'Schedule', icon: CalendarDays },
  { id: 'patients', label: 'Patients', icon: Users },
  { id: 'doctors', label: 'Doctors', icon: Stethoscope },
];

const viewFromHash = () => {
  const id = window.location.hash.replace('#/', '');
  return VIEWS.some((v) => v.id === id) ? id : 'schedule';
};

export default function App() {
  const [view, setView] = useState(viewFromHash);
  const [doctors, setDoctors] = useState([]);
  const [patients, setPatients] = useState([]);
  const [notice, setNotice] = useState(null);

  const notify = useCallback((message, tone = 'success') => setNotice({ message, tone, at: Date.now() }), []);

  const loadDirectory = useCallback(async () => {
    try {
      const [d, p] = await Promise.all([api.doctors(), api.patients()]);
      setDoctors(d);
      setPatients(p);
    } catch (err) {
      notify(err.message, 'error');
    }
  }, [notify]);

  useEffect(() => {
    loadDirectory();
    const onHash = () => setView(viewFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, [loadDirectory]);

  useEffect(() => {
    if (!notice || notice.tone === 'error') return undefined;
    const t = setTimeout(() => setNotice(null), 4000);
    return () => clearTimeout(t);
  }, [notice]);

  return (
    <div className="shell">
      <a className="skip-link" href="#main">Skip to content</a>
      <aside className="rail">
        <div className="brand">
          <svg viewBox="0 0 32 32" width="32" height="32" aria-hidden="true">
            <rect width="32" height="32" rx="8" fill="currentColor" />
            <path d="M16 9v14M9 16h14" stroke="var(--rail)" strokeWidth="3.5" strokeLinecap="round" />
          </svg>
          <div>
            <strong>CareSlot</strong>
            <small>Front desk</small>
          </div>
        </div>
        <nav aria-label="Main">
          {VIEWS.map(({ id, label, icon: Icon }) => (
            <a key={id} href={`#/${id}`} aria-current={view === id ? 'page' : undefined}>
              <Icon size={18} aria-hidden="true" />
              <span>{label}</span>
            </a>
          ))}
        </nav>
        <p className="rail__foot">Riverside Family Clinic</p>
      </aside>

      <main id="main" className="content" tabIndex={-1}>
        <Notice notice={notice} onDismiss={() => setNotice(null)} />
        {view === 'schedule' && <Schedule doctors={doctors} patients={patients} notify={notify} />}
        {view === 'patients' && <Patients patients={patients} reload={loadDirectory} notify={notify} />}
        {view === 'doctors' && <Doctors doctors={doctors} reload={loadDirectory} notify={notify} />}
      </main>
    </div>
  );
}
