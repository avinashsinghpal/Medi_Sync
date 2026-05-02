import { useNavigate } from 'react-router-dom';
import { Activity, User, Stethoscope, ArrowRight, Shield, Clock, HeartPulse } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: 'var(--color-bg-primary)',
      position: 'relative',
      overflowX: 'hidden'
    }}>
      {/* Dynamic Background Elements */}
      <div style={{ 
        position: 'absolute', top: '-10%', right: '-5%', width: '40vw', height: '40vw', 
        background: 'radial-gradient(circle, rgba(14, 165, 233, 0.15) 0%, transparent 70%)', 
        borderRadius: '50%', zIndex: 0, filter: 'blur(80px)' 
      }} />
      <div style={{ 
        position: 'absolute', bottom: '10%', left: '-5%', width: '30vw', height: '30vw', 
        background: 'radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%)', 
        borderRadius: '50%', zIndex: 0, filter: 'blur(60px)' 
      }} />

      {/* Navbar */}
      <nav className="glass-panel" style={{ 
        position: 'fixed', top: '1.5rem', left: '1.5rem', right: '1.5rem', 
        padding: '0.875rem 2.5rem', display: 'flex', justifyContent: 'space-between', 
        alignItems: 'center', zIndex: 100, borderRadius: 'var(--radius-full)',
        border: '1px solid rgba(255, 255, 255, 0.4)',
        boxShadow: '0 15px 35px -5px rgba(0, 0, 0, 0.05)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem' }}>
          <div style={{ 
            background: 'linear-gradient(135deg, var(--color-primary) 0%, #0369a1 100%)', 
            padding: '0.625rem', borderRadius: '12px', color: 'white',
            boxShadow: '0 8px 16px -4px rgba(14, 165, 233, 0.4)'
          }}>
            <Activity size={24} />
          </div>
          <span style={{ fontSize: '1.5rem', fontWeight: '800', letterSpacing: '-0.025em', color: 'var(--color-text-primary)' }}>MediSync<span style={{ color: 'var(--color-primary)' }}>.</span></span>
        </div>
        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <button 
            className="btn-primary" 
            onClick={() => navigate('/login')}
            style={{ padding: '0.625rem 2rem' }}
          >
            Sign In
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', paddingTop: '8rem', position: 'relative', zIndex: 1 }}>
        <div className="container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
          
          <div className="animate-slide-up" style={{ marginBottom: '3.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
              <span style={{ 
                display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
                padding: '0.5rem 1.25rem', background: 'white', 
                color: 'var(--color-primary)', borderRadius: 'var(--radius-full)', 
                fontSize: '0.875rem', fontWeight: '700',
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.05)',
                border: '1px solid #f1f5f9'
              }}>
                <HeartPulse size={16} /> AI-Powered Health Platform
              </span>
            </div>
            <h1 style={{ 
              fontSize: 'clamp(2.75rem, 6vw, 5rem)', 
              marginBottom: '1.5rem', 
              maxWidth: '900px', 
              fontWeight: '800', 
              letterSpacing: '-0.04em',
              lineHeight: 1.05
            }}>
              Intelligent Care for <br />
              <span style={{ 
                background: 'linear-gradient(to right, var(--color-primary), #0ea5e9, #6366f1)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                display: 'inline-block'
              }}>Modern Healthcare.</span>
            </h1>
            <p style={{ 
              fontSize: '1.25rem', 
              color: 'var(--color-text-secondary)', 
              maxWidth: '650px', 
              margin: '0 auto 4rem auto',
              lineHeight: '1.6',
              fontWeight: '450'
            }}>
              The ultimate platform for seamless patient-doctor connection. AI-driven triage, instant consultations, and secure medical history in one place.
            </p>
          </div>

          {/* Action Cards */}
          <div className="animate-slide-up delay-200" style={{ 
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', 
            gap: '2.5rem', width: '100%', maxWidth: '1000px' 
          }}>
            {/* Patient Card */}
            <div 
              className="glass-panel"
              style={{ 
                padding: '3rem 2.5rem', display: 'flex', flexDirection: 'column', 
                alignItems: 'center', transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)', cursor: 'pointer',
                border: '1px solid rgba(255, 255, 255, 0.6)',
                backgroundColor: 'rgba(255, 255, 255, 0.7)'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-12px) scale(1.02)';
                e.currentTarget.style.boxShadow = '0 30px 60px -12px rgba(0, 0, 0, 0.1)';
                e.currentTarget.style.borderColor = 'rgba(16, 185, 129, 0.3)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0) scale(1)';
                e.currentTarget.style.boxShadow = 'var(--glass-shadow)';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.6)';
              }}
              onClick={() => navigate('/login?role=patient')}
            >
              <div style={{ 
                width: '90px', height: '90px', borderRadius: '24px', 
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', 
                display: 'flex', alignItems: 'center', justifyContent: 'center', 
                color: 'white', marginBottom: '2rem',
                boxShadow: '0 12px 24px -6px rgba(16, 185, 129, 0.4)',
                transform: 'rotate(-5deg)'
              }}>
                <User size={44} />
              </div>
              <h2 style={{ fontSize: '2rem', marginBottom: '1rem', fontWeight: '700' }}>Patient Portal</h2>
              <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2.5rem', fontSize: '1.05rem', lineHeight: '1.5' }}>
                Take control of your health journey. Book appointments, access records, and chat with providers.
              </p>
              <button className="btn-secondary" style={{ width: '100%', padding: '1rem' }}>
                Enter Portal <ArrowRight size={20} />
              </button>
            </div>

            {/* Doctor Card */}
            <div 
              className="glass-panel"
              style={{ 
                padding: '3rem 2.5rem', display: 'flex', flexDirection: 'column', 
                alignItems: 'center', transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)', cursor: 'pointer',
                border: '1px solid rgba(255, 255, 255, 0.6)',
                backgroundColor: 'rgba(255, 255, 255, 0.7)'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-12px) scale(1.02)';
                e.currentTarget.style.boxShadow = '0 30px 60px -12px rgba(0, 0, 0, 0.1)';
                e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.3)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0) scale(1)';
                e.currentTarget.style.boxShadow = 'var(--glass-shadow)';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.6)';
              }}
              onClick={() => navigate('/login?role=doctor')}
            >
              <div style={{ 
                width: '90px', height: '90px', borderRadius: '24px', 
                background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%)', 
                display: 'flex', alignItems: 'center', justifyContent: 'center', 
                color: 'white', marginBottom: '2rem',
                boxShadow: '0 12px 24px -6px rgba(2, 132, 199, 0.4)',
                transform: 'rotate(5deg)'
              }}>
                <Stethoscope size={44} />
              </div>
              <h2 style={{ fontSize: '2rem', marginBottom: '1rem', fontWeight: '700' }}>Doctor Portal</h2>
              <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2.5rem', fontSize: '1.05rem', lineHeight: '1.5' }}>
                Optimize your clinical workflow. Manage smart queues and leverage AI for faster consultations.
              </p>
              <button className="btn-secondary" style={{ width: '100%', padding: '1rem' }}>
                Enter Portal <ArrowRight size={20} />
              </button>
            </div>
          </div>
          
          {/* Features Section */}
          <div className="animate-slide-up delay-300" style={{ 
            display: 'flex', gap: '4rem', marginTop: '8rem', marginBottom: '6rem',
            justifyContent: 'center', flexWrap: 'wrap'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
              <div style={{ color: 'var(--color-primary)', background: '#e0f2fe', padding: '1rem', borderRadius: '16px' }}>
                <Shield size={28} />
              </div>
              <div style={{ textAlign: 'left' }}>
                <h4 style={{ fontSize: '1.15rem', fontWeight: '700' }}>Secure Data</h4>
                <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.95rem' }}>End-to-end encrypted privacy</span>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
              <div style={{ color: '#10b981', background: '#d1fae5', padding: '1rem', borderRadius: '16px' }}>
                <Clock size={28} />
              </div>
              <div style={{ textAlign: 'left' }}>
                <h4 style={{ fontSize: '1.15rem', fontWeight: '700' }}>Zero Wait Time</h4>
                <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.95rem' }}>AI-driven priority system</span>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
              <div style={{ color: '#f59e0b', background: '#fef3c7', padding: '1rem', borderRadius: '16px' }}>
                <HeartPulse size={28} />
              </div>
              <div style={{ textAlign: 'left' }}>
                <h4 style={{ fontSize: '1.15rem', fontWeight: '700' }}>AI Triage</h4>
                <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.95rem' }}>Advanced clinical extraction</span>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

