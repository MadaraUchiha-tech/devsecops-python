export const STATUS_LABEL = {
  SCHEDULED: 'Scheduled',
  CHECKED_IN: 'Checked in',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
  NO_SHOW: 'No-show',
};

export const toISODate = (d) => {
  const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
};

export const formatTime = (iso) =>
  new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

export const formatDay = (isoDate) =>
  new Date(`${isoDate}T12:00:00`).toLocaleDateString([], { weekday: 'long', day: 'numeric', month: 'long' });

export const shiftDate = (isoDate, days) => {
  const d = new Date(`${isoDate}T12:00:00`);
  d.setDate(d.getDate() + days);
  return toISODate(d);
};

export const initials = (name) =>
  name
    .replace(/^Dr\.?\s+/i, '')
    .split(/\s+/)
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();
