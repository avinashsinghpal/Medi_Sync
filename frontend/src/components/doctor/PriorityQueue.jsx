import { useNavigate } from 'react-router-dom';
import { usePriorityQueue } from '../../hooks/useDashboard';
import PriorityBadge from '../shared/PriorityBadge';
import LoadingSpinner from '../shared/LoadingSpinner';
import { PRIORITY_CONFIG } from '../../utils/priorityHelpers';
import { Play, Calendar, CheckCheck, Clock, User } from 'lucide-react';

const PRIORITY_ROW = {
  critical: { bg: '#fffbfb', border: '#fecaca', dot: '#ef4444' },
  moderate: { bg: '#fffdf7', border: '#fde68a', dot: '#f59e0b' },
  routine:  { bg: '#f9fffe', border: '#d1fae5', dot: '#10b981' },
};

function ActionButton({ item, navigate }) {
  const status = String(item.status).toLowerCase();

  if (status === 'pending') {
    return (
      <button
        onClick={async () => {
          try {
            const { default: api } = await import('../../utils/api');
            await api.patch(`/appointments/${item.id}/confirm`);
            window.location.reload();
          } catch (err) { console.error('Confirm failed', err); }
        }}
        style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.3rem',
          padding: '0.375rem 0.875rem',
          background: 'linear-gradient(135deg, #f59e0b, #d97706)',
          color: 'white', borderRadius: '0.5rem', fontSize: '0.75rem',
          fontWeight: '600', cursor: 'pointer', border: 'none',
          boxShadow: '0 2px 4px rgba(217,119,6,0.25)',
        }}
      >
        Confirm
      </button>
    );
  }

  if (status === 'confirmed') {
    return (
      <button
        onClick={async () => {
          try {
            const { default: api } = await import('../../utils/api');
            await api.patch(`/appointments/${item.id}/start`);
            navigate(`/doctor/consultation/${item.id}`);
          } catch (err) { console.error('Failed to start', err); }
        }}
        style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.3rem',
          padding: '0.375rem 0.875rem',
          background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
          color: 'white', borderRadius: '0.5rem', fontSize: '0.75rem',
          fontWeight: '600', cursor: 'pointer', border: 'none',
          boxShadow: '0 2px 4px rgba(2,132,199,0.25)',
        }}
      >
        <Play size={11} fill="currentColor" /> Start
      </button>
    );
  }

  if (status === 'in_session') {
    return (
      <button
        onClick={() => navigate(`/doctor/consultation/${item.id}`)}
        style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.3rem',
          padding: '0.375rem 0.875rem',
          background: 'linear-gradient(135deg, #10b981, #059669)',
          color: 'white', borderRadius: '0.5rem', fontSize: '0.75rem',
          fontWeight: '600', cursor: 'pointer', border: 'none',
          boxShadow: '0 2px 4px rgba(5,150,105,0.25)',
        }}
      >
        <Play size={11} fill="currentColor" /> Resume
      </button>
    );
  }

  if (status === 'completed') {
    return (
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', color: '#10b981', fontSize: '0.75rem', fontWeight: '600' }}>
        <CheckCheck size={14} /> Done
      </span>
    );
  }

  return null;
}

