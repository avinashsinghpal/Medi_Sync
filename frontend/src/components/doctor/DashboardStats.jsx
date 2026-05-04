import { useDashboardStats } from '../../hooks/useDashboard';
import LoadingSpinner from '../shared/LoadingSpinner';
import { Users, AlertCircle, CheckCircle2, Clock } from 'lucide-react';

export default function DashboardStats({ doctorId, date }) {
  const { data: stats, isLoading, isError } = useDashboardStats(doctorId, date);

  if (isLoading) {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
        {[1, 2, 3].map(i => (
          <div key={i} className="stat-card" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'center', minHeight: '110px', alignItems: 'center' }}>
            <LoadingSpinner size="sm" />
          </div>
        ))}
      </div>
    );
  }

  if (isError || !stats) {
    return (
      <div className="stat-card" style={{ padding: '1.5rem', marginBottom: '2rem', color: '#ef4444' }}>
        Failed to load dashboard statistics.
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Appointments',
      value: stats.total,
      subtitle: 'Scheduled today',
      icon: <Users size={22} />,
      iconBg: 'linear-gradient(135deg, #e0f2fe, #bae6fd)',
      iconColor: '#0284c7',
      accent: '#0ea5e9',
      valueColor: '#0f172a',
    },
    {
      title: 'Critical Patients',
      value: stats.critical,
      subtitle: 'Require immediate care',
      icon: <AlertCircle size={22} />,
      iconBg: 'linear-gradient(135deg, #fef2f2, #fecaca)',
      iconColor: '#dc2626',
      accent: '#ef4444',
      valueColor: stats.critical > 0 ? '#dc2626' : '#0f172a',
    },
    {
      title: 'Completed Today',
      value: stats.completed,
      subtitle: `${stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0}% completion rate`,
      icon: <CheckCircle2 size={22} />,
      iconBg: 'linear-gradient(135deg, #f0fdf4, #bbf7d0)',
      iconColor: '#059669',
      accent: '#10b981',
      valueColor: '#059669',
    },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
      {statCards.map((card, idx) => (
        <div
          key={idx}
          className="stat-card"
          style={{ '--card-accent': card.accent, padding: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1.125rem', cursor: 'default' }}
        >
          <div style={{
            background: card.iconBg,
            color: card.iconColor,
            width: '48px', height: '48px',
            borderRadius: '0.875rem',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
            boxShadow: '0 2px 4px rgba(0,0,0,0.06)',
          }}>
            {card.icon}
          </div>
          <div style={{ flex: 1 }}>
            <p style={{ margin: '0 0 0.25rem', fontSize: '0.8125rem', color: '#64748b', fontWeight: '500' }}>{card.title}</p>
            <h3 style={{ margin: '0 0 0.25rem', fontSize: '2rem', color: card.valueColor, fontWeight: '700', lineHeight: 1 }}>
              {card.value}
            </h3>
            <p style={{ margin: 0, fontSize: '0.75rem', color: '#94a3b8', fontWeight: '400' }}>{card.subtitle}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
