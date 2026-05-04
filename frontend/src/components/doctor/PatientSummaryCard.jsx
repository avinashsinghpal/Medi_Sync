import { useNavigate } from 'react-router-dom';
import { usePatientSummary } from '../../hooks/usePatientData';
import PriorityBadge from '../shared/PriorityBadge';
import LoadingSpinner from '../shared/LoadingSpinner';
import { AlertTriangle, ChevronRight, Activity, Pill, Calendar, Hash } from 'lucide-react';

export default function PatientSummaryCard({ patientId, compact = false }) {
  const navigate = useNavigate();
  const { data: patient, isLoading, isError } = usePatientSummary(patientId);

  if (isLoading) {
    return (
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '200px' }}>
        <LoadingSpinner size="md" />
      </div>
    );
  }

  if (isError || !patient) {
    return (
      <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid #ef4444' }}>
        <h3 style={{ color: '#ef4444', margin: 0 }}>Error loading patient data</h3>
        <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.5rem' }}>Could not load data for patient {patientId}</p>
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.125rem' }}>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '0.25rem', color: '#0f172a' }}>{patient.name}</h2>
          <div style={{ display: 'flex', gap: '1rem', color: '#64748b', fontSize: '0.875rem' }}>
            <span>Age: <strong style={{ color: '#0f172a' }}>{patient.age}</strong></span>
            <span>Blood Group: <strong style={{ color: '#dc2626' }}>{patient.blood_group || 'Unknown'}</strong></span>
          </div>
        </div>
        <PriorityBadge priority={patient.priority} />
      </div>

      {/* Risk flags */}
      {patient.risk_flags && patient.risk_flags.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {patient.risk_flags.map((flag, idx) => (
            <span key={idx} style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
              backgroundColor: '#fee2e2', color: '#b91c1c',
              padding: '0.25rem 0.5rem', borderRadius: '0.375rem', fontSize: '0.75rem', fontWeight: '600',
            }}>
              <AlertTriangle size={12} />{flag}
            </span>
          ))}
        </div>
      )}

      {/* Stats row */}
      {!compact && (
        <div style={{ display: 'flex', gap: '1rem', paddingTop: '0.5rem', borderTop: '1px solid #e2e8f0' }}>
          {patient.total_visits > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.8125rem', color: '#64748b' }}>
              <Hash size={13} /><span><strong style={{ color: '#0f172a' }}>{patient.total_visits}</strong> visit{patient.total_visits !== 1 ? 's' : ''}</span>
            </div>
          )}
          {patient.last_visit && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.8125rem', color: '#64748b' }}>
              <Calendar size={13} /><span>Last: <strong style={{ color: '#0f172a' }}>{new Date(patient.last_visit).toLocaleDateString()}</strong></span>
            </div>
          )}
        </div>
      )}

      {/* Diagnoses & Medications */}
      {!compact && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', paddingTop: '1rem', borderTop: '1px solid #e2e8f0' }}>
          <div>
            <h4 style={{ fontSize: '0.8125rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.625rem', fontWeight: '600' }}>
              <Activity size={13} color="#0ea5e9" /> Recent Diagnoses
            </h4>
            <ul style={{ listStyle: 'none', margin: 0, padding: 0, fontSize: '0.8125rem', display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
              {patient.diagnoses?.slice(0, 3).map((d, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.375rem', color: '#334155' }}>
                  <span style={{ color: '#0ea5e9', marginTop: '2px' }}>•</span>{d}
                </li>
              ))}
              {(!patient.diagnoses || patient.diagnoses.length === 0) && (
                <li style={{ color: '#94a3b8', fontStyle: 'italic' }}>None recorded</li>
              )}
            </ul>
          </div>
          <div>
            <h4 style={{ fontSize: '0.8125rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.625rem', fontWeight: '600' }}>
              <Pill size={13} color="#8b5cf6" /> Current Medications
            </h4>
            <ul style={{ listStyle: 'none', margin: 0, padding: 0, fontSize: '0.8125rem', display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
              {patient.medications?.slice(0, 3).map((m, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.375rem', color: '#334155' }}>
                  <span style={{ color: '#8b5cf6', marginTop: '2px' }}>•</span>{m}
                </li>
              ))}
              {(!patient.medications || patient.medications.length === 0) && (
                <li style={{ color: '#94a3b8', fontStyle: 'italic' }}>None recorded</li>
              )}
            </ul>
          </div>
        </div>
      )}

      {/* View History button */}
      <button
        onClick={() => navigate(`/doctor/patient/${patientId}/history`)}
        style={{
          marginTop: compact ? '0' : '0.25rem',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.25rem',
          width: '100%', padding: '0.625rem',
          backgroundColor: '#f8fafc', color: '#0ea5e9',
          fontWeight: '500', fontSize: '0.875rem',
          borderRadius: '0.5rem', border: '1px solid #e2e8f0',
          cursor: 'pointer', transition: 'all 0.2s',
        }}
        onMouseOver={e => { e.currentTarget.style.backgroundColor = '#e0f2fe'; e.currentTarget.style.borderColor = '#bae6fd'; }}
        onMouseOut={e => { e.currentTarget.style.backgroundColor = '#f8fafc'; e.currentTarget.style.borderColor = '#e2e8f0'; }}
      >
        View Full History <ChevronRight size={16} />
      </button>
    </div>
  );
}
