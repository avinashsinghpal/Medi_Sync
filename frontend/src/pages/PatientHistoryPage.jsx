import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/shared/Navbar';
import PatientSummaryCard from '../components/doctor/PatientSummaryCard';
import { usePatientHistory } from '../hooks/usePatientData';
import { useAuthStore } from '../store/authStore';
import { ArrowLeft, Clock, FileText, FlaskConical, Pill, Stethoscope, ClipboardList } from 'lucide-react';
import LoadingSpinner from '../components/shared/LoadingSpinner';

const RECORD_TYPE_META = {
  diagnosis: {
    label: 'Diagnosis',
    icon: Stethoscope,
    color: '#0ea5e9',
    bg: '#e0f2fe',
    border: '#bae6fd',
  },
  prescription: {
    label: 'Prescription',
    icon: Pill,
    color: '#8b5cf6',
    bg: '#ede9fe',
    border: '#c4b5fd',
  },
  lab_result: {
    label: 'Lab Result',
    icon: FlaskConical,
    color: '#10b981',
    bg: '#d1fae5',
    border: '#6ee7b7',
  },
  note: {
    label: 'Clinical Note',
    icon: ClipboardList,
    color: '#f59e0b',
    bg: '#fef3c7',
    border: '#fcd34d',
  },
};

function RecordCard({ record }) {
  const meta = RECORD_TYPE_META[record.record_type] || RECORD_TYPE_META.note;
  const Icon = meta.icon;
  const date = record.recorded_at ? new Date(record.recorded_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  }) : 'Unknown date';

  return (
    <div style={{
      border: `1px solid ${meta.border}`,
      borderLeft: `4px solid ${meta.color}`,
      borderRadius: '0.75rem',
      padding: '1.25rem 1.5rem',
      backgroundColor: '#ffffff',
      transition: 'box-shadow 0.2s, transform 0.2s',
      cursor: 'default',
    }}
      onMouseOver={e => { e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.08)'; e.currentTarget.style.transform = 'translateY(-1px)'; }}
      onMouseOut={e => { e.currentTarget.style.boxShadow = 'none'; e.currentTarget.style.transform = 'none'; }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
          <span style={{
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            width: '32px', height: '32px', borderRadius: '0.5rem',
            backgroundColor: meta.bg, color: meta.color, flexShrink: 0,
          }}>
            <Icon size={16} />
          </span>
          <h3 style={{ margin: 0, fontSize: '0.9375rem', color: '#0f172a', fontWeight: '600' }}>
            {record.title}
          </h3>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.25rem', flexShrink: 0, marginLeft: '1rem' }}>
          <span style={{
            fontSize: '0.6875rem', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em',
            color: meta.color, backgroundColor: meta.bg,
            padding: '0.2rem 0.5rem', borderRadius: '0.25rem',
          }}>
            {meta.label}
          </span>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{date}</span>
        </div>
      </div>

      {/* Content */}
      <p style={{ fontSize: '0.875rem', color: '#475569', margin: '0 0 1rem 0', lineHeight: '1.6' }}>
        {record.content}
      </p>

      {/* Tags */}
      {record.tags && record.tags.length > 0 && (
        <div style={{ display: 'flex', gap: '0.375rem', flexWrap: 'wrap' }}>
          {record.tags.map((tag, i) => (
            <span key={i} style={{
              fontSize: '0.6875rem', color: '#64748b', backgroundColor: '#f1f5f9',
              padding: '0.2rem 0.5rem', borderRadius: '0.25rem', fontWeight: '500',
              border: '1px solid #e2e8f0',
            }}>
              #{tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default function PatientHistoryPage() {
  const { id: paramId } = useParams();
  const { user } = useAuthStore();
  const id = paramId || user?.id;
  const navigate = useNavigate();
  const { data: history, isLoading, isError } = usePatientHistory(id);

  const grouped = history ? history.reduce((acc, record) => {
    const type = record.record_type || 'note';
    if (!acc[type]) acc[type] = [];
    acc[type].push(record);
    return acc;
  }, {}) : {};

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f1f5f9' }}>
      <Navbar />

      <main style={{ flex: 1, padding: '1.5rem', maxWidth: '1280px', margin: '0 auto', width: '100%', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

        {/* Back button */}
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <button
            onClick={() => navigate(-1)}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
              color: '#64748b', background: 'transparent', border: 'none',
              fontSize: '0.875rem', fontWeight: '500', cursor: 'pointer',
              padding: '0.5rem', marginLeft: '-0.5rem', borderRadius: '0.375rem',
            }}
            onMouseOver={e => e.currentTarget.style.backgroundColor = '#e2e8f0'}
            onMouseOut={e => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            <ArrowLeft size={16} /> Back
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: '1.5rem', alignItems: 'start' }}>

          {/* Left: Summary Card */}
          <div style={{ position: 'sticky', top: '1.5rem' }}>
            <PatientSummaryCard patientId={id} compact={false} />
          </div>

          {/* Right: History */}
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <h2 style={{ fontSize: '1.25rem', color: '#0f172a', margin: '0 0 1.5rem 0', display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <Clock size={20} color="#0ea5e9" /> Comprehensive Medical History
            </h2>

            {isLoading ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
                <LoadingSpinner />
              </div>
            ) : isError ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#ef4444' }}>
                Failed to load patient history.
              </div>
            ) : !history || history.length === 0 ? (
              <div style={{ padding: '4rem 2rem', textAlign: 'center', color: '#64748b', backgroundColor: '#f8fafc', borderRadius: '0.5rem' }}>
                <FileText size={48} style={{ opacity: 0.2, margin: '0 auto 1rem auto', display: 'block' }} />
                <p style={{ margin: 0 }}>No historical records found for this patient.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                {/* Summary chips */}
                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                  {Object.entries(RECORD_TYPE_META).map(([type, meta]) => {
                    const count = grouped[type]?.length || 0;
                    if (!count) return null;
                    return (
                      <span key={type} style={{
                        display: 'inline-flex', alignItems: 'center', gap: '0.375rem',
                        fontSize: '0.8125rem', fontWeight: '600', color: meta.color,
                        backgroundColor: meta.bg, border: `1px solid ${meta.border}`,
                        padding: '0.35rem 0.75rem', borderRadius: '2rem',
                      }}>
                        <meta.icon size={13} /> {count} {meta.label}{count !== 1 ? 's' : ''}
                      </span>
                    );
                  })}
                </div>

                {/* All records sorted by date descending */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {[...history]
                    .sort((a, b) => new Date(b.recorded_at) - new Date(a.recorded_at))
                    .map((record, index) => (
                      <RecordCard key={record.record_id || index} record={record} />
                    ))}
                </div>
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}
