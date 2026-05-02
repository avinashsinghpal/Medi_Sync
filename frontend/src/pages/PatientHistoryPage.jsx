import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/shared/Navbar';
import PatientSummaryCard from '../components/doctor/PatientSummaryCard';
import { usePatientHistory } from '../hooks/usePatientData';
import { ArrowLeft, Clock, FileText } from 'lucide-react';
import LoadingSpinner from '../components/shared/LoadingSpinner';

export default function PatientHistoryPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: history, isLoading, isError } = usePatientHistory(id);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f1f5f9' }}>
      <Navbar />
      
      <main style={{ flex: 1, padding: '1.5rem', maxWidth: '1200px', margin: '0 auto', width: '100%', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
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
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '1.5rem' }}>
          
          {/* Left Column: Summary */}
          <div style={{ alignSelf: 'start' }}>
            <PatientSummaryCard patientId={id} compact={false} />
          </div>

          {/* Right Column: Full History List */}
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <h2 style={{ fontSize: '1.25rem', color: '#0f172a', margin: '0 0 1.5rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Clock size={20} color="#0ea5e9" /> Comprehensive Medical History
            </h2>

            {isLoading ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
                <LoadingSpinner />
              </div>
            ) : isError ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#ef4444' }}>
                Failed to load patient history.
              </div>
            ) : !history || history.length === 0 ? (
              <div style={{ padding: '4rem 2rem', textAlign: 'center', color: '#64748b', backgroundColor: '#f8fafc', borderRadius: '0.5rem' }}>
                <FileText size={48} style={{ opacity: 0.2, margin: '0 auto 1rem auto' }} />
                <p>No historical records found for this patient.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {history.map((record, index) => (
                  <div key={record.record_id || index} style={{ 
                    border: '1px solid #e2e8f0', borderRadius: '0.5rem', padding: '1.25rem',
                    backgroundColor: '#ffffff', transition: 'box-shadow 0.2s'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                      <h3 style={{ margin: 0, fontSize: '1rem', color: '#0f172a' }}>{record.title}</h3>
                      <span style={{ fontSize: '0.75rem', color: '#64748b', backgroundColor: '#f1f5f9', padding: '0.25rem 0.5rem', borderRadius: '0.25rem' }}>
                        {new Date(record.recorded_at).toLocaleDateString()}
                      </span>
                    </div>
                    
                    <p style={{ fontSize: '0.875rem', color: '#475569', margin: '0 0 1rem 0', lineHeight: '1.5' }}>
                      {record.content}
                    </p>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                        {record.tags && record.tags.map((tag, i) => (
                          <span key={i} style={{ 
                            fontSize: '0.75rem', color: '#0284c7', backgroundColor: '#e0f2fe',
                            padding: '0.125rem 0.375rem', borderRadius: '0.25rem', fontWeight: '500'
                          }}>
                            {tag}
                          </span>
                        ))}
                      </div>
                      <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        {record.record_type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