export default function PriorityQueue({ doctorId, date }) {
  const navigate = useNavigate();
  const { data: queue, isLoading, isError } = usePriorityQueue(doctorId, date);

  if (isLoading) {
    return (
      <div className="glass-card" style={{ padding: '2.5rem', display: 'flex', justifyContent: 'center' }}>
        <LoadingSpinner />
      </div>
    );
  }

  if (isError || !queue) {
    return (
      <div className="glass-card" style={{ padding: '2rem', textAlign: 'center', color: '#ef4444' }}>
        Failed to load appointment queue.
      </div>
    );
  }

  const sortedQueue = [...queue].sort((a, b) => {
    const w = { critical: 0, moderate: 1, routine: 2 };
    const wA = w[a.priority?.toLowerCase()] ?? 3;
    const wB = w[b.priority?.toLowerCase()] ?? 3;
    if (wA !== wB) return wA - wB;
    return a.scheduledTime.localeCompare(b.scheduledTime);
  });

  return (
    <div className="glass-card" style={{ overflow: 'hidden' }}>
      {/* Header */}
      <div style={{
        padding: '1.125rem 1.5rem',
        borderBottom: '1px solid var(--color-border-subtle)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        background: 'linear-gradient(135deg, #f8fafc, white)',
      }}>
        <h3 style={{ fontSize: '1rem', margin: 0, color: '#0f172a', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Clock size={16} color="#0ea5e9" /> Upcoming Queue
        </h3>
        <span style={{
          fontSize: '0.75rem', color: '#64748b', fontWeight: '600',
          background: '#f1f5f9', padding: '0.25rem 0.625rem', borderRadius: '999px',
          border: '1px solid var(--color-border-medium)',
        }}>
          {sortedQueue.length} appointment{sortedQueue.length !== 1 ? 's' : ''}
        </span>
      </div>

      {sortedQueue.length === 0 ? (
        <div style={{ padding: '4rem 2rem', textAlign: 'center', color: 'var(--color-text-muted)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{ background: 'linear-gradient(135deg, #f0f9ff, #e0f2fe)', padding: '1.25rem', borderRadius: '50%', marginBottom: '1rem' }}>
            <Calendar size={28} color="#0ea5e9" style={{ opacity: 0.7 }} />
          </div>
          <p style={{ fontWeight: '600', color: '#334155', marginBottom: '0.25rem' }}>Queue is clear</p>
          <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>No upcoming appointments scheduled.</p>
        </div>
      ) : (
        <div>
          {sortedQueue.map((item, index) => {
            const pKey = item.priority?.toLowerCase() || 'routine';
            const row = PRIORITY_ROW[pKey] || PRIORITY_ROW.routine;

            return (
              <div
                key={item.id}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '40px 1fr auto',
                  alignItems: 'center',
                  gap: '1rem',
                  padding: '1rem 1.5rem',
                  backgroundColor: row.bg,
                  borderBottom: '1px solid var(--color-border-subtle)',
                  borderLeft: `3px solid ${row.border}`,
                  transition: 'background-color 0.15s',
                  cursor: 'default',
                }}
                onMouseOver={e => e.currentTarget.style.filter = 'brightness(0.985)'}
                onMouseOut={e => e.currentTarget.style.filter = 'none'}
              >
                {/* Position badge */}
                <div style={{
                  width: '32px', height: '32px', borderRadius: '50%',
                  background: pKey === 'critical' ? 'linear-gradient(135deg, #fecaca, #fca5a5)' :
                              pKey === 'moderate' ? 'linear-gradient(135deg, #fde68a, #fcd34d)' :
                              'linear-gradient(135deg, #bbf7d0, #86efac)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '0.75rem', fontWeight: '700',
                  color: pKey === 'critical' ? '#991b1b' : pKey === 'moderate' ? '#92400e' : '#065f46',
                  flexShrink: 0,
                }}>
                  {index + 1}
                </div>

                {/* Patient info */}
                <div style={{ minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem', flexWrap: 'wrap' }}>
                    <span style={{ fontWeight: '700', color: '#0f172a', fontSize: '0.9375rem' }}>{item.patientName}</span>
                    <PriorityBadge priority={item.priority} />
                    {item.age && (
                      <span style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                        <User size={11} /> {item.age}y
                      </span>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '1.25rem', fontSize: '0.8125rem', color: '#64748b', flexWrap: 'wrap' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Clock size={12} /> {item.scheduledTime}
                    </span>
                    {item.estimatedDuration && (
                      <span>~{item.estimatedDuration}</span>
                    )}
                    {item.symptomsPreview && (
                      <span style={{ color: '#94a3b8', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '200px' }}>
                        {item.symptomsPreview}
                      </span>
                    )}
                  </div>
                </div>

                {/* Action */}
                <div style={{ flexShrink: 0 }}>
                  <ActionButton item={item} navigate={navigate} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
