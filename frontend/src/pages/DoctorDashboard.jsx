import Navbar from '../components/shared/Navbar';
import DashboardStats from '../components/doctor/DashboardStats';
import PriorityQueue from '../components/doctor/PriorityQueue';
import PatientSummaryCard from '../components/doctor/PatientSummaryCard';
import { useAuthStore } from '../store/authStore';
import { usePriorityQueue } from '../hooks/useDashboard';

export default function DoctorDashboard() {
  const { user } = useAuthStore();
  const today = new Date().toISOString().split('T')[0];
  const { data: queue = [] } = usePriorityQueue(user?.id, today);
  const nextPatientId = queue.length > 0 ? queue[0].patientId : null;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      
      <main className="container" style={{ flex: 1, padding: '2rem 1.5rem' }}>
        <div style={{ marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '1.875rem', marginBottom: '0.5rem' }}>Welcome, Dr. {user?.name?.split(' ')[0] || 'Doctor'}</h1>
          <p style={{ color: '#64748b', margin: 0 }}>Here's your upcoming schedule.</p>
        </div>

        <DashboardStats doctorId={user?.id} date={today} />

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem' }}>
          {/* Main Queue Column */}
          <div style={{ minWidth: 0 }}>
            <PriorityQueue doctorId={user?.id} date={today} />
          </div>
          
          {/* Sidebar / Quick Look */}
          <div>
            <h3 style={{ fontSize: '1.125rem', marginBottom: '1rem', color: '#0f172a' }}>Next Patient</h3>
            {nextPatientId ? (
              <PatientSummaryCard patientId={nextPatientId} />
            ) : (
              <div className="glass-panel" style={{ padding: '1.25rem', color: '#64748b' }}>
                No patients in queue.
              </div>
            )}
            
            <div className="glass-panel" style={{ marginTop: '1.5rem', padding: '1.25rem' }}>
              <h4 style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Quick Actions</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <button style={{ padding: '0.75rem', backgroundColor: '#f1f5f9', border: 'none', borderRadius: '0.375rem', textAlign: 'left', fontWeight: '500', color: '#334155', cursor: 'pointer' }}>View All Patients</button>
                <button style={{ padding: '0.75rem', backgroundColor: '#f1f5f9', border: 'none', borderRadius: '0.375rem', textAlign: 'left', fontWeight: '500', color: '#334155', cursor: 'pointer' }}>Review Lab Results (3)</button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
