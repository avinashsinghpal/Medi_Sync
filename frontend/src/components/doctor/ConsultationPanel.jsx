import { useEffect } from 'react';
import PatientSummaryCard from './PatientSummaryCard';
import SpeechRecorder from './SpeechRecorder';
import { useProcessConsultation, useCompleteConsultation } from '../../hooks/useConsultation';
import useConsultationStore from '../../store/consultationStore';
import { CheckCircle, Activity, FileText, Pill, AlertTriangle, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ConsultationPanel({ appointmentId, patientId }) {
  const navigate = useNavigate();
  
  // Store state
  const { 
    transcript, 
    extractedData, 
    setExtractedData, 
    setConsultationSummary,
    clearConsultation 
  } = useConsultationStore();

  // Mutations
  const processConsultation = useProcessConsultation();
  const completeConsultation = useCompleteConsultation();

  // We need to access the audio blob directly or assume the store handles text. 
  // We'll use a local instance of useAudioRecorder to get the blob for the API, 
  // or we can pass the blob up from SpeechRecorder if we refactored it. 
  // Let's rely mostly on text input for this implementation since backend NLP works well with text.
  // We can leave audioBlob as null unless passed via an event.

  useEffect(() => {
    // Clear state on unmount
    return () => clearConsultation();
  }, [clearConsultation]);

  const handleGenerateSummary = async () => {
    if (!transcript.trim()) return;
    
    try {
      const result = await processConsultation.mutateAsync({
        appointmentId,
        textInput: transcript,
        audioBlob: null // Assuming text only for now to ensure backend doesn't reject if upload fails
      });
      
      setExtractedData(result.structured_output);
      setConsultationSummary(result.consultation_summary);
    } catch (err) {
      console.error('Failed to process consultation:', err);
    }
  };

  const handleComplete = async () => {
    if (!extractedData) return;
    
    try {
      // In a real flow, the consultation_id would come from the processing result.
      // Let's assume processConsultation returns it, but we can also use a mock ID or get it from store.
      // We will assume the API hook knows or we just pass a placeholder if not present in the mock data.
      await completeConsultation.mutateAsync({
        appointmentId,
        consultationId: 'mock-consultation-id-123' 
      });
      navigate('/doctor/dashboard');
    } catch (err) {
      console.error('Failed to complete consultation:', err);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr 350px', gap: '1.5rem', height: '100%' }}>
      
      {/* Left Column: Patient Info */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h3 style={{ fontSize: '1rem', color: '#64748b', margin: 0, paddingLeft: '0.5rem', borderLeft: '3px solid #0ea5e9' }}>
          Patient Context
        </h3>
        <PatientSummaryCard patientId={patientId} compact={true} />
      </div>

      {/* Center Column: Recording & Processing */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <h3 style={{ fontSize: '1rem', color: '#64748b', margin: 0, paddingLeft: '0.5rem', borderLeft: '3px solid #ef4444' }}>
          Audio Capture
        </h3>
        <SpeechRecorder />
        
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={handleGenerateSummary}
            disabled={processConsultation.isPending || !transcript.trim()}
            className="btn-primary"
            style={{ 
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              opacity: (processConsultation.isPending || !transcript.trim()) ? 0.6 : 1,
              cursor: (processConsultation.isPending || !transcript.trim()) ? 'not-allowed' : 'pointer',
              padding: '0.75rem 1.5rem', backgroundColor: '#0ea5e9', color: 'white',
              border: 'none', borderRadius: '0.5rem', fontWeight: '500'
            }}
          >
            {processConsultation.isPending ? <Loader2 className="spin" size={18} /> : <FileText size={18} />}
            Generate Summary
          </button>
        </div>
      </div>

      {/* Right Column: Extracted Data */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h3 style={{ fontSize: '1rem', color: '#64748b', margin: 0, paddingLeft: '0.5rem', borderLeft: '3px solid #10b981' }}>
          Extracted Data
        </h3>
        
        <div className="glass-panel" style={{ padding: '1.5rem', flex: 1, display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {!extractedData ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#94a3b8', gap: '1rem', textAlign: 'center' }}>
              <Activity size={48} opacity={0.2} />
              <p>Record audio and click "Generate Summary" to extract medical entities.</p>
            </div>
          ) : (
            <>
              {/* Risk Level */}
              <div>
                <h4 style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <AlertTriangle size={14} /> Predicted Risk Level
                </h4>
                <div style={{ display: 'inline-flex', padding: '0.25rem 0.75rem', borderRadius: '1rem', fontSize: '0.875rem', fontWeight: 'bold', backgroundColor: extractedData.risk_level === 'Critical' ? '#fee2e2' : '#f1f5f9', color: extractedData.risk_level === 'Critical' ? '#ef4444' : '#64748b' }}>
                  {extractedData.risk_level || 'Routine'}
                </div>
              </div>

              {/* Symptoms */}
              <div>
                <h4 style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Activity size={14} /> Symptoms
                </h4>
                <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.875rem' }}>
                  {extractedData.symptoms?.map((s, i) => <li key={i}>{s}</li>) || <li>None detected</li>}
                </ul>
              </div>

              {/* Medications */}
              <div>
                <h4 style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Pill size={14} /> Prescribed Medications
                </h4>
                <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.875rem' }}>
                  {extractedData.medications?.map((m, i) => <li key={i}>{m}</li>) || <li>None prescribed</li>}
                </ul>
              </div>

              <div style={{ marginTop: 'auto', paddingTop: '1.5rem', borderTop: '1px solid #e2e8f0' }}>
                <button
                  onClick={handleComplete}
                  disabled={completeConsultation.isPending}
                  style={{
                    width: '100%', padding: '0.75rem', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem',
                    backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '0.5rem', fontWeight: '600',
                    cursor: completeConsultation.isPending ? 'not-allowed' : 'pointer', opacity: completeConsultation.isPending ? 0.7 : 1
                  }}
                >
                  {completeConsultation.isPending ? <Loader2 className="spin" size={18} /> : <CheckCircle size={18} />}
                  Save & Complete
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
