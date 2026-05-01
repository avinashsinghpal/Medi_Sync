## Purpose
React.js frontend — Doctor Dashboard and Patient Booking Interface.

**Calm healthcare tone. Minimal cognitive load. Fast readability.**

## Tech Stack
- React 18 + Vite
- React Router v6
- Zustand (state management)
- React Query (server state / API calls)
- Recharts (analytics charts)
- CSS Modules (component-level styling)
- React Hook Form + Zod (form validation)

---

## File Structure

```
frontend/src/
├── components/
│   ├── doctor/
│   │   ├── PriorityQueue.jsx        # Doctor's appointment queue with priority badges
│   │   ├── PatientSummaryCard.jsx   # Compact patient overview card
│   │   ├── ConsultationPanel.jsx    # Active consultation workspace
│   │   ├── SpeechRecorder.jsx       # Audio capture + live transcription display
│   │   └── DashboardStats.jsx       # Stats cards (total, critical, completed)
│   ├── patient/
│   │   ├── BookingForm.jsx          # Step-by-step appointment booking
│   │   ├── SymptomInput.jsx         # Guided symptom entry with suggestions
│   │   ├── AppointmentCard.jsx      # Single appointment status card
│   │   └── MedicalHistory.jsx       # Expandable medical history timeline
│   └── shared/
│       ├── PriorityBadge.jsx        # 🔴🟡🟢 colored badge component
│       ├── LoadingSpinner.jsx
│       ├── ErrorBoundary.jsx
│       ├── ConfirmDialog.jsx
│       └── Navbar.jsx
├── pages/
│   ├── DoctorDashboard.jsx          # Main doctor view (requires DOCTOR role)
│   ├── PatientDashboard.jsx         # Patient self-service portal
│   ├── ConsultationPage.jsx         # Active consultation with audio
│   ├── PatientProfilePage.jsx       # Full patient history view
│   ├── AppointmentBookingPage.jsx   # Patient appointment booking flow
│   ├── LoginPage.jsx
│   └── NotFoundPage.jsx
├── hooks/
│   ├── usePatientData.js            # React Query hooks for patient API
│   ├── useAppointments.js           # Appointment management hooks
│   ├── useDashboard.js              # Dashboard data hooks
│   ├── useConsultation.js           # Consultation processing hook
│   └── useAudioRecorder.js          # MediaRecorder API wrapper
├── store/
│   ├── authStore.js                 # JWT token + user role state
│   ├── dashboardStore.js            # Doctor dashboard UI state
│   └── consultationStore.js         # Active consultation state
└── utils/
    ├── api.js                       # Axios instance with auth interceptor
    ├── formatters.js                # Date, duration, name formatters
    └── priorityHelpers.js           # Priority level → color/icon mapping
```

---

## Component Specifications

### `PriorityQueue.jsx`
- Displays ordered list of today's appointments
- Each row shows: queue position, patient name, age, priority badge, scheduled time, estimated duration
- Rows are color-coded: red background (critical), yellow (moderate), white (routine)
- "Start Consultation" button on CONFIRMED appointments
- Real-time refresh every 60 seconds via React Query
- Props: `doctorId: string, date: string`

### `PatientSummaryCard.jsx`
- Compact card showing: name, age, blood group, priority badge, last 3 diagnoses, current meds
- Expandable "View Full History" button → navigates to `PatientProfilePage`
- Shows risk flags as highlighted warning pills
- Props: `patientId: string, compact?: boolean`

### `ConsultationPanel.jsx`
- Three-column layout: patient info | recording controls | extracted data
- Left: PatientSummaryCard (compact mode)
- Center: SpeechRecorder with live transcript display
- Right: Real-time NLP extraction results updating as doctor speaks
- "Generate Summary" button → calls POST /api/consultation/process
- "Save & Complete" button → calls PATCH /appointments/{id}/complete
- Props: `appointmentId: string, patientId: string`

### `SpeechRecorder.jsx`
- Uses `useAudioRecorder` hook (MediaRecorder API)
- Visual waveform animation while recording
- Live transcript display (streaming or polling)
- Recording timer display
- States: idle | recording | processing | done | error
- Props: `onTranscript: (text: string) => void, onError: (err: Error) => void`

### `BookingForm.jsx`
- Multi-step form (Step 1: Patient info, Step 2: Date/Time, Step 3: Symptoms, Step 4: Confirm)
- Step 3 uses `SymptomInput` with guided suggestions
- Shows AI-predicted priority badge after symptom entry
- Shows estimated wait time from API
- Validates each step before proceeding

---

## State: `authStore.js`

```javascript
{
  user: { id, email, role, name } | null,
  token: string | null,
  isAuthenticated: boolean,
  login: (email, password) => Promise<void>,
  logout: () => void,
  refreshToken: () => Promise<void>,
}
```

## State: `consultationStore.js`

```javascript
{
  activeAppointmentId: string | null,
  isRecording: boolean,
  transcript: string,
  extractedData: ExtractionResult | null,
  consultationSummary: string | null,
  setTranscript: (text: string) => void,
  setExtractedData: (data) => void,
  clearConsultation: () => void,
}
```

---

## Routing

```
/login                   → LoginPage (public)
/doctor/dashboard        → DoctorDashboard (DOCTOR | ADMIN)
/doctor/consultation/:id → ConsultationPage (DOCTOR)
/doctor/patient/:id      → PatientProfilePage (DOCTOR | ADMIN | NURSE)
/patient/dashboard       → PatientDashboard (PATIENT)
/patient/book            → AppointmentBookingPage (PATIENT)
*                        → NotFoundPage
```

---

## Priority Color Mapping

```javascript
// utils/priorityHelpers.js
export const PRIORITY_CONFIG = {
  critical: { color: "#ef4444", bg: "#fef2f2", icon: "🔴", label: "Critical" },
  moderate: { color: "#f59e0b", bg: "#fffbeb", icon: "🟡", label: "Moderate" },
  routine:  { color: "#10b981", bg: "#f0fdf4", icon: "🟢", label: "Routine" },
};
```

---

## Expected Component Test Outcomes

| Component | Test | Expected |
|---|---|---|
| PriorityBadge | priority="critical" | Red badge with 🔴 |
| BookingForm | Empty symptoms submit | Form validation error shown |
| PriorityQueue | CRITICAL items | Displayed first, red highlighted |
| ConsultationPanel | Start recording | SpeechRecorder enters recording state |
| PatientSummaryCard | No blood_group | Shows "Unknown" gracefully |
