import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Stethoscope, LogOut, User, UserCircle, ClipboardList } from 'lucide-react';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="glass-nav">
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '4rem' }}>
        <Link
          to={isAuthenticated ? (user?.role === 'DOCTOR' ? '/doctor/dashboard' : '/patient/dashboard') : '/'}
          style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', textDecoration: 'none' }}
        >
          <div style={{ background: 'linear-gradient(135deg, #0ea5e9, #0284c7)', color: 'white', padding: '0.5rem', borderRadius: '0.625rem', display: 'flex', boxShadow: '0 2px 8px rgba(14,165,233,0.3)' }}>
            <Stethoscope size={20} />
          </div>
          <span style={{ color: 'var(--color-brand-primary)', fontWeight: '800', fontSize: '1.25rem', fontFamily: 'Outfit', letterSpacing: '-0.03em' }}>
            Medi<span style={{ color: 'var(--color-brand-accent)' }}>Sync</span>
          </span>
        </Link>

        {isAuthenticated ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem' }}>
            {/* User Pill */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.625rem',
              padding: '0.35rem 0.875rem 0.35rem 0.35rem',
              background: 'linear-gradient(135deg, #f8fafc, white)',
              border: '1px solid var(--color-border-subtle)',
              borderRadius: 'var(--radius-full)',
              boxShadow: 'var(--shadow-xs)'
            }}>
              <div style={{
                width: '1.875rem', height: '1.875rem', borderRadius: '50%',
                background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: 'white', fontSize: '0.75rem', fontWeight: '700'
              }}>
                {user?.name?.charAt(0) || 'U'}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1 }}>
                <span style={{ fontWeight: '600', color: 'var(--color-text-title)', fontSize: '0.8125rem' }}>{user?.name}</span>
                <span style={{ color: 'var(--color-brand-accent)', fontSize: '0.625rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{user?.role}</span>
              </div>
            </div>

            {/* Patient links */}
            {user?.role === 'PATIENT' && (
              <>
                <Link to="/patient/profile" className="btn-premium-ghost">
                  <UserCircle size={17} />
                  <span>Profile</span>
                </Link>
                <Link to="/patient/history" className="btn-premium-ghost">
                  <ClipboardList size={17} />
                  <span>History</span>
                </Link>
              </>
            )}

            {/* Doctor links */}
            {(user?.role === 'DOCTOR' || user?.role === 'ADMIN') && (
              <Link to="/doctor/patients" className="btn-premium-ghost">
                <User size={17} />
                <span>Patients</span>
              </Link>
            )}

            <button onClick={handleLogout} className="btn-danger-ghost">
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', gap: '1rem' }}>
            <Link to="/login" className="btn-premium btn-premium-primary">
              Sign In to Portal
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
