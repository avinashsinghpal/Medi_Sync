import Navbar from '../components/shared/Navbar';
import BookingForm from '../components/patient/BookingForm';

export default function AppointmentBookingPage() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f8fafc' }}>
      <Navbar />
      
      <main className="container" style={{ flex: 1, padding: '3rem 1.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <h1 style={{ fontSize: '2.25rem', color: '#0f172a', marginBottom: '0.5rem' }}>Book an Appointment</h1>
          <p style={{ color: '#64748b', fontSize: '1.125rem' }}>Follow the steps below to schedule your consultation.</p>
        </div>
        
        <BookingForm />
      </main>
    </div>
  );
}
