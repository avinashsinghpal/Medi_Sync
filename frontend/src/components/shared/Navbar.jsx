import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Stethoscope, LogOut, User, UserCircle } from 'lucide-react';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="glass-nav">
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '4.5rem' }}>
        <Link 
          to={isAuthenticated ? (user?.role === 'DOCTOR' ? '/doctor/dashboard' : '/patient/dashboard') : '/'} 
          style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', textDecoration: 'none' }}
        >
          <div style={{ backgroundColor: 'var(--color-brand-accent)', color: 'white', padding: '0.5rem', borderRadius: '0.75rem', display: 'flex' }}>
            <Stethoscope size={22} />
          </div>
          <span style={{ color: 'var(--color-brand-primary)', fontWeight: '700', fontSize: '1.375rem', fontFamily: 'Outfit' }}>MediSync</span>
        </Link>
        
        {isAuthenticated ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.375rem 0.75rem', backgroundColor: 'var(--color-border-subtle)', borderRadius: 'var(--radius-full)' }}>
              <div style={{ width: '2rem', height: '2rem', borderRadius: '50%', backgroundColor: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-brand-primary)', boxShadow: 'var(--shadow-sm)' }}>
                <User size={16} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1 }}>
                <span style={{ fontWeight: '600', color: 'var(--color-text-title)', fontSize: '0.8125rem' }}>{user?.name}</span>
                <span style={{ color: 'var(--color-brand-accent)', fontSize: '0.6875rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.025em' }}>{user?.role}</span>
              </div>
            </div>

            {user?.role === 'PATIENT' && (
              <Link to="/patient/profile" className="btn-premium-ghost" style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', padding: '0.5rem', borderRadius: 'var(--radius-button)' }}>
                <UserCircle size={20} />
                <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>Profile</span>
              </Link>
            )}

            <button 
              onClick={handleLogout}
              className="btn-premium-ghost"
              style={{ color: 'var(--color-brand-danger)' }}
            >
              <LogOut size={18} />
              <span style={{ fontSize: '0.875rem', fontWeight: '600' }}>Logout</span>
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', gap: '1rem' }}>
            <Link to="/login" className="btn-premium btn-premium-primary">
              Login to Portal
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
