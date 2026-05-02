import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Stethoscope, LogOut, User } from 'lucide-react';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav style={{ 
      backgroundColor: 'white', 
      borderBottom: '1px solid #e2e8f0',
      position: 'sticky',
      top: 0,
      zIndex: 40,
      boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
    }}>
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '4rem' }}>
        <Link to={isAuthenticated ? (user?.role === 'DOCTOR' ? '/doctor/dashboard' : '/patient/dashboard') : '/'} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#0ea5e9', fontWeight: '700', fontSize: '1.25rem' }}>
          <Stethoscope size={24} />
          <span>MediSync</span>
        </Link>
        
        {isAuthenticated ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#64748b', fontSize: '0.875rem' }}>
              <div style={{ width: '2rem', height: '2rem', borderRadius: '50%', backgroundColor: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0f172a' }}>
                <User size={16} />
              </div>
              <span style={{ fontWeight: '500', color: '#0f172a' }}>{user?.name}</span>
              <span style={{ backgroundColor: '#e0f2fe', color: '#0284c7', padding: '0.125rem 0.375rem', borderRadius: '0.25rem', fontSize: '0.625rem', fontWeight: 'bold' }}>{user?.role}</span>
            </div>
            <button 
              onClick={handleLogout}
              style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: '#64748b', background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '0.875rem' }}
              onMouseOver={(e) => e.currentTarget.style.color = '#ef4444'}
              onMouseOut={(e) => e.currentTarget.style.color = '#64748b'}
            >
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </div>
        ) : (
          <div>
            <Link to="/login" style={{ padding: '0.5rem 1rem', backgroundColor: '#0ea5e9', color: 'white', borderRadius: '0.375rem', fontWeight: '500' }}>Login</Link>
          </div>
        )}
      </div>
    </nav>
  );
}
