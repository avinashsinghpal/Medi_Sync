import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuthStore } from '../store/authStore';
import { Stethoscope, Loader2 } from 'lucide-react';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

export default function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [error, setError] = useState('');
  
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(loginSchema)
  });

  const onSubmit = async (data) => {
    try {
      setError('');
      const user = await login(data.email, data.password);
      if (user.role === 'DOCTOR' || user.role === 'ADMIN') {
        navigate('/doctor/dashboard');
      } else {
        navigate('/patient/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', backgroundColor: 'var(--color-bg-main)' }}>
      {/* Left Branding Panel (Hidden on mobile, 50% width on desktop) */}
      <div className="dynamic-gradient desktop-only" style={{ flex: 1, display: 'none', flexDirection: 'column', padding: '4rem', color: 'white', position: 'relative', overflow: 'hidden' }}>
         <div style={{ position: 'absolute', inset: 0, backgroundImage: 'url(/login-bg.png)', backgroundSize: 'cover', backgroundPosition: 'center', opacity: 0.4, mixBlendMode: 'overlay' }} />
         
         <div style={{ position: 'relative', zIndex: 10, display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: 'auto' }}>
            <div style={{ backgroundColor: 'white', color: 'var(--color-brand-primary)', padding: '0.75rem', borderRadius: '1rem', boxShadow: 'var(--shadow-md)' }}>
              <Stethoscope size={32} />
            </div>
            <h1 style={{ color: 'white', fontSize: '2rem', margin: 0 }}>MediSync AI</h1>
         </div>
         
         <div style={{ position: 'relative', zIndex: 10, marginTop: 'auto' }} className="animate-fade-in stagger-1">
            <h2 style={{ fontSize: '3rem', fontWeight: 700, lineHeight: 1.2, marginBottom: '1.5rem', color: 'white' }}>Intelligent Patient History System</h2>
            <p style={{ fontSize: '1.25rem', opacity: 0.9, maxWidth: '600px', lineHeight: 1.6 }}>Streamline your clinical workflows with AI-powered consultation summaries and intelligent priority queuing.</p>
         </div>
      </div>

      {/* Right Login Panel */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem', position: 'relative' }}>
        {/* Subtle background decoration for right side */}
        <div style={{ position: 'absolute', top: '0', right: '0', width: '300px', height: '300px', background: 'var(--color-brand-accent)', borderRadius: '50%', filter: 'blur(100px)', opacity: '0.05', zIndex: '0' }} />
        
        <div style={{ width: '100%', maxWidth: '400px', position: 'relative', zIndex: 1 }} className="animate-fade-in">
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '2.5rem' }}>
            <div className="mobile-only-icon" style={{ backgroundColor: '#e0f2fe', color: '#0284c7', padding: '1rem', borderRadius: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem', boxShadow: 'var(--shadow-sm)' }}>
              <Stethoscope size={32} />
            </div>
            <h1 style={{ fontSize: '2.25rem', textAlign: 'center', marginBottom: '0.5rem' }}>Welcome Back</h1>
            <p style={{ textAlign: 'center', color: 'var(--color-text-muted)' }}>Sign in to access your dashboard</p>
          </div>

          {error && (
            <div className="animate-fade-in" style={{ backgroundColor: 'var(--color-crit-bg)', color: 'var(--color-crit-red)', padding: '1rem', borderRadius: 'var(--radius-button)', marginBottom: '1.5rem', fontSize: '0.9375rem', textAlign: 'center', border: '1px solid #fda4af' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <label htmlFor="email" style={{ display: 'block', fontSize: '0.9375rem', fontWeight: '500', marginBottom: '0.5rem', color: 'var(--color-text-title)' }}>Email Address</label>
              <input 
                id="email" 
                type="email" 
                {...register('email')}
                placeholder="doctor@medisync.com"
                style={{ borderColor: errors.email ? 'var(--color-brand-danger)' : 'var(--color-border-medium)' }}
              />
              {errors.email && <p style={{ color: 'var(--color-brand-danger)', fontSize: '0.8125rem', marginTop: '0.375rem', fontWeight: 500 }}>{errors.email.message}</p>}
            </div>

            <div>
              <label htmlFor="password" style={{ display: 'block', fontSize: '0.9375rem', fontWeight: '500', marginBottom: '0.5rem', color: 'var(--color-text-title)' }}>Password</label>
              <input 
                id="password" 
                type="password" 
                {...register('password')}
                placeholder="••••••••"
                style={{ borderColor: errors.password ? 'var(--color-brand-danger)' : 'var(--color-border-medium)' }}
              />
              {errors.password && <p style={{ color: 'var(--color-brand-danger)', fontSize: '0.8125rem', marginTop: '0.375rem', fontWeight: 500 }}>{errors.password.message}</p>}
            </div>

            <button 
              type="submit" 
              disabled={isSubmitting}
              className="btn-premium btn-premium-primary"
              style={{
                width: '100%',
                marginTop: '1rem',
                opacity: isSubmitting ? 0.7 : 1,
                cursor: isSubmitting ? 'not-allowed' : 'pointer'
              }}
            >
              {isSubmitting ? (
                <>
                  <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
                  Authenticating...
                </>
              ) : 'Sign In'}
            </button>
          </form>
          
          <div style={{ marginTop: '2.5rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--color-text-muted)', padding: '1.5rem', backgroundColor: 'var(--color-border-subtle)', borderRadius: 'var(--radius-button)' }}>
            <p style={{ fontWeight: 600, marginBottom: '0.5rem', color: 'var(--color-text-body)' }}>Demo Credentials</p>
            <p><strong>Doctor:</strong> doctor@medisync.com / doctor123</p>
            <p style={{ marginTop: '0.25rem' }}><strong>Patient:</strong> patient@medisync.com / patient123</p>
          </div>
        </div>
      </div>

      <style>
        {`
          @media (min-width: 1024px) {
            .desktop-only { display: flex !important; }
            .mobile-only-icon { display: none !important; }
          }
          @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        `}
      </style>
    </div>
  );
}
