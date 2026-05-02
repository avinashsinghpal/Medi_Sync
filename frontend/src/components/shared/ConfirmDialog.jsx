import { X } from 'lucide-react';

export default function ConfirmDialog({ 
  isOpen, 
  title, 
  message, 
  onConfirm, 
  onCancel, 
  confirmText = 'Confirm', 
  cancelText = 'Cancel',
  isDestructive = false
}) {
  if (!isOpen) return null;

  return (
    <div 
      style={{
        position: 'fixed',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.5)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 50
      }}
    >
      <div 
        style={{
          backgroundColor: 'white',
          borderRadius: '0.75rem',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          width: '100%',
          maxWidth: '28rem',
          padding: '1.5rem',
          animation: 'modalSlideIn 0.2s ease-out'
        }}
      >
        <style>{`@keyframes modalSlideIn { from { opacity: 0; transform: translateY(1rem) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }`}</style>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#0f172a' }}>{title}</h3>
          <button onClick={onCancel} style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>
        <div style={{ marginBottom: '1.5rem', color: '#475569' }}>
          {message}
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
          <button 
            onClick={onCancel}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '0.375rem',
              color: '#475569',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            {cancelText}
          </button>
          <button 
            onClick={onConfirm}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: isDestructive ? '#ef4444' : '#0ea5e9',
              border: 'none',
              borderRadius: '0.375rem',
              color: 'white',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
