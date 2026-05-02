import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/shared/Navbar';
import ConsultationPanel from '../components/doctor/ConsultationPanel';
import { ArrowLeft } from 'lucide-react';
import { useAppointment } from '../hooks/useAppointments';

export default function ConsultationPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: appointment } = useAppointment(id);
  const patientId = appointment?.patient_id;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f1f5f9' }}>
      <Navbar />
      
      <main style={{ flex: 1, padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center' }}>
          <button 
            onClick={() => navigate('/doctor/dashboard')}
            style={{ 
              display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
              color: '#64748b', background: 'transparent', border: 'none', 
              fontSize: '0.875rem', fontWeight: '500', cursor: 'pointer',
              padding: '0.5rem', marginLeft: '-0.5rem', borderRadius: '0.375rem'
            }}
            onMouseOver={e => e.currentTarget.style.backgroundColor = '#e2e8f0'}
            onMouseOut={e => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            <ArrowLeft size={16} /> Back to Dashboard
          </button>
          <div style={{ marginLeft: '1rem', paddingLeft: '1rem', borderLeft: '1px solid #cbd5e1' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Appointment ID: </span>
            <span style={{ color: '#475569', fontSize: '0.875rem', fontWeight: '600', fontFamily: 'monospace' }}>{id}</span>
          </div>
        </div>

        <ConsultationPanel appointmentId={id} patientId={patientId} />
      </main>
    </div>
  );
}
