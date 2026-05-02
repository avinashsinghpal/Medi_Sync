import { useNavigate } from 'react-router-dom';
import Navbar from '../components/shared/Navbar';
import PriorityBadge from '../components/shared/PriorityBadge';
import { useAuthStore } from '../store/authStore';
import { Calendar, Plus, Clock, FileText } from 'lucide-react';

export default function PatientDashboard() {
  const navigate = useNavigate();
  const { user } = useAuthStore();

  // Mocking patient appointments
  const upcomingAppointments = [
    { id: 'app-1', date: 'Oct 24, 2023', time: '10:00 AM', doctor: 'Dr. Sarah Jenkins', priority: 'routine', status: 'CONFIRMED' }
  ];

  const pastAppointments = [
    { id: 'app-old-1', date: 'Sep 12, 2023', time: '02:30 PM', doctor: 'Dr. Michael Chen', priority: 'moderate', status: 'COMPLETED' }
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f8fafc' }}>
      <Navbar />
      
      <main className="container" style={{ flex: 1, padding: '2rem 1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: '1.875rem', marginBottom: '0.5rem', color: '#0f172a' }}>Hello, {user?.name?.split(' ')[0] || 'Patient'}</h1>
            <p style={{ color: '#64748b', margin: 0 }}>Manage your health and appointments.</p>
          </div>
          <button 
            onClick={() => navigate('/patient/book')}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
              padding: '0.75rem 1.5rem', backgroundColor: '#0ea5e9', color: 'white',
              border: 'none', borderRadius: '0.5rem', fontWeight: '600', cursor: 'pointer',
              transition: 'background-color 0.2s', boxShadow: '0 4px 6px -1px rgba(14, 165, 233, 0.2)'
            }}
            onMouseOver={e => e.currentTarget.style.backgroundColor = '#0284c7'}
            onMouseOut={e => e.currentTarget.style.backgroundColor = '#0ea5e9'}
          >
            <Plus size={18} /> Book Appointment
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem' }}>
          
          {/* Upcoming Appointments */}
          <div>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Clock size={20} color="#0ea5e9" /> Upcoming
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {upcomingAppointments.length === 0 ? (
                <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>
                  No upcoming appointments.
                </div>
              ) : upcomingAppointments.map(app => (
                <div key={app.id} className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid #0ea5e9' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                    <div>
                      <h3 style={{ margin: '0 0 0.25rem 0', fontSize: '1.125rem' }}>{app.date} at {app.time}</h3>
                      <p style={{ margin: 0, color: '#64748b' }}>with {app.doctor}</p>
                    </div>
                    <PriorityBadge priority={app.priority} />
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <span style={{ backgroundColor: '#e2e8f0', padding: '0.25rem 0.5rem', borderRadius: '0.25rem', fontSize: '0.75rem', fontWeight: '600', color: '#475569' }}>
                      {app.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Past Appointments */}
          <div>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileText size={20} color="#64748b" /> History
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {pastAppointments.length === 0 ? (
                <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>
                  No past appointments.
                </div>
              ) : pastAppointments.map(app => (
                <div key={app.id} className="glass-panel" style={{ padding: '1.5rem', opacity: 0.8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                    <div>
                      <h3 style={{ margin: '0 0 0.25rem 0', fontSize: '1.125rem' }}>{app.date}</h3>
                      <p style={{ margin: 0, color: '#64748b' }}>with {app.doctor}</p>
                    </div>
                  </div>
                  <button style={{ 
                    padding: '0.5rem 1rem', backgroundColor: '#f1f5f9', border: 'none', 
                    borderRadius: '0.375rem', fontSize: '0.875rem', fontWeight: '500', 
                    color: '#0f172a', cursor: 'pointer', width: '100%' 
                  }}>
                    View Summary
                  </button>
                </div>
              ))}
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
