import { STATUS_LABEL } from '../format';

export default function StatusPill({ status }) {
  return (
    <span className={`pill pill--${status.toLowerCase()}`}>
      <span className="pill__dot" aria-hidden="true" />
      {STATUS_LABEL[status]}
    </span>
  );
}
