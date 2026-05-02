import { create } from 'zustand';

const useConsultationStore = create((set) => ({
  activeAppointmentId: null,
  isRecording: false,
  transcript: '',
  extractedData: null,
  consultationSummary: null,

  setActiveAppointmentId: (id) => set({ activeAppointmentId: id }),
  
  setIsRecording: (isRecording) => set({ isRecording }),
  
  setTranscript: (text) => set({ transcript: text }),
  
  appendTranscript: (text) => set((state) => ({ 
    transcript: state.transcript ? `${state.transcript} ${text}` : text 
  })),
  
  setExtractedData: (data) => set({ extractedData: data }),
  
  setConsultationSummary: (summary) => set({ consultationSummary: summary }),

  clearConsultation: () => set({
    activeAppointmentId: null,
    isRecording: false,
    transcript: '',
    extractedData: null,
    consultationSummary: null,
  }),
}));

export default useConsultationStore;
