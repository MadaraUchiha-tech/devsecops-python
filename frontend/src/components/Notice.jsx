import { AlertTriangle, CheckCircle2, X } from 'lucide-react';

export default function Notice({ notice, onDismiss }) {
  if (!notice) return null;
  const Icon = notice.tone === 'error' ? AlertTriangle : CheckCircle2;
  return (
    <div className={`notice notice--${notice.tone}`} role={notice.tone === 'error' ? 'alert' : 'status'}>
      <Icon size={18} aria-hidden="true" />
      <span>{notice.message}</span>
      <button className="icon-btn" onClick={onDismiss} aria-label="Dismiss message">
        <X size={16} />
      </button>
    </div>
  );
}
