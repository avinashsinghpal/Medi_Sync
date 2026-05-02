import { useState, useEffect } from 'react';
import Navbar from '../components/shared/Navbar';
import { useAuthStore } from '../store/authStore';
import { useUpdatePatient } from '../hooks/usePatientData';
import api from '../utils/api';
import { User, Mail, Phone, MapPin, Save, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

export default function PatientProfilePage() {
  const { user } = useAuthStore();
  const [formData, setFormData] = useState({
    full_name: '',
    contact_email: '',
    contact_phone: '',
    date_of_birth: '',
    gender: 'prefer_not_to_say',
    address: '',
    blood_group: ''
  });
  const [isLoading, setIsLoading] = useState(true);
  const [saveStatus, setSaveStatus] = useState(null); // 'success' | 'error' | null
  
  const updateMutation = useUpdatePatient(user?.id);

  useEffect(() => {
    async function fetchProfile() {
      if (!user?.id) return;
      try {
        const response = await api.get(`/patients/${user.id}`);
        const data = response.data;
        setFormData({
          full_name: data.full_name || '',
          contact_email: data.contact_email || '',
          contact_phone: data.contact_phone || '',
          date_of_birth: data.date_of_birth || '',
          gender: data.gender || 'prefer_not_to_say',
          address: data.address || '',
          blood_group: data.blood_group || ''
        });
      } catch (err) {
        console.error('Failed to fetch profile', err);
      } finally {
        setIsLoading(false);
      }
    }
    fetchProfile();
  }, [user?.id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setSaveStatus(null);
    updateMutation.mutate(formData, {
      onSuccess: () => {
        setSaveStatus('success');
        setTimeout(() => setSaveStatus(null), 3000);
      },
      onError: () => {
        setSaveStatus('error');
      }
    });
  };

  if (isLoading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg-main)' }}>
        <Navbar />
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
          <Loader2 size={48} className="spin" color="var(--color-brand-accent)" />
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg-main)' }}>
      <Navbar />
      
      <main className="container" style={{ padding: '3rem 2rem' }}>
        <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
          <div style={{ marginBottom: '2.5rem' }}>
            <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>My Profile</h1>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '1.125rem' }}>Update your personal information and contact details.</p>
          </div>

          <form onSubmit={handleSubmit} className="glass-card" style={{ padding: '2.5rem', border: '1px solid var(--color-border-subtle)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
              <div style={{ gridColumn: 'span 2' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: 'var(--color-text-muted)', marginBottom: '0.625rem' }}>Full Name</label>
                <div style={{ position: 'relative' }}>
                  <User size={18} style={{ position: 'absolute', left: '1.25rem', top: '1rem', color: 'var(--color-text-muted)' }} />
                  <input 
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    style={{ paddingLeft: '3.25rem' }}
                    required
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: 'var(--color-text-muted)', marginBottom: '0.625rem' }}>Email Address</label>
                <div style={{ position: 'relative' }}>
                  <Mail size={18} style={{ position: 'absolute', left: '1.25rem', top: '1rem', color: 'var(--color-text-muted)' }} />
                  <input 
                    type="email"
                    name="contact_email"
                    value={formData.contact_email}
                    onChange={handleChange}
                    style={{ paddingLeft: '3.25rem' }}
                    required
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: 'var(--color-text-muted)', marginBottom: '0.625rem' }}>Phone Number</label>
                <div style={{ position: 'relative' }}>
                  <Phone size={18} style={{ position: 'absolute', left: '1.25rem', top: '1rem', color: 'var(--color-text-muted)' }} />
                  <input 
                    name="contact_phone"
                    value={formData.contact_phone}
                    onChange={handleChange}
                    style={{ paddingLeft: '3.25rem' }}
                    required
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: 'var(--color-text-muted)', marginBottom: '0.625rem' }}>Date of Birth</label>
                <input 
                  type="date"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: 'var(--color-text-muted)', marginBottom: '0.625rem' }}>Gender</label>
                <select name="gender" value={formData.gender} onChange={handleChange}>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              </div>

              <div style={{ gridColumn: 'span 2' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: 'var(--color-text-muted)', marginBottom: '0.625rem' }}>Residential Address</label>
                <div style={{ position: 'relative' }}>
                  <MapPin size={18} style={{ position: 'absolute', left: '1.25rem', top: '1rem', color: 'var(--color-text-muted)' }} />
                  <textarea 
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    rows="3"
                    style={{ paddingLeft: '3.25rem', resize: 'none' }}
                  />
                </div>
              </div>
            </div>

            <div style={{ marginTop: '2.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                {saveStatus === 'success' && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-brand-success)', fontSize: '0.9375rem', fontWeight: '600' }}>
                    <CheckCircle size={20} />
                    Profile updated successfully!
                  </div>
                )}
                {saveStatus === 'error' && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-brand-danger)', fontSize: '0.9375rem', fontWeight: '600' }}>
                    <AlertCircle size={20} />
                    Failed to update profile. Please try again.
                  </div>
                )}
              </div>
              
              <button 
                type="submit" 
                className="btn-premium btn-premium-primary"
                disabled={updateMutation.isPending}
                style={{ minWidth: '160px' }}
              >
                {updateMutation.isPending ? <Loader2 size={20} className="spin" /> : <><Save size={20} /> Save Changes</>}
              </button>
            </div>
          </form>
        </div>
      </main>

      <style>{`
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
