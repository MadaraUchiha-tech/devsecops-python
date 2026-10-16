import { useState } from 'react';
import { Search, Trash2, UserPlus } from 'lucide-react';
import { api } from '../api';

export default function Patients({ patients, reload, notify }) {
  const [query, setQuery] = useState('');
  const [saving, setSaving] = useState(false);
  const q = query.trim().toLowerCase();
  const visible = q
    ? patients.filter((p) => p.full_name.toLowerCase().includes(q) || p.email.toLowerCase().includes(q))
    : patients;

  const add = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const f = new FormData(form);
    setSaving(true);
    try {
      const p = await api.createPatient({
        full_name: f.get('full_name').trim(),
        email: f.get('email').trim(),
        phone: f.get('phone').trim(),
        date_of_birth: f.get('dob') || null,
      });
      form.reset();
      notify(`Registered ${p.full_name}.`);
      reload();
    } catch (err) {
      notify(err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  const remove = async (p) => {
    if (!window.confirm(`Remove ${p.full_name} and all of their appointments?`)) return;
    try {
      await api.deletePatient(p.id);
      notify(`Removed ${p.full_name}.`);
      reload();
    } catch (err) {
      notify(err.message, 'error');
    }
  };

  return (
    <div className="stack">
      <header className="page-head">
        <div>
          <h1>Patients</h1>
          <p className="muted">{patients.length} registered</p>
        </div>
        <label className="search">
          <Search size={16} aria-hidden="true" />
          <span className="sr-only">Search patients</span>
          <input type="search" placeholder="Search by name or email" value={query} onChange={(e) => setQuery(e.target.value)} />
        </label>
      </header>

      <form className="panel inline-form" onSubmit={add} aria-labelledby="new-patient">
        <h2 id="new-patient" className="panel__title"><UserPlus size={18} aria-hidden="true" /> Register patient</h2>
        <label className="field"><span>Full name</span><input name="full_name" required minLength={2} autoComplete="off" /></label>
        <label className="field"><span>Email</span><input name="email" type="email" required autoComplete="off" /></label>
        <label className="field"><span>Phone</span><input name="phone" type="tel" autoComplete="off" /></label>
        <label className="field"><span>Date of birth</span><input name="dob" type="date" /></label>
        <button className="btn btn--primary" disabled={saving}>{saving ? 'Saving…' : 'Register'}</button>
      </form>

      <div className="table-wrap">
        <table>
          <thead>
            <tr><th scope="col">Name</th><th scope="col">Email</th><th scope="col">Phone</th><th scope="col">Date of birth</th><th scope="col"><span className="sr-only">Actions</span></th></tr>
          </thead>
          <tbody>
            {visible.map((p) => (
              <tr key={p.id}>
                <td data-label="Name"><strong>{p.full_name}</strong></td>
                <td data-label="Email">{p.email}</td>
                <td data-label="Phone" className="num">{p.phone || '—'}</td>
                <td data-label="Born" className="num">{p.date_of_birth || '—'}</td>
                <td className="row-actions">
                  <button className="icon-btn" onClick={() => remove(p)} aria-label={`Remove ${p.full_name}`}><Trash2 size={16} /></button>
                </td>
              </tr>
            ))}
            {visible.length === 0 && (
              <tr><td colSpan={5} className="muted table-empty">{q ? `No patient matches “${query}”.` : 'No patients yet. Register the first one above.'}</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
