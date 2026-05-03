import { useDashboardStats } from '../../hooks/useDashboard';
import LoadingSpinner from '../shared/LoadingSpinner';
import { Users, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function DashboardStats({ doctorId, date }) {
  const { data: stats, isLoading, isError } = useDashboardStats(doctorId, date);

  if (isLoading) {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {[1, 2, 3].map(i => (
          <div key={i} className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'center', minHeight: '120px', alignItems: 'center' }}>
            <LoadingSpinner size="sm" />
          </div>
        ))}
      </div>
    );
  }

  if (isError || !stats) {
    return (
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem', color: '#ef4444' }}>
        Failed to load dashboard statistics.
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Appointments',
      value: stats.total,
      icon: <Users size={24} color="#0ea5e9" />,
      bgColor: '#e0f2fe',
      textColor: '#0f172a'
    },
    {
      title: 'Critical Patients',
      value: stats.critical,
      icon: <AlertCircle size={24} color="#ef4444" />,
      bgColor: '#fef2f2',
      textColor: '#ef4444'
    },
    {
      title: 'Completed Today',
      value: stats.completed,
      icon: <CheckCircle2 size={24} color="#10b981" />,
      bgColor: '#f0fdf4',
      textColor: '#10b981'
    }
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
      {statCards.map((card, idx) => (
        <div key={idx} className="glass-card card-hover" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.25rem', cursor: 'default' }}>
          <div style={{ backgroundColor: card.bgColor, padding: '1rem', borderRadius: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {card.icon}
          </div>
          <div>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#64748b', fontWeight: '500' }}>{card.title}</p>
            <h3 style={{ margin: 0, fontSize: '1.875rem', color: card.textColor, fontWeight: '700' }}>{card.value}</h3>
          </div>
        </div>
      ))}
    </div>
  );
}
