import { PRIORITY_CONFIG } from '../../utils/priorityHelpers';

export default function PriorityBadge({ priority = 'routine' }) {
  const config = PRIORITY_CONFIG[priority?.toLowerCase()] || PRIORITY_CONFIG.routine;

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.375rem',
        padding: '0.25rem 0.625rem',
        borderRadius: '9999px',
        backgroundColor: config.bg,
        color: config.color,
        fontSize: '0.75rem',
        fontWeight: '600',
        textTransform: 'uppercase',
        letterSpacing: '0.025em',
        boxShadow: `0 0 0 1px ${config.color}20 inset` // Subtle border
      }}
    >
      <span aria-hidden="true" style={{ fontSize: '0.875rem' }}>{config.icon}</span>
      {config.label}
    </span>
  );
}
