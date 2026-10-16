const BASE = '/api';

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, { method = 'GET', body } = {}) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError('Cannot reach the CareSlot API. Check that the backend is running.', 0);
  }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => `${d.loc?.at(-1)}: ${d.msg}`).join('; ')
      : detail || `Request failed (${res.status})`;
    throw new ApiError(message, res.status);
  }
  return data;
}

const qs = (params) => {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '');
  return entries.length ? `?${new URLSearchParams(entries)}` : '';
};

export const api = {
  appointments: (params = {}) => request(`/appointments${qs(params)}`),
  stats: () => request('/appointments/stats'),
  book: (body) => request('/appointments', { method: 'POST', body }),
  updateAppointment: (id, body) => request(`/appointments/${id}`, { method: 'PUT', body }),
  deleteAppointment: (id) => request(`/appointments/${id}`, { method: 'DELETE' }),
  doctors: (params = {}) => request(`/doctors${qs(params)}`),
  createDoctor: (body) => request('/doctors', { method: 'POST', body }),
  updateDoctor: (id, body) => request(`/doctors/${id}`, { method: 'PUT', body }),
  patients: (params = {}) => request(`/patients${qs(params)}`),
  createPatient: (body) => request('/patients', { method: 'POST', body }),
  deletePatient: (id) => request(`/patients/${id}`, { method: 'DELETE' }),
};
