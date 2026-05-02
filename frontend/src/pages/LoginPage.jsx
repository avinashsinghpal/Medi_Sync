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
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--color-bg-primary)', padding: '1rem' }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '28rem', padding: '2.5rem', position: 'relative', overflow: 'hidden' }}>
        {/* Decorative background element */}
        <div style={{ position: 'absolute', top: '-10%', right: '-10%', width: '150px', height: '150px', background: 'var(--color-primary)', borderRadius: '50%', filter: 'blur(60px)', opacity: '0.2', zIndex: '0' }} />
        <div style={{ position: 'absolute', bottom: '-10%', left: '-10%', width: '150px', height: '150px', background: 'var(--color-routine-text)', borderRadius: '50%', filter: 'blur(60px)', opacity: '0.1', zIndex: '0' }} />
        
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
            <div style={{ backgroundColor: '#e0f2fe', color: '#0284c7', padding: '1rem', borderRadius: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Stethoscope size={32} />
            </div>
          </div>
          
          <h1 style={{ fontSize: '1.875rem', textAlign: 'center', marginBottom: '0.5rem', color: 'var(--color-text-primary)' }}>Welcome Back</h1>
          <p style={{ textAlign: 'center', color: 'var(--color-text-secondary)', marginBottom: '2rem' }}>Sign in to your MediSync account</p>

          {error && (
            <div style={{ backgroundColor: 'var(--color-critical-bg)', color: 'var(--color-critical-text)', padding: '0.75rem', borderRadius: '0.5rem', marginBottom: '1.5rem', fontSize: '0.875rem', textAlign: 'center' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label htmlFor="email" style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', color: 'var(--color-text-primary)' }}>Email</label>
              <input 
                id="email" 
                type="email" 
                {...register('email')}
                placeholder="doctor@medisync.com"
                style={{ width: '100%', borderColor: errors.email ? 'var(--color-critical-text)' : 'var(--color-border)' }}
              />
              {errors.email && <p style={{ color: 'var(--color-critical-text)', fontSize: '0.75rem', marginTop: '0.25rem' }}>{errors.email.message}</p>}
            </div>

            <div>
              <label htmlFor="password" style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', color: 'var(--color-text-primary)' }}>Password</label>
              <input 
                id="password" 
                type="password" 
                {...register('password')}
                placeholder="••••••••"
                style={{ width: '100%', borderColor: errors.password ? 'var(--color-critical-text)' : 'var(--color-border)' }}
              />
              {errors.password && <p style={{ color: 'var(--color-critical-text)', fontSize: '0.75rem', marginTop: '0.25rem' }}>{errors.password.message}</p>}
            </div>

            <button 
              type="submit" 
              disabled={isSubmitting}
              style={{
                width: '100%',
                padding: '0.875rem',
                backgroundColor: 'var(--color-primary)',
                color: 'white',
                borderRadius: '0.5rem',
                fontWeight: '600',
                marginTop: '0.5rem',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                gap: '0.5rem',
                opacity: isSubmitting ? 0.7 : 1,
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => !isSubmitting && (e.currentTarget.style.backgroundColor = 'var(--color-primary-hover)')}
              onMouseOut={(e) => !isSubmitting && (e.currentTarget.style.backgroundColor = 'var(--color-primary)')}
            >
              {isSubmitting ? (
                <>
                  <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
                  Signing in...
                </>
              ) : 'Sign In'}
            </button>
          </form>
          
          <div style={{ marginTop: '2rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
            <p>Demo accounts: doctor@medisync.com / doctor123, patient@medisync.com / patient123</p>
          </div>
        </div>
      </div>
      <style>
        {`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}
      </style>
    </div>
  );
}
