import { useState, useRef, useCallback } from 'react';

export const useAudioRecorder = ({ onTranscript, onError }) => {
  const [status, setStatus] = useState('idle'); // idle | recording | processing | done | error
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);

  // Mock transcription for demonstration
  const mockTranscriptIntervalRef = useRef(null);
  const mockSentences = [
    "Patient reports a headache that started two days ago.",
    " The pain is throbbing and located primarily in the frontal region.",
    " It's a 7 out of 10 on the pain scale.",
    " Patient also mentions slight nausea but no vomiting.",
    " Blood pressure is 130 over 85.",
    " I will prescribe some ibuprofen and recommend rest."
  ];
  let sentenceIndex = 0;

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        // In a real app, send chunks to a WebSocket or accumulate for an API
      };

      mediaRecorder.onstop = () => {
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start(1000); // 1 sec chunks
      setStatus('recording');
      setRecordingTime(0);
      
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

      // MOCK: Simulate streaming transcription text
      sentenceIndex = 0;
      mockTranscriptIntervalRef.current = setInterval(() => {
        if (sentenceIndex < mockSentences.length) {
          if (onTranscript) {
            onTranscript(mockSentences[sentenceIndex]);
          }
          sentenceIndex++;
        }
      }, 3000); // Every 3 seconds add a sentence

    } catch (err) {
      console.error("Error accessing microphone:", err);
      setStatus('error');
      if (onError) onError(err);
    }
  }, [onTranscript, onError]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    
    clearInterval(timerRef.current);
    clearInterval(mockTranscriptIntervalRef.current);
    
    // Status immediately goes to processing to simulate API sending
    setStatus('processing');
    
    // Simulate API finish
    setTimeout(() => {
      setStatus('done');
    }, 1500);

  }, []);

  return {
    status,
    recordingTime,
    startRecording,
    stopRecording
  };
};
