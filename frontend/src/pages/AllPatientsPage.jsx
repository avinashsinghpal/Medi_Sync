import { useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/shared/Navbar';
import { useAllPatients, useSearchPatients } from '../hooks/usePatientData';
import { Search, User, Mail, Phone, Calendar, ChevronRight, Loader2, ArrowLeft } from 'lucide-react';

export default function AllPatientsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const { data: allPatientsData, isLoading: isLoadingAll } = useAllPatients();
  const { data: searchResults, isLoading: isSearching } = useSearchPatients(searchQuery);

  const patients = searchQuery.length >= 2 ? searchResults : (allPatientsData?.patients || []);
  const isLoading = searchQuery.length >= 2 ? isSearching : isLoadingAll;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg-main)' }}>
      <Navbar />
      
      <main className="container" style={{ padding: '3rem 2rem' }}>
        <div className="animate-fade-in" style={{ marginBottom: '3rem' }}>
          <Link to="/doctor/dashboard" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-text-muted)', textDecoration: 'none', marginBottom: '1.5rem', fontWeight: '500', fontSize: '0.9375rem' }}>
            <ArrowLeft size={16} />
            Back to Dashboard
          </Link>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>Patient Directory</h1>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '1.125rem' }}>Search and manage all clinical patient records in the system.</p>
        </div>

        <div className="animate-fade-in stagger-1" style={{ marginBottom: '2.5rem' }}>
          <div style={{ position: 'relative', maxWidth: '600px' }}>
            <Search 
              size={20} 
              style={{ position: 'absolute', left: '1.25rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} 
            />
            <input 
              type="text" 
              placeholder="Search by name, email, or patient ID..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: '3.5rem', height: '3.5rem', fontSize: '1.0625rem', boxShadow: 'var(--shadow-sm)' }}
            />
            {isSearching && (
              <Loader2 
                size={20} 
                className="spin" 
                style={{ position: 'absolute', right: '1.25rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-brand-accent)' }} 
              />
            )}
          </div>
        </div>

        <div className="animate-fade-in stagger-2">
          {isLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '5rem 0' }}>
              <Loader2 size={48} className="spin" color="var(--color-brand-accent)" />
            </div>
          ) : patients.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '1.5rem' }}>
              {patients.map((patient) => (
                <Link 
                  key={patient.patient_id} 
                  to={`/doctor/patient/${patient.patient_id}/history`}
                  className="glass-card card-hover"
                  style={{ textDecoration: 'none', padding: '1.5rem', display: 'flex', gap: '1.25rem', alignItems: 'center' }}
                >
                  <div style={{ 
                    width: '4rem', height: '4rem', borderRadius: '1rem', 
                    backgroundColor: 'var(--color-med-bg)', color: 'var(--color-med-blue)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}>
                    <User size={32} />
                  </div>
                  
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <h3 style={{ fontSize: '1.125rem', marginBottom: '0.25rem' }}>{patient.full_name}</h3>
                      <span style={{ 
                        fontSize: '0.6875rem', fontWeight: '700', padding: '0.25rem 0.5rem', 
                        borderRadius: '0.375rem', backgroundColor: 'var(--color-border-subtle)', 
                        color: 'var(--color-text-muted)', textTransform: 'uppercase'
                      }}>
                        {patient.patient_id}
                      </span>
                    </div>
                    
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginTop: '0.75rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                        <Calendar size={14} />
                        <span>{patient.age} yrs, {patient.gender}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                        <Mail size={14} />
                        <span style={{ maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{patient.contact_email}</span>
                      </div>
                    </div>
                  </div>
                  
                  <ChevronRight size={20} color="var(--color-border-medium)" />
                </Link>
              ))}
            </div>
          ) : (
            <div className="glass-card" style={{ padding: '5rem 0', textAlign: 'center', color: 'var(--color-text-muted)' }}>
              <Search size={48} style={{ margin: '0 auto 1.5rem', opacity: 0.2 }} />
              <h3 style={{ fontSize: '1.25rem', color: 'var(--color-text-title)' }}>No patients found</h3>
              <p>Try adjusting your search criteria or register a new patient.</p>
            </div>
          )}
        </div>
      </main>
      
      <style>{`
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: translateY(-50%) rotate(0deg); } to { transform: translateY(-50%) rotate(360deg); } }
      `}</style>
    </div>
  );
}
