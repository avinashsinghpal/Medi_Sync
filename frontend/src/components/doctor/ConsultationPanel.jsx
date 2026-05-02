import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PatientSummaryCard from './PatientSummaryCard';
import SpeechRecorder from './SpeechRecorder';
import { useConsultationStore } from '../../store/consultationStore';
import { useProcessConsultation, useCompleteConsultation } from '../../hooks/useConsultation';
import { FileText, Save, CheckCircle, Activity, Loader2 } from 'lucide-react';

export default function ConsultationPanel({ appointmentId, patientId }) {
  const navigate = useNavigate();
  
  const { 
    transcript, 
    setTranscript, 
    extractedData, 
    setExtractedData, 
    consultationSummary, 
    setConsultationSummary,
    clearConsultation 
  } = useConsultationStore();

  const { mutate: processConsultation, isPending: isProcessing } = useProcessConsultation();
  const { mutate: completeConsultation, isPending: isCompleting } = useCompleteConsultation();

  // Clean up on mount/unmount
  useEffect(() => {
    return () => clearConsultation();
  }, [clearConsultation]);

  const handleGenerateSummary = () => {
    if (!transcript.trim()) return;
    
    processConsultation({ appointmentId, transcript }, {
      onSuccess: (data) => {
        setExtractedData(data.entities);
        setConsultationSummary(data.summary);
      }
    });
  };

  const handleSaveComplete = () => {
    completeConsultation({ appointmentId, summary: consultationSummary || transcript }, {
      onSuccess: () => {
        clearConsultation();
        navigate('/doctor/dashboard');
      }
    });
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr 350px', gap: '1.5rem', height: 'calc(100vh - 6rem)' }}>
      
      {/* Left Column: Patient Context */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h2 style={{ fontSize: '1.125rem', color: '#0f172a', margin: '0 0 0.5rem 0' }}>Patient Context</h2>
        <PatientSummaryCard patientId={patientId} compact={false} />
      </div>

      {/* Center Column: Recording & Transcript */}
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <SpeechRecorder onTranscript={setTranscript} />
        
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
          <button
            onClick={handleGenerateSummary}
            disabled={!transcript || isProcessing}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
              padding: '0.75rem 1.5rem', backgroundColor: '#f1f5f9', color: '#0f172a',
              border: '1px solid #e2e8f0', borderRadius: '0.5rem', fontWeight: '600', cursor: (!transcript || isProcessing) ? 'not-allowed' : 'pointer',
              opacity: (!transcript || isProcessing) ? 0.6 : 1,
              transition: 'all 0.2s'
            }}
          >
            {isProcessing ? <Loader2 size={18} className="spin" /> : <FileText size={18} />}
            Generate NLP Summary
          </button>
        </div>
      </div>

      {/* Right Column: Extracted Data & Actions */}
      <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', padding: '1.5rem', overflowY: 'auto' }}>
        <h2 style={{ fontSize: '1.125rem', color: '#0f172a', margin: '0 0 1.5rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity size={20} color="#0ea5e9" /> AI Extraction Results
        </h2>

        {!extractedData && !consultationSummary ? (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', color: '#94a3b8', textAlign: 'center' }}>
            <FileText size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
            <p>Generate a summary to view extracted entities and structured notes.</p>
          </div>
        ) : (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            
            {extractedData && (
              <div>
                <h3 style={{ fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748b', marginBottom: '0.75rem' }}>Extracted Entities</h3>
                
                {Object.entries(extractedData).map(([category, items]) => (
                  <div key={category} style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.75rem', color: '#475569', fontWeight: '600', marginBottom: '0.25rem', textTransform: 'capitalize' }}>{category}</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
                      {items.map((item, i) => (
                        <span key={i} style={{ backgroundColor: '#e0f2fe', color: '#0284c7', padding: '0.25rem 0.5rem', borderRadius: '0.25rem', fontSize: '0.75rem', fontWeight: '500' }}>
                          {item}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {consultationSummary && (
              <div>
                <h3 style={{ fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748b', marginBottom: '0.75rem' }}>Structured Summary</h3>
                <div style={{ backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '0.5rem', padding: '1rem', fontSize: '0.875rem', color: '#334155', lineHeight: '1.6' }}>
                  {consultationSummary}
                </div>
              </div>
            )}
          </div>
        )}

        <div style={{ marginTop: 'auto', paddingTop: '1.5rem', borderTop: '1px solid #e2e8f0' }}>
          <button
            onClick={handleSaveComplete}
            disabled={isCompleting || (!consultationSummary && !transcript)}
            style={{
              width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
              padding: '0.875rem', backgroundColor: '#10b981', color: 'white',
              border: 'none', borderRadius: '0.5rem', fontWeight: '600', cursor: (isCompleting || (!consultationSummary && !transcript)) ? 'not-allowed' : 'pointer',
              opacity: (isCompleting || (!consultationSummary && !transcript)) ? 0.6 : 1,
              transition: 'background-color 0.2s'
            }}
            onMouseOver={e => !isCompleting && (e.currentTarget.style.backgroundColor = '#059669')}
            onMouseOut={e => !isCompleting && (e.currentTarget.style.backgroundColor = '#10b981')}
          >
            {isCompleting ? <Loader2 size={18} className="spin" /> : <Save size={18} />}
            Save & Complete
          </button>
        </div>
        <style>{`.spin { animation: spin 1s linear infinite; }`}</style>
      </div>
    </div>
  );
}
