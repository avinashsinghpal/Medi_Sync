import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/shared/Navbar';
import PriorityBadge from '../components/shared/PriorityBadge';
import { useAuthStore } from '../store/authStore';
import { Calendar, Plus, Clock, FileText, ChevronDown, ChevronUp, Activity, ClipboardList } from 'lucide-react';
import { usePatientAppointments } from '../hooks/useAppointments';

export default function PatientDashboard() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { data: appointments = [] } = usePatientAppointments(user?.id);
  const norm = (s) => (s || '').toLowerCase();
  const upcomingAppointments = appointments.filter((a) => ['pending', 'confirmed', 'in_session'].includes(norm(a.status)));
  const pastAppointments = appointments.filter((a) => ['completed', 'cancelled', 'no_show'].includes(norm(a.status)));

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--color-bg-main)' }}>
      <Navbar />
      
      <main className="container" style={{ flex: 1, padding: '3rem 2rem' }}>
        <div className="animate-fade-in" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '3rem' }}>
          <div>
            <h1 style={{ fontSize: '2.5rem', marginBottom: '0.25rem' }}>Hello, {user?.name?.split(' ')[0] || 'Patient'}</h1>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '1.125rem' }}>Manage your health journey and upcoming clinical visits.</p>
          </div>
          <button 
            onClick={() => navigate('/patient/book')}
            className="btn-premium btn-premium-primary"
            style={{ padding: '1rem 2rem', fontSize: '1rem' }}
          >
            <Plus size={20} /> Book New Consultation
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '3rem' }}>
          
          {/* Upcoming Appointments */}
          <div className="animate-fade-in stagger-1">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--color-med-bg)', color: 'var(--color-med-blue)', borderRadius: '0.75rem' }}>
                <Activity size={20} />
              </div>
              <h2 style={{ fontSize: '1.375rem' }}>Upcoming Visits</h2>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {upcomingAppointments.length === 0 ? (
                <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--color-text-muted)', borderStyle: 'dashed' }}>
                  <Calendar size={32} style={{ margin: '0 auto 1rem', opacity: 0.2 }} />
                  <p>You have no scheduled visits at the moment.</p>
                </div>
              ) : upcomingAppointments.map(app => (
                <div key={app.appointment_id} className="glass-card card-hover" style={{ padding: '1.75rem', borderLeft: '5px solid var(--color-brand-accent)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
                    <div>
                      <h3 style={{ margin: '0 0 0.375rem 0', fontSize: '1.1875rem' }}>{new Date(app.scheduled_at).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</h3>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-text-muted)', fontSize: '0.9375rem' }}>
                        <Clock size={14} />
                        <span>{new Date(app.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                    </div>
                    <PriorityBadge priority={app.priority_level} />
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ 
                        backgroundColor: 'var(--color-border-subtle)', color: 'var(--color-text-muted)', 
                        padding: '0.375rem 0.75rem', borderRadius: 'var(--radius-button)', 
                        fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.025em'
                      }}>
                        {app.status.replace('_', ' ')}
                      </span>
                    </div>
                    <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>ID: {app.appointment_id.slice(-6)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Past Appointments */}
          <div className="animate-fade-in stagger-2">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--color-border-subtle)', color: 'var(--color-text-muted)', borderRadius: '0.75rem' }}>
                <ClipboardList size={20} />
              </div>
              <h2 style={{ fontSize: '1.375rem' }}>Medical History</h2>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {pastAppointments.length === 0 ? (
                <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--color-text-muted)', borderStyle: 'dashed' }}>
                  <FileText size={32} style={{ margin: '0 auto 1rem', opacity: 0.2 }} />
                  <p>Your medical history will appear here after your first visit.</p>
                </div>
              ) : pastAppointments.map(app => (
                <AppointmentHistoryCard key={app.appointment_id} app={app} />
              ))}
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

function AppointmentHistoryCard({ app }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`glass-card ${isExpanded ? '' : 'card-hover'}`} style={{ padding: '1.5rem', transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
        <div>
          <h3 style={{ margin: '0 0 0.375rem 0', fontSize: '1.125rem' }}>{new Date(app.scheduled_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</h3>
          <p style={{ margin: 0, color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>Consultation with Dr. {app.doctor_id || 'Staff'}</p>
        </div>
        <span style={{ 
          backgroundColor: 'var(--color-border-subtle)', color: 'var(--color-text-muted)', 
          padding: '0.25rem 0.625rem', borderRadius: '0.375rem', 
          fontSize: '0.6875rem', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.05em'
        }}>
          {app.status}
        </span>
      </div>

      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className="btn-premium btn-premium-secondary"
        style={{ width: '100%', padding: '0.625rem' }}
      >
        {isExpanded ? (
          <>Hide Summary <ChevronUp size={16} /></>
        ) : (
          <>View Clinical Summary <ChevronDown size={16} /></>
        )}
      </button>

      {isExpanded && (
        <div className="animate-fade-in" style={{ 
          marginTop: '1.25rem', 
          padding: '1.25rem', 
          backgroundColor: 'var(--color-bg-main)', 
          borderRadius: 'var(--radius-button)', 
          border: '1px solid var(--color-border-subtle)',
          fontSize: '0.9375rem',
          color: 'var(--color-text-body)',
          lineHeight: '1.7',
          whiteSpace: 'pre-wrap',
          boxShadow: 'inset 0 2px 4px 0 rgba(0,0,0,0.02)'
        }}>
          <div style={{ fontWeight: '700', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--color-brand-accent)', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>Doctor's Notes</div>
          {app.notes || "No summary notes provided for this consultation."}
        </div>
      )}
    </div>
  );
}
