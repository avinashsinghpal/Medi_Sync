import { useNavigate } from 'react-router-dom';
import { usePriorityQueue } from '../../hooks/useDashboard';
import PriorityBadge from '../shared/PriorityBadge';
import LoadingSpinner from '../shared/LoadingSpinner';
import { PRIORITY_CONFIG } from '../../utils/priorityHelpers';
import { Play } from 'lucide-react';

export default function PriorityQueue({ doctorId, date }) {
  const navigate = useNavigate();
  const { data: queue, isLoading, isError } = usePriorityQueue(doctorId, date);

  if (isLoading) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', display: 'flex', justifyContent: 'center' }}>
        <LoadingSpinner />
      </div>
    );
  }

  if (isError || !queue) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', color: '#ef4444' }}>
        Failed to load appointment queue.
      </div>
    );
  }

  // Ensure CRITICAL items are displayed first
  const sortedQueue = [...queue].sort((a, b) => {
    const priorityWeights = { critical: 0, moderate: 1, routine: 2 };
    const weightA = priorityWeights[a.priority?.toLowerCase()] ?? 3;
    const weightB = priorityWeights[b.priority?.toLowerCase()] ?? 3;
    
    if (weightA !== weightB) return weightA - weightB;
    // Secondary sort by scheduled time if priorities match
    return a.scheduledTime.localeCompare(b.scheduledTime);
  });

  return (
    <div className="glass-panel" style={{ overflow: 'hidden' }}>
      <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #e2e8f0', backgroundColor: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: '1.125rem', margin: 0, color: '#0f172a' }}>Today's Queue</h3>
        <span style={{ fontSize: '0.875rem', color: '#64748b' }}>{sortedQueue.length} Appointments</span>
      </div>
      
      {sortedQueue.length === 0 ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>
          No appointments scheduled for today.
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ backgroundColor: '#f1f5f9', color: '#64748b' }}>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '600' }}>#</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '600' }}>Patient</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '600' }}>Age</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '600' }}>Priority</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '600' }}>Time</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '600' }}>Duration</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: '600', textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {sortedQueue.map((item, index) => {
                const isCritical = item.priority?.toLowerCase() === 'critical';
                const rowBgColor = PRIORITY_CONFIG[item.priority?.toLowerCase()]?.bg || '#ffffff';
                
                return (
                  <tr 
                    key={item.id} 
                    style={{ 
                      backgroundColor: isCritical ? '#fef2f2' : rowBgColor, 
                      borderBottom: '1px solid #e2e8f0',
                      transition: 'background-color 0.2s'
                    }}
                  >
                    <td style={{ padding: '1rem', color: '#64748b', fontWeight: '500' }}>{index + 1}</td>
                    <td style={{ padding: '1rem', fontWeight: '600', color: '#0f172a' }}>{item.patientName}</td>
                    <td style={{ padding: '1rem', color: '#475569' }}>{item.age}</td>
                    <td style={{ padding: '1rem' }}><PriorityBadge priority={item.priority} /></td>
                    <td style={{ padding: '1rem', color: '#475569' }}>{item.scheduledTime}</td>
                    <td style={{ padding: '1rem', color: '#475569' }}>{item.estimatedDuration}</td>
                    <td style={{ padding: '1rem', textAlign: 'right' }}>
                      {item.status === 'CONFIRMED' && (
                        <button
                          onClick={() => navigate(`/doctor/consultation/${item.id}`)}
                          style={{
                            display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
                            padding: '0.375rem 0.75rem', backgroundColor: '#0ea5e9', color: 'white',
                            borderRadius: '0.375rem', fontSize: '0.75rem', fontWeight: '600', cursor: 'pointer',
                            border: 'none', transition: 'background-color 0.2s'
                          }}
                          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#0284c7'}
                          onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#0ea5e9'}
                        >
                          <Play size={12} fill="currentColor" /> Start
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
