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
        <div className="animate-fade-in" style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '2.25rem', marginBottom: '0.25rem', color: 'var(--color-text-title)' }}>Good Morning, Dr. {user?.name?.split(' ')[0] || 'Doctor'}</h1>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '1.0625rem' }}>You have <strong style={{ color: 'var(--color-brand-primary)' }}>{queue.length}</strong> patients scheduled for today.</p>
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

        <div className="dashboard-grid">
          {/* Main Queue Column */}
          <div className="animate-fade-in stagger-2" style={{ minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <h2 style={{ fontSize: '1.375rem', margin: 0 }}>Live Priority Queue</h2>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-brand-accent)', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em', backgroundColor: 'var(--color-med-bg)', padding: '0.25rem 0.75rem', borderRadius: '1rem' }}>Real-time updates</span>
            </div>
            <PriorityQueue doctorId={user?.id} date={selectedDate} />
          </div>
          
          {/* Sidebar / Quick Look */}
          <div className="animate-fade-in stagger-3">
            <h3 style={{ fontSize: '1.25rem', marginBottom: '1.25rem' }}>Next Patient</h3>
            {nextPatientId ? (
              <PatientSummaryCard patientId={nextPatientId} />
            ) : (
              <div className="glass-card" style={{ padding: '3rem 2rem', textAlign: 'center', color: 'var(--color-text-muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '200px' }}>
                <div style={{ backgroundColor: 'var(--color-border-subtle)', padding: '1rem', borderRadius: '50%', marginBottom: '1rem' }}>
                  <Users size={28} style={{ color: 'var(--color-text-muted)', opacity: 0.6 }} />
                </div>
                <p style={{ fontWeight: 500 }}>No patients in queue</p>
                <p style={{ fontSize: '0.875rem', opacity: 0.7, marginTop: '0.25rem' }}>Check back later or view directory.</p>
              </div>
            )}
            
            <div className="glass-card" style={{ marginTop: '2rem', padding: '1.5rem' }}>
              <h4 style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '1.25rem', textTransform: 'uppercase', letterSpacing: '0.075em', fontWeight: '700' }}>Management Console</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <Link to="/doctor/patients" className="menu-item-hover" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', padding: '0.875rem 1rem', borderRadius: 'var(--radius-button)', textDecoration: 'none', color: 'var(--color-text-title)', fontWeight: 500, backgroundColor: 'var(--color-bg-main)', border: '1px solid var(--color-border-subtle)', transition: 'all 0.2s' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ color: 'var(--color-brand-accent)' }}><Users size={18} /></div>
                    <span>Patient Directory</span>
                  </div>
                  <ChevronRight size={16} color="var(--color-text-muted)" />
                </Link>
                <Link to="/doctor/lab-results" className="menu-item-hover" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', padding: '0.875rem 1rem', borderRadius: 'var(--radius-button)', textDecoration: 'none', color: 'var(--color-text-title)', fontWeight: 500, backgroundColor: 'var(--color-bg-main)', border: '1px solid var(--color-border-subtle)', transition: 'all 0.2s' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ color: 'var(--color-brand-accent)' }}><FlaskConical size={18} /></div>
                    <span>Lab Review</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ backgroundColor: 'var(--color-crit-red)', color: 'white', padding: '0.125rem 0.5rem', borderRadius: '1rem', fontSize: '0.75rem', fontWeight: 700 }}>3</span>
                    <ChevronRight size={16} color="var(--color-text-muted)" />
                  </div>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
