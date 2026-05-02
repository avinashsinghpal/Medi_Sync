import { useAudioRecorder } from '../../hooks/useAudioRecorder';
import { Mic, Square, Loader2, CheckCircle2, AlertTriangle } from 'lucide-react';
import { useConsultationStore } from '../../store/consultationStore';
import { useEffect } from 'react';

export default function SpeechRecorder({ onTranscript, onError }) {
  const { status, recordingTime, startRecording, stopRecording } = useAudioRecorder({
    onTranscript: (text) => {
      onTranscript && onTranscript(text);
    },
    onError
  });
  
  const { transcript } = useConsultationStore();
  const setIsRecording = useConsultationStore(state => state.setIsRecording);

  // Sync state to store
  useEffect(() => {
    setIsRecording(status === 'recording');
  }, [status, setIsRecording]);

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Header / Controls */}
      <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f8fafc' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <h3 style={{ margin: 0, fontSize: '1.125rem', color: '#0f172a' }}>Live Transcription</h3>
          {status === 'recording' && (
            <span style={{ 
              display: 'inline-flex', alignItems: 'center', gap: '0.375rem', 
              color: '#ef4444', fontSize: '0.875rem', fontWeight: '600' 
            }}>
              <span style={{ 
                width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ef4444',
                animation: 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite' 
              }} />
              {formatTime(recordingTime)}
            </span>
          )}
        </div>
        
        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: .5; }
          }
          @keyframes waveform {
            0% { transform: scaleY(0.2); }
            50% { transform: scaleY(1); }
            100% { transform: scaleY(0.2); }
          }
        `}</style>

        <div>
          {status === 'idle' || status === 'done' ? (
            <button
              onClick={startRecording}
              style={{
                display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
                padding: '0.5rem 1rem', backgroundColor: '#0ea5e9', color: 'white',
                border: 'none', borderRadius: '0.5rem', fontWeight: '500', cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={e => e.currentTarget.style.backgroundColor = '#0284c7'}
              onMouseOut={e => e.currentTarget.style.backgroundColor = '#0ea5e9'}
            >
              <Mic size={18} /> {status === 'done' ? 'Restart Recording' : 'Start Recording'}
            </button>
          ) : status === 'recording' ? (
            <button
              onClick={stopRecording}
              style={{
                display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
                padding: '0.5rem 1rem', backgroundColor: '#ef4444', color: 'white',
                border: 'none', borderRadius: '0.5rem', fontWeight: '500', cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={e => e.currentTarget.style.backgroundColor = '#dc2626'}
              onMouseOut={e => e.currentTarget.style.backgroundColor = '#ef4444'}
            >
              <Square size={18} fill="currentColor" /> Stop
            </button>
          ) : status === 'processing' ? (
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', color: '#0ea5e9', fontSize: '0.875rem', fontWeight: '500' }}>
              <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> Processing...
            </div>
          ) : status === 'error' ? (
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', color: '#ef4444', fontSize: '0.875rem', fontWeight: '500' }}>
              <AlertTriangle size={18} /> Error accessing mic
            </div>
          ) : null}
        </div>
      </div>

      {/* Waveform Visualization (Mock) */}
      {status === 'recording' && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px', height: '60px', backgroundColor: '#f1f5f9', borderBottom: '1px solid #e2e8f0' }}>
          {[...Array(20)].map((_, i) => (
            <div 
              key={i} 
              style={{
                width: '4px', height: '30px', backgroundColor: '#0ea5e9', borderRadius: '2px',
                animation: `waveform ${0.8 + Math.random() * 0.5}s ease-in-out infinite`,
                animationDelay: `${Math.random() * 0.5}s`
              }} 
            />
          ))}
        </div>
      )}

      {/* Transcript Text Area */}
      <div style={{ flex: 1, padding: '1.5rem', overflowY: 'auto', backgroundColor: '#ffffff', minHeight: '300px' }}>
        {!transcript && status === 'idle' ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#94a3b8' }}>
            <Mic size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
            <p>Click "Start Recording" to begin the consultation.</p>
          </div>
        ) : (
          <p style={{ fontSize: '1.05rem', lineHeight: '1.7', color: '#334155', whiteSpace: 'pre-wrap' }}>
            {transcript}
            {status === 'recording' && (
              <span style={{ 
                display: 'inline-block', width: '4px', height: '1.05rem', 
                backgroundColor: '#0ea5e9', marginLeft: '4px', verticalAlign: 'middle',
                animation: 'pulse 1s infinite'
              }} />
            )}
          </p>
        )}
      </div>
    </div>
  );
}
