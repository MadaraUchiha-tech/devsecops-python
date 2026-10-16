import { useState } from 'react';
import { CalendarPlus } from 'lucide-react';
import { api } from '../api';

export default function BookingPanel({ date, doctors, patients, onBooked, onError }) {
  const [submitting, setSubmitting] = useState(false);
  const [conflict, setConflict] = useState('');
  const activeDoctors = doctors.filter((d) => d.active);
  const ready = activeDoctors.length > 0 && patients.length > 0;

  const submit = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const f = new FormData(form);
    setSubmitting(true);
    setConflict('');
    try {
      const appt = await api.book({
        patient_id: Number(f.get('patient')),
        doctor_id: Number(f.get('doctor')),
        scheduled_at: new Date(`${f.get('date')}T${f.get('time')}`).toISOString(),
        duration_minutes: Number(f.get('duration')),
        reason: f.get('reason').trim(),
      });
      form.reset();
      onBooked(appt);
    } catch (err) {
      if (err.status === 409) setConflict(err.message);
      else onError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="panel" aria-labelledby="book-title">
      <h2 id="book-title" className="panel__title">
        <CalendarPlus size={18} aria-hidden="true" /> Book appointment
      </h2>
      {!ready ? (
        <p className="muted">Add at least one active doctor and one patient before booking.</p>
      ) : (
        <form className="form" onSubmit={submit} key={date}>
          <label className="field">
            <span>Patient</span>
            <select name="patient" required defaultValue="">
              <option value="" disabled>Choose a patient</option>
              {patients.map((p) => (
                <option key={p.id} value={p.id}>{p.full_name}</option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Doctor</span>
            <select name="doctor" required defaultValue="">
              <option value="" disabled>Choose a doctor</option>
              {activeDoctors.map((d) => (
                <option key={d.id} value={d.id}>{d.full_name} · {d.specialty}</option>
              ))}
            </select>
          </label>
          <div className="field-row">
            <label className="field">
              <span>Date</span>
              <input type="date" name="date" required defaultValue={date} />
            </label>
            <label className="field">
              <span>Time</span>
              <input type="time" name="time" required defaultValue="09:00" step="300" />
            </label>
          </div>
          <label className="field">
            <span>Length</span>
            <select name="duration" defaultValue="30">
              <option value="15">15 minutes</option>
              <option value="30">30 minutes</option>
              <option value="45">45 minutes</option>
              <option value="60">1 hour</option>
            </select>
          </label>
          <label className="field">
            <span>Reason for visit</span>
            <input name="reason" required minLength={2} maxLength={200} placeholder="e.g. Follow-up on blood test" />
          </label>
          {conflict && (
            <p className="field-error" role="alert">
              That slot is taken. {conflict}. Pick another time or doctor.
            </p>
          )}
          <button className="btn btn--primary" type="submit" disabled={submitting}>
            {submitting ? 'Booking…' : 'Book appointment'}
          </button>
        </form>
      )}
    </section>
  );
}
