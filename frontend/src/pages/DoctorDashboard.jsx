import { useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/shared/Navbar';
import DashboardStats from '../components/doctor/DashboardStats';
import PriorityQueue from '../components/doctor/PriorityQueue';
import PatientSummaryCard from '../components/doctor/PatientSummaryCard';
import { useAuthStore } from '../store/authStore';
import { usePriorityQueue } from '../hooks/useDashboard';
import { Calendar, Users, FlaskConical, ChevronRight } from 'lucide-react';

export default function DoctorDashboard() {
  const { user } = useAuthStore();
  const d = new Date();
  const initialDate = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const [selectedDate, setSelectedDate] = useState(initialDate);
  
  const { data: queue = [] } = usePriorityQueue(user?.id, selectedDate);
  const nextPatientId = queue.length > 0 ? queue[0].patientId : null;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--color-bg-main)' }}>
      <Navbar />
      
      <main className="container" style={{ flex: 1, padding: '2.5rem 2rem' }}>
        <div className="animate-fade-in" style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h1 style={{ fontSize: '2.25rem', marginBottom: '0.25rem' }}>Good Morning, Dr. {user?.name?.split(' ')[0] || 'Doctor'}</h1>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '1.0625rem' }}>You have {queue.length} patients scheduled for today.</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', backgroundColor: 'white', padding: '0.5rem 1rem', borderRadius: 'var(--radius-button)', boxShadow: 'var(--shadow-sm)', border: '1px solid var(--color-border-medium)' }}>
            <Calendar size={18} color="var(--color-brand-accent)" />
            <input 
              type="date" 
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              style={{
                padding: '0.25rem',
                border: 'none',
                fontSize: '0.9375rem',
                fontWeight: '600',
                backgroundColor: 'transparent',
                color: 'var(--color-brand-primary)',
                cursor: 'pointer',
                width: 'auto'
              }}
            />
          </div>
        </div>

        <div className="animate-fade-in stagger-1">
          <DashboardStats doctorId={user?.id} date={selectedDate} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '2.5rem', marginTop: '1.5rem' }}>
          {/* Main Queue Column */}
          <div className="animate-fade-in stagger-2" style={{ minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
              <h2 style={{ fontSize: '1.375rem' }}>Live Priority Queue</h2>
              <span style={{ fontSize: '0.8125rem', color: 'var(--color-brand-accent)', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Real-time updates</span>
            </div>
            <PriorityQueue doctorId={user?.id} date={selectedDate} />
          </div>
          
          {/* Sidebar / Quick Look */}
          <div className="animate-fade-in stagger-3">
            <h3 style={{ fontSize: '1.25rem', marginBottom: '1.25rem' }}>Next Patient</h3>
            {nextPatientId ? (
              <PatientSummaryCard patientId={nextPatientId} />
            ) : (
              <div className="glass-card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                <Users size={32} style={{ margin: '0 auto 1rem', opacity: 0.2 }} />
                <p>No patients in queue for this time.</p>
              </div>
            )}
            
            <div className="glass-card" style={{ marginTop: '2rem', padding: '1.5rem', border: '1px solid var(--color-border-subtle)' }}>
              <h4 style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.075em', fontWeight: '700' }}>Management Console</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <Link to="/doctor/patients" className="btn-premium btn-premium-secondary" style={{ justifyContent: 'space-between', width: '100%' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <Users size={18} />
                    <span>Patient Directory</span>
                  </div>
                  <ChevronRight size={16} opacity={0.5} />
                </Link>
                <Link to="/doctor/lab-results" className="btn-premium btn-premium-secondary" style={{ justifyContent: 'space-between', width: '100%' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <FlaskConical size={18} />
                    <span>Lab Review <span style={{ backgroundColor: 'var(--color-brand-danger)', color: 'white', padding: '0.125rem 0.375rem', borderRadius: '0.25rem', fontSize: '0.625rem', marginLeft: '0.25rem' }}>3</span></span>
                  </div>
                  <ChevronRight size={16} opacity={0.5} />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
