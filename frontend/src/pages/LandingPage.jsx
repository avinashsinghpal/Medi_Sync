import { useNavigate } from 'react-router-dom';
import { Activity, User, Stethoscope, ArrowRight, Shield, Clock, HeartPulse } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Navbar */}
      <nav className="glass-panel" style={{ 
        position: 'fixed', top: '1rem', left: '1rem', right: '1rem', 
        padding: '1rem 2rem', display: 'flex', justifyContent: 'space-between', 
        alignItems: 'center', zIndex: 100, borderRadius: 'var(--radius-full)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ background: 'var(--color-primary)', padding: '0.5rem', borderRadius: '50%', color: 'white' }}>
            <Activity size={24} />
          </div>
          <span style={{ fontSize: '1.25rem', fontWeight: '700', color: 'var(--color-text-primary)' }}>MediSync</span>
        </div>
        <div>
          <button 
            className="btn-primary" 
            onClick={() => navigate('/login')}
          >
            Sign In
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', paddingTop: '6rem' }}>
        <div className="container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
          
          <div className="animate-slide-up" style={{ marginBottom: '2rem' }}>
            <span style={{ 
              display: 'inline-block', padding: '0.5rem 1rem', background: 'var(--color-routine-bg)', 
              color: 'var(--color-routine-text)', borderRadius: 'var(--radius-full)', 
              fontSize: '0.875rem', fontWeight: '600', marginBottom: '1.5rem',
              boxShadow: 'var(--shadow-sm)'
            }}>
              ✨ The Future of Healthcare is Here
            </span>
            <h1 style={{ fontSize: 'clamp(2.5rem, 5vw, 4.5rem)', marginBottom: '1.5rem', maxWidth: '800px' }}>
              Intelligent Care, <br />
              <span style={{ color: 'var(--color-primary)' }}>Seamless Experience</span>
            </h1>
            <p style={{ fontSize: '1.125rem', color: 'var(--color-text-secondary)', maxWidth: '600px', margin: '0 auto 3rem auto' }}>
              Experience healthcare redefined. MediSync brings AI-driven prioritization and seamless consultations to both doctors and patients in one unified platform.
            </p>
          </div>

          {/* Action Cards */}
          <div className="animate-slide-up delay-200" style={{ 
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '2rem', width: '100%', maxWidth: '900px' 
          }}>
            {/* Patient Card */}
            <div 
              className="glass-panel"
              style={{ 
                padding: '2.5rem', display: 'flex', flexDirection: 'column', 
                alignItems: 'center', transition: 'all 0.3s ease', cursor: 'pointer'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-10px)';
                e.currentTarget.style.boxShadow = 'var(--shadow-xl)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'var(--glass-shadow)';
              }}
              onClick={() => navigate('/login?role=patient')}
            >
              <div style={{ 
                width: '80px', height: '80px', borderRadius: '50%', 
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', 
                display: 'flex', alignItems: 'center', justifyContent: 'center', 
                color: 'white', marginBottom: '1.5rem',
                boxShadow: '0 10px 20px rgba(16, 185, 129, 0.3)'
              }}>
                <User size={40} />
              </div>
              <h2 style={{ fontSize: '1.75rem', marginBottom: '1rem' }}>I am a Patient</h2>
              <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem' }}>
                Book appointments, track your health history, and connect with top doctors effortlessly.
              </p>
              <button className="btn-secondary" style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '0.5rem', alignItems: 'center' }}>
                Patient Portal <ArrowRight size={18} />
              </button>
            </div>

            {/* Doctor Card */}
            <div 
              className="glass-panel"
              style={{ 
                padding: '2.5rem', display: 'flex', flexDirection: 'column', 
                alignItems: 'center', transition: 'all 0.3s ease', cursor: 'pointer'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-10px)';
                e.currentTarget.style.boxShadow = 'var(--shadow-xl)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'var(--glass-shadow)';
              }}
              onClick={() => navigate('/login?role=doctor')}
            >
              <div style={{ 
                width: '80px', height: '80px', borderRadius: '50%', 
                background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%)', 
                display: 'flex', alignItems: 'center', justifyContent: 'center', 
                color: 'white', marginBottom: '1.5rem',
                boxShadow: '0 10px 20px rgba(2, 132, 199, 0.3)'
              }}>
                <Stethoscope size={40} />
              </div>
              <h2 style={{ fontSize: '1.75rem', marginBottom: '1rem' }}>I am a Doctor</h2>
              <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem' }}>
                Manage priority queues, utilize AI consultations, and provide better care.
              </p>
              <button className="btn-secondary" style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '0.5rem', alignItems: 'center' }}>
                Doctor Portal <ArrowRight size={18} />
              </button>
            </div>
          </div>
          
          {/* Features Section */}
          <div className="animate-slide-up delay-300" style={{ 
            display: 'flex', gap: '3rem', marginTop: '6rem', marginBottom: '4rem',
            justifyContent: 'center', flexWrap: 'wrap'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ color: 'var(--color-primary)', background: '#e0f2fe', padding: '0.75rem', borderRadius: '50%' }}>
                <Shield size={24} />
              </div>
              <div style={{ textAlign: 'left' }}>
                <h4 style={{ fontSize: '1.1rem' }}>Secure Data</h4>
                <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>End-to-end encrypted</span>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ color: '#10b981', background: '#d1fae5', padding: '0.75rem', borderRadius: '50%' }}>
                <Clock size={24} />
              </div>
              <div style={{ textAlign: 'left' }}>
                <h4 style={{ fontSize: '1.1rem' }}>Zero Wait Time</h4>
                <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>Smart queue system</span>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ color: '#f59e0b', background: '#fef3c7', padding: '0.75rem', borderRadius: '50%' }}>
                <HeartPulse size={24} />
              </div>
              <div style={{ textAlign: 'left' }}>
                <h4 style={{ fontSize: '1.1rem' }}>AI Triage</h4>
                <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>Intelligent prioritization</span>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
