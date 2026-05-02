import Navbar from '../components/shared/Navbar';

export default function PatientDashboard() {
  return (
    <div>
      <Navbar />
      <div className="container" style={{ marginTop: '2rem' }}>
        <h1 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Patient Dashboard</h1>
        <p>This is a placeholder for the Patient Dashboard.</p>
      </div>
    </div>
  );
}
