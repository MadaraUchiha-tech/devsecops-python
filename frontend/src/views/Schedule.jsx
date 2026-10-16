import { useCallback, useEffect, useState } from 'react';
import { ChevronLeft, ChevronRight, Clock, Stethoscope } from 'lucide-react';
import { api } from '../api';
import { formatDay, formatTime, initials, shiftDate, toISODate } from '../format';
import StatusPill from '../components/StatusPill';
import BookingPanel from '../components/BookingPanel';

const NEXT_ACTIONS = {
  SCHEDULED: [
    { to: 'CHECKED_IN', label: 'Check in', primary: true },
    { to: 'NO_SHOW', label: 'No-show' },
    { to: 'CANCELLED', label: 'Cancel' },
  ],
  CHECKED_IN: [
    { to: 'COMPLETED', label: 'Complete', primary: true },
    { to: 'CANCELLED', label: 'Cancel' },
  ],
};

export default function Schedule({ doctors, patients, notify }) {
  const today = toISODate(new Date());
  const [date, setDate] = useState(today);
  const [appointments, setAppointments] = useState(null);
  const [stats, setStats] = useState(null);
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(async () => {
    try {
      const [list, s] = await Promise.all([api.appointments({ on_date: date }), api.stats()]);
      setAppointments(list);
      setStats(s);
    } catch (err) {
      setAppointments([]);
      notify(err.message, 'error');
    }
  }, [date, notify]);

  useEffect(() => {
    setAppointments(null);
    load();
  }, [load]);

  const move = async (appt, to) => {
    setBusyId(appt.id);
    try {
      await api.updateAppointment(appt.id, { status: to });
      await load();
    } catch (err) {
      notify(err.message, 'error');
    } finally {
      setBusyId(null);
    }
  };

  const counts = (appointments || []).reduce((acc, a) => ({ ...acc, [a.status]: (acc[a.status] || 0) + 1 }), {});
  const waiting = counts.CHECKED_IN || 0;

  return (
    <div className="schedule">
      <div className="schedule__main">
        <header className="page-head">
          <div>
            <h1>{date === today ? 'Today' : formatDay(date)}</h1>
            <p className="muted">
              {date === today && `${formatDay(date)} · `}
              {appointments ? `${appointments.length} appointments` : 'Loading appointments'}
              {waiting > 0 && ` · ${waiting} in the waiting room`}
            </p>
          </div>
          <div className="date-nav" role="group" aria-label="Change day">
            <button className="icon-btn icon-btn--bordered" onClick={() => setDate(shiftDate(date, -1))} aria-label="Previous day">
              <ChevronLeft size={18} />
            </button>
            <button className="btn btn--ghost" onClick={() => setDate(today)} disabled={date === today}>
              Today
            </button>
            <button className="icon-btn icon-btn--bordered" onClick={() => setDate(shiftDate(date, 1))} aria-label="Next day">
              <ChevronRight size={18} />
            </button>
          </div>
        </header>

        {stats && (
          <dl className="ledger" aria-label="Clinic totals">
            <div><dt>Upcoming</dt><dd>{stats.scheduled}</dd></div>
            <div><dt>Waiting</dt><dd>{stats.checked_in}</dd></div>
            <div><dt>Completed</dt><dd>{stats.completed}</dd></div>
            <div><dt>No-show / cancelled</dt><dd>{stats.cancelled + stats.no_show}</dd></div>
            <div><dt>Patients on file</dt><dd>{stats.patients}</dd></div>
          </dl>
        )}

        <section aria-label="Appointments for the day">
          {appointments === null ? (
            <ul className="timeline" aria-busy="true">
              {[0, 1, 2].map((i) => <li key={i} className="slot slot--skeleton" />)}
            </ul>
          ) : appointments.length === 0 ? (
            <div className="empty">
              <Clock size={28} aria-hidden="true" />
              <h2>No appointments on this day</h2>
              <p className="muted">Use the booking form to schedule a patient. Double-booked slots are rejected automatically.</p>
            </div>
          ) : (
            <ol className="timeline">
              {appointments.map((a) => (
                <li key={a.id} className={`slot slot--${a.status.toLowerCase()}`}>
                  <time className="slot__time" dateTime={a.scheduled_at}>
                    {formatTime(a.scheduled_at)}
                    <small>{a.duration_minutes} min</small>
                  </time>
                  <div className="slot__body">
                    <div className="slot__line">
                      <strong>{a.patient_name}</strong>
                      <StatusPill status={a.status} />
                    </div>
                    <p className="slot__reason">{a.reason}</p>
                    <p className="slot__meta">
                      <Stethoscope size={14} aria-hidden="true" /> {a.doctor_name} · {a.specialty}
                    </p>
                  </div>
                  {NEXT_ACTIONS[a.status] && (
                    <div className="slot__actions">
                      {NEXT_ACTIONS[a.status].map((act) => (
                        <button
                          key={act.to}
                          className={`btn btn--sm ${act.primary ? 'btn--primary' : 'btn--ghost'}`}
                          disabled={busyId === a.id}
                          onClick={() => move(a, act.to)}
                          aria-label={`${act.label} ${a.patient_name}`}
                        >
                          {act.label}
                        </button>
                      ))}
                    </div>
                  )}
                </li>
              ))}
            </ol>
          )}
        </section>
      </div>

      <aside className="schedule__side">
        <BookingPanel
          date={date}
          doctors={doctors}
          patients={patients}
          onError={(m) => notify(m, 'error')}
          onBooked={(appt) => {
            notify(`Booked ${appt.patient_name} with ${appt.doctor_name} at ${formatTime(appt.scheduled_at)}.`);
            const bookedDay = toISODate(new Date(appt.scheduled_at));
            if (bookedDay !== date) setDate(bookedDay);
            else load();
          }}
        />
        {stats && stats.doctor_load.length > 0 && (
          <section className="panel" aria-labelledby="load-title">
            <h2 id="load-title" className="panel__title">Doctor workload</h2>
            <ul className="load">
              {stats.doctor_load.map((d) => {
                const max = Math.max(...stats.doctor_load.map((x) => x.upcoming), 1);
                return (
                  <li key={d.doctor_id}>
                    <span className="avatar" aria-hidden="true">{initials(d.doctor_name)}</span>
                    <div className="load__who">
                      <span>{d.doctor_name}</span>
                      <small>{d.specialty}</small>
                    </div>
                    <div className="load__bar" aria-hidden="true">
                      <span style={{ inlineSize: `${(d.upcoming / max) * 100}%` }} />
                    </div>
                    <span className="load__n">{d.upcoming}<span className="sr-only"> upcoming</span></span>
                  </li>
                );
              })}
            </ul>
          </section>
        )}
      </aside>
    </div>
  );
}
