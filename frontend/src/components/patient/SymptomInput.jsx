import { useState } from 'react';
import { Plus, X } from 'lucide-react';

const COMMON_SYMPTOMS = [
  'Headache', 'Fever', 'Cough', 'Sore Throat', 'Nausea',
  'Fatigue', 'Chest Pain', 'Shortness of Breath', 'Dizziness', 'Muscle Ache'
];

export default function SymptomInput({ symptoms, onChange }) {
  const [inputValue, setInputValue] = useState('');

  const handleAdd = (symptom) => {
    const trimmed = symptom.trim();
    if (trimmed && !symptoms.includes(trimmed)) {
      onChange([...symptoms, trimmed]);
    }
    setInputValue('');
  };

  const handleRemove = (symptom) => {
    onChange(symptoms.filter(s => s !== symptom));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAdd(inputValue);
    }
  };

  const suggestions = COMMON_SYMPTOMS.filter(s => 
    s.toLowerCase().includes(inputValue.toLowerCase()) && !symptoms.includes(s)
  );

  return (
    <div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
        {symptoms.map((symptom, idx) => (
          <span 
            key={idx}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
              backgroundColor: '#e0f2fe', color: '#0369a1',
              padding: '0.375rem 0.75rem', borderRadius: '9999px', fontSize: '0.875rem', fontWeight: '500'
            }}
          >
            {symptom}
            <button
              type="button"
              onClick={() => handleRemove(symptom)}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: 'transparent', border: 'none', color: '#0369a1',
                cursor: 'pointer', padding: 0, marginLeft: '0.25rem'
              }}
            >
              <X size={14} />
            </button>
          </span>
        ))}
      </div>

      <div style={{ position: 'relative' }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a symptom and press Enter..."
            style={{ flex: 1, padding: '0.75rem', borderRadius: '0.375rem', border: '1px solid #cbd5e1' }}
          />
          <button
            type="button"
            onClick={() => handleAdd(inputValue)}
            style={{
              display: 'flex', alignItems: 'center', gap: '0.25rem',
              padding: '0 1rem', backgroundColor: '#0f172a', color: 'white',
              border: 'none', borderRadius: '0.375rem', fontWeight: '500', cursor: 'pointer'
            }}
          >
            <Plus size={18} /> Add
          </button>
        </div>

        {inputValue && suggestions.length > 0 && (
          <ul style={{
            position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 10,
            backgroundColor: 'white', border: '1px solid #e2e8f0', borderRadius: '0.375rem',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', marginTop: '0.25rem',
            listStyle: 'none', padding: 0, margin: '0.25rem 0 0 0', maxHeight: '150px', overflowY: 'auto'
          }}>
            {suggestions.map(s => (
              <li 
                key={s} 
                onClick={() => handleAdd(s)}
                style={{ padding: '0.75rem 1rem', cursor: 'pointer', borderBottom: '1px solid #f1f5f9' }}
                onMouseOver={e => e.currentTarget.style.backgroundColor = '#f8fafc'}
                onMouseOut={e => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                {s}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
