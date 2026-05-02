import { Link } from 'react-router-dom';
import Navbar from '../components/shared/Navbar';
import { ArrowLeft, FlaskConical, FileText, CheckCircle2, AlertTriangle, Clock, ChevronRight } from 'lucide-react';

const MOCK_LAB_RESULTS = [
  {
    id: 'LAB-901',
    patientName: 'Ravi Kumar',
    patientId: 'P-1001',
    testName: 'Complete Blood Count (CBC)',
    date: '2026-05-01',
    status: 'Flagged',
    priority: 'High',
    summary: 'Hemoglobin levels slightly below normal range (11.2 g/dL).'
  },
  {
    id: 'LAB-905',
    patientName: 'Priya Mehra',
    patientId: 'P-1005',
    testName: 'Lipid Profile',
    date: '2026-04-30',
    status: 'Normal',
    priority: 'Routine',
    summary: 'All values within optimal clinical ranges.'
  },
  {
    id: 'LAB-908',
    patientName: 'Vikram Singh',
    patientId: 'P-1012',
    testName: 'HbA1c (Diabetes)',
    date: '2026-05-02',
    status: 'Critical',
    priority: 'Urgent',
    summary: 'HbA1c: 8.4%. Immediate adjustment of insulin dosage recommended.'
  }
];

export default function LabResultsPage() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg-main)' }}>
      <Navbar />
      
      <main className="container" style={{ padding: '3rem 2rem' }}>
        <div className="animate-fade-in" style={{ marginBottom: '3rem' }}>
          <Link to="/doctor/dashboard" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-text-muted)', textDecoration: 'none', marginBottom: '1.5rem', fontWeight: '500', fontSize: '0.9375rem' }}>
            <ArrowLeft size={16} />
            Back to Dashboard
          </Link>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <div>
              <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>Lab Review</h1>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '1.125rem' }}>Review pending diagnostic results and flag critical findings.</p>
            </div>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--color-brand-danger)' }}>3</div>
                <div style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>Pending</div>
              </div>
            </div>
          </div>
        </div>

        <div className="animate-fade-in stagger-1">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {MOCK_LAB_RESULTS.map((lab, index) => (
              <div 
                key={lab.id} 
                className="glass-card card-hover"
                style={{ padding: '1.5rem', display: 'grid', gridTemplateColumns: 'auto 1fr auto', gap: '2rem', alignItems: 'center' }}
              >
                <div style={{ 
                  width: '3.5rem', height: '3.5rem', borderRadius: '1rem', 
                  backgroundColor: lab.status === 'Critical' ? 'var(--color-crit-bg)' : (lab.status === 'Flagged' ? 'var(--color-high-bg)' : 'var(--color-low-bg)'),
                  color: lab.status === 'Critical' ? 'var(--color-crit-red)' : (lab.status === 'Flagged' ? 'var(--color-high-orange)' : 'var(--color-low-green)'),
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  {lab.status === 'Critical' ? <AlertTriangle size={24} /> : (lab.status === 'Flagged' ? <Clock size={24} /> : <CheckCircle2 size={24} />)}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 2fr', gap: '2rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.125rem', marginBottom: '0.25rem' }}>{lab.testName}</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
                      <span style={{ fontWeight: '600', color: 'var(--color-text-title)' }}>{lab.patientName}</span>
                      <span style={{ color: 'var(--color-text-muted)' }}>({lab.patientId})</span>
                    </div>
                  </div>
                  <div>
                    <p style={{ fontSize: '0.875rem', color: 'var(--color-text-body)', lineHeight: 1.4 }}>{lab.summary}</p>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <FileText size={12} /> {lab.id}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <Clock size={12} /> {lab.date}
                      </span>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ 
                      fontSize: '0.6875rem', fontWeight: '800', padding: '0.25rem 0.625rem', borderRadius: '0.375rem',
                      backgroundColor: lab.status === 'Critical' ? 'var(--color-crit-bg)' : (lab.status === 'Flagged' ? 'var(--color-high-bg)' : 'var(--color-low-bg)'),
                      color: lab.status === 'Critical' ? 'var(--color-crit-red)' : (lab.status === 'Flagged' ? 'var(--color-high-orange)' : 'var(--color-low-green)'),
                      textTransform: 'uppercase', letterSpacing: '0.05em'
                    }}>
                      {lab.status}
                    </span>
                  </div>
                  <button className="btn-premium btn-premium-ghost" style={{ padding: '0.5rem' }}>
                    <ChevronRight size={20} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
