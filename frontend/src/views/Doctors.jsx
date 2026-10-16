import { useState } from 'react';
import { Stethoscope } from 'lucide-react';
import { api } from '../api';

export default function Doctors({ doctors, reload, notify }) {
  const [saving, setSaving] = useState(false);

  const add = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const f = new FormData(form);
    setSaving(true);
    try {
      const d = await api.createDoctor({
        full_name: f.get('full_name').trim(),
        specialty: f.get('specialty').trim(),
        room: f.get('room').trim(),
      });
      form.reset();
      notify(`Added ${d.full_name}.`);
      reload();
    } catch (err) {
      notify(err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  const toggle = async (d) => {
    try {
      await api.updateDoctor(d.id, { active: !d.active });
      notify(`${d.full_name} is now ${d.active ? 'off duty' : 'accepting appointments'}.`);
      reload();
    } catch (err) {
      notify(err.message, 'error');
    }
  };

  return (
    <div className="stack">
      <header className="page-head">
        <div>
          <h1>Doctors</h1>
          <p className="muted">{doctors.filter((d) => d.active).length} of {doctors.length} accepting appointments</p>
        </div>
      </header>

      <form className="panel inline-form" onSubmit={add} aria-labelledby="new-doctor">
        <h2 id="new-doctor" className="panel__title"><Stethoscope size={18} aria-hidden="true" /> Add doctor</h2>
        <label className="field"><span>Full name</span><input name="full_name" required minLength={2} placeholder="Dr. …" autoComplete="off" /></label>
        <label className="field"><span>Specialty</span><input name="specialty" required minLength={2} autoComplete="off" /></label>
        <label className="field"><span>Room</span><input name="room" maxLength={20} autoComplete="off" /></label>
        <button className="btn btn--primary" disabled={saving}>{saving ? 'Saving…' : 'Add doctor'}</button>
      </form>

      <div className="table-wrap">
        <table>
          <thead>
            <tr><th scope="col">Name</th><th scope="col">Specialty</th><th scope="col">Room</th><th scope="col">Availability</th></tr>
          </thead>
          <tbody>
            {doctors.map((d) => (
              <tr key={d.id} className={d.active ? '' : 'row--muted'}>
                <td data-label="Name"><strong>{d.full_name}</strong></td>
                <td data-label="Specialty">{d.specialty}</td>
                <td data-label="Room" className="num">{d.room || '—'}</td>
                <td data-label="Availability">
                  <label className="switch">
                    <input type="checkbox" role="switch" checked={d.active} onChange={() => toggle(d)} />
                    <span>{d.active ? 'On duty' : 'Off duty'}</span>
                  </label>
                </td>
              </tr>
            ))}
            {doctors.length === 0 && (
              <tr><td colSpan={4} className="muted table-empty">No doctors yet. Add the first one above.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
