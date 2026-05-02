import Navbar from '../components/shared/Navbar';

export default function DoctorDashboard() {
  return (
    <div>
      <Navbar />
      <div className="container" style={{ marginTop: '2rem' }}>
        <h1 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Doctor Dashboard</h1>
        <p>This is a placeholder for the Doctor Dashboard.</p>
      </div>
    </div>
  );
}
