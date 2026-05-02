import { useState, useEffect } from 'react';
import useAudioRecorder from '../../hooks/useAudioRecorder';
import useConsultationStore from '../../store/consultationStore';
import { Mic, Square, AlertCircle } from 'lucide-react';

export default function SpeechRecorder({ onTranscript, onError }) {
  const { isRecording, startRecording, stopRecording, error: recordError } = useAudioRecorder();
  const [timer, setTimer] = useState(0);
  
  const { setTranscript, transcript } = useConsultationStore();

  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setTimer((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(interval);
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setTimer(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  useEffect(() => {
    if (recordError && onError) {
      onError(new Error(recordError));
    }
  }, [recordError, onError]);

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  const handleStart = () => {
    setTranscript('');
    startRecording();
  };

  const handleStop = () => {
    stopRecording();
    // Simulate live transcription by putting something in the text area 
    // if we wanted to mock live speech-to-text.
    // In a real app, this would stream chunks to a backend WebSocket.
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0, fontSize: '1.125rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Mic size={20} color={isRecording ? '#ef4444' : '#64748b'} />
          Audio Capture
        </h3>
        {isRecording && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ef4444', fontWeight: 'bold' }}>
            <span style={{ 
              width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ef4444', 
              animation: 'pulse 1.5s infinite' 
            }} />
            {formatTime(timer)}
          </div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem 0' }}>
        {!isRecording ? (
          <button
            onClick={handleStart}
            style={{
              width: '64px', height: '64px', borderRadius: '50%', border: 'none',
              backgroundColor: '#ef4444', color: 'white', display: 'flex', justifyContent: 'center', alignItems: 'center',
              cursor: 'pointer', boxShadow: '0 4px 6px -1px rgba(239, 68, 68, 0.4)',
              transition: 'transform 0.1s'
            }}
            onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.95)'}
            onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            <Mic size={32} />
          </button>
        ) : (
          <button
            onClick={handleStop}
            style={{
              width: '64px', height: '64px', borderRadius: '50%', border: 'none',
              backgroundColor: '#1e293b', color: 'white', display: 'flex', justifyContent: 'center', alignItems: 'center',
              cursor: 'pointer', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.2)',
              transition: 'transform 0.1s'
            }}
            onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.95)'}
            onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            <Square size={24} fill="currentColor" />
          </button>
        )}
      </div>

      {recordError && (
        <div style={{ color: '#ef4444', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={16} /> {recordError}
        </div>
      )}

      <div>
        <label style={{ display: 'block', fontSize: '0.875rem', color: '#64748b', marginBottom: '0.5rem', fontWeight: '500' }}>
          Live Transcript (or type manual notes here)
        </label>
        <textarea
          value={transcript}
          onChange={(e) => {
            setTranscript(e.target.value);
            if (onTranscript) onTranscript(e.target.value);
          }}
          placeholder="Transcription will appear here... You can also type notes manually."
          style={{
            width: '100%', minHeight: '120px', padding: '0.75rem', borderRadius: '0.5rem',
            border: '1px solid #cbd5e1', fontSize: '0.875rem', resize: 'vertical',
            fontFamily: 'inherit', outline: 'none'
          }}
          onFocus={(e) => e.target.style.borderColor = '#0ea5e9'}
          onBlur={(e) => e.target.style.borderColor = '#cbd5e1'}
        />
      </div>
    </div>
  );
}
