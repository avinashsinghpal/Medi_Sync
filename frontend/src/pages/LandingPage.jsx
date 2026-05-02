import { useNavigate } from 'react-router-dom';
import { Activity, User, Stethoscope, ArrowRight, Shield, Clock, HeartPulse } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: 'var(--color-bg-main)',
      position: 'relative',
      overflowX: 'hidden'
    }}>
      {/* Dynamic Background Elements */}
      <div style={{ 
        position: 'absolute', top: '-10%', right: '-5%', width: '40vw', height: '40vw', 
        background: 'radial-gradient(circle, rgba(14, 165, 233, 0.12) 0%, transparent 70%)', 
        borderRadius: '50%', zIndex: 0, filter: 'blur(100px)' 
      }} />
      <div style={{ 
        position: 'absolute', bottom: '10%', left: '-5%', width: '30vw', height: '30vw', 
        background: 'radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 70%)', 
        borderRadius: '50%', zIndex: 0, filter: 'blur(80px)' 
      }} />

      {/* Navbar */}
      <nav className="glass-nav" style={{ 
        position: 'fixed', top: '1.25rem', left: '2rem', right: '2rem', 
        padding: '0.75rem 2.5rem', display: 'flex', justifyContent: 'space-between', 
        alignItems: 'center', zIndex: 100, borderRadius: 'var(--radius-full)',
        border: '1px solid var(--glass-border)',
        boxShadow: 'var(--shadow-premium)',
        background: 'rgba(255, 255, 255, 0.8)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ 
            background: 'var(--color-brand-primary)', 
            padding: '0.5rem', borderRadius: '0.75rem', color: 'white',
            display: 'flex'
          }}>
            <Activity size={22} />
          </div>
          <span style={{ fontSize: '1.5rem', fontWeight: '800', fontFamily: 'Outfit', color: 'var(--color-brand-primary)', letterSpacing: '-0.02em' }}>
            MediSync<span style={{ color: 'var(--color-brand-accent)' }}>AI</span>
          </span>
        </div>
        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <button 
            className="btn-premium btn-premium-primary" 
            onClick={() => navigate('/login')}
            style={{ padding: '0.625rem 1.75rem', borderRadius: 'var(--radius-full)' }}
          >
            Sign In to Portal
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', paddingTop: '10rem', position: 'relative', zIndex: 1 }}>
        <div className="container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
          
          <div className="animate-fade-in" style={{ marginBottom: '4rem' }}>
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1.5rem' }}>
              <span style={{ 
                display: 'inline-flex', alignItems: 'center', gap: '0.625rem',
                padding: '0.5rem 1.25rem', background: 'white', 
                color: 'var(--color-brand-accent)', borderRadius: 'var(--radius-full)', 
                fontSize: '0.8125rem', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.05em',
                boxShadow: 'var(--shadow-sm)',
                border: '1px solid var(--color-border-subtle)'
              }}>
                <HeartPulse size={14} /> The Future of Clinical Intelligence
              </span>
            </div>
            <h1 style={{ 
              fontSize: 'clamp(3rem, 7vw, 5.5rem)', 
              marginBottom: '1.5rem', 
              maxWidth: '1000px', 
              fontWeight: '800', 
              letterSpacing: '-0.04em',
              lineHeight: 1,
              fontFamily: 'Outfit'
            }}>
              Care That Moves as <br />
              <span style={{ 
                background: 'linear-gradient(135deg, var(--color-brand-accent), #3b82f6, #6366f1)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                display: 'inline-block'
              }}>Fast as You Do.</span>
            </h1>
            <p style={{ 
              fontSize: '1.25rem', 
              color: 'var(--color-text-body)', 
              maxWidth: '700px', 
              margin: '0 auto 4rem auto',
              lineHeight: '1.6',
              opacity: 0.8
            }}>
              MediSync AI streamlines the entire clinical lifecycle. From intelligent triage to AI-powered transcription, we give doctors their time back and patients the care they deserve.
            </p>
          </div>

          {/* Action Cards */}
          <div className="animate-fade-in stagger-2" style={{ 
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', 
            gap: '2.5rem', width: '100%', maxWidth: '1100px' 
          }}>
            {/* Patient Card */}
            <div 
              className="glass-card card-hover"
              style={{ 
                padding: '3.5rem 2.5rem', display: 'flex', flexDirection: 'column', 
                alignItems: 'center', cursor: 'pointer',
                background: 'rgba(255, 255, 255, 0.6)',
                borderColor: 'var(--color-border-subtle)'
              }}
              onClick={() => navigate('/login?role=patient')}
            >
              <div style={{ 
                width: '80px', height: '80px', borderRadius: '22px', 
                background: 'var(--color-brand-success)', 
                display: 'flex', alignItems: 'center', justifyContent: 'center', 
                color: 'white', marginBottom: '2rem',
                boxShadow: '0 12px 24px -6px rgba(16, 185, 129, 0.3)',
                transform: 'rotate(-4deg)'
              }}>
                <User size={40} />
              </div>
              <h2 style={{ fontSize: '2rem', marginBottom: '1rem', fontFamily: 'Outfit' }}>Patient Portal</h2>
              <p style={{ color: 'var(--color-text-muted)', marginBottom: '2.5rem', fontSize: '1.05rem' }}>
                Access your medical history, book instant consultations, and manage your health records in one secure vault.
              </p>
              <button className="btn-premium btn-premium-secondary" style={{ width: '100%' }}>
                Enter Portal <ArrowRight size={18} />
              </button>
            </div>

            {/* Doctor Card */}
            <div 
              className="glass-card card-hover"
              style={{ 
                padding: '3.5rem 2.5rem', display: 'flex', flexDirection: 'column', 
                alignItems: 'center', cursor: 'pointer',
                background: 'rgba(255, 255, 255, 0.6)',
                borderColor: 'var(--color-border-subtle)'
              }}
              onClick={() => navigate('/login?role=doctor')}
            >
              <div style={{ 
                width: '80px', height: '80px', borderRadius: '22px', 
                background: 'var(--color-brand-primary)', 
                display: 'flex', alignItems: 'center', justifyContent: 'center', 
                color: 'white', marginBottom: '2rem',
                boxShadow: '0 12px 24px -6px rgba(15, 23, 42, 0.3)',
                transform: 'rotate(4deg)'
              }}>
                <Stethoscope size={40} />
              </div>
              <h2 style={{ fontSize: '2rem', marginBottom: '1rem', fontFamily: 'Outfit' }}>Doctor Portal</h2>
              <p style={{ color: 'var(--color-text-muted)', marginBottom: '2.5rem', fontSize: '1.05rem' }}>
                Harness AI-driven prioritization, automated clinical documentation, and smart queue management.
              </p>
              <button className="btn-premium btn-premium-secondary" style={{ width: '100%' }}>
                Enter Portal <ArrowRight size={18} />
              </button>
            </div>
          </div>
          
          {/* Trust Section */}
          <div className="animate-fade-in stagger-3" style={{ 
            display: 'flex', gap: '5rem', marginTop: '8rem', marginBottom: '8rem',
            justifyContent: 'center', flexWrap: 'wrap'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <Shield size={24} color="var(--color-brand-accent)" />
              <div style={{ textAlign: 'left' }}>
                <h4 style={{ fontSize: '1rem', fontWeight: '700' }}>HIPAA Compliant</h4>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>Bank-grade security</span>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <Clock size={24} color="var(--color-brand-success)" />
              <div style={{ textAlign: 'left' }}>
                <h4 style={{ fontSize: '1rem', fontWeight: '700' }}>Real-time Sync</h4>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>Instant data availability</span>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <HeartPulse size={24} color="var(--color-brand-danger)" />
              <div style={{ textAlign: 'left' }}>
                <h4 style={{ fontSize: '1rem', fontWeight: '700' }}>AI Triage</h4>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>99% extraction accuracy</span>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

