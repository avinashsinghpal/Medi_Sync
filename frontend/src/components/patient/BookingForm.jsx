import { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import SymptomInput from './SymptomInput';
import PriorityBadge from '../shared/PriorityBadge';
import { useBookAppointment, useEstimatedWaitTime } from '../../hooks/useAppointments';
import { Loader2, Calendar, Clock, AlertCircle } from 'lucide-react';

const formSchema = z.object({
  patient_id: z.string().min(1, 'Patient ID is required'),
  date_time: z.string().min(1, 'Date & Time are required'),
  reason: z.string().min(10, 'Please provide a brief reason (min 10 chars)'),
  symptoms: z.array(z.string()).min(1, 'Please add at least one symptom'),
});

export default function BookingForm() {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();
  const { mutate: bookAppointment, isPending } = useBookAppointment();

  const { control, register, handleSubmit, formState: { errors }, watch, trigger } = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      patient_id: 'p-1', // Mocking current user ID
      date_time: '',
      reason: '',
      symptoms: [],
    },
    mode: 'onTouched'
  });

  const symptoms = watch('symptoms');
  const { data: estimate, isLoading: isEstimating } = useEstimatedWaitTime(symptoms);

  const handleNext = async (fieldsToValidate) => {
    const isStepValid = await trigger(fieldsToValidate);
    if (isStepValid) setStep(prev => prev + 1);
  };

  const onSubmit = (data) => {
    bookAppointment({
      ...data,
      priority: estimate?.priority || 'routine'
    }, {
      onSuccess: () => {
        navigate('/patient/dashboard');
      }
    });
  };

  return (
    <div className="glass-panel" style={{ maxWidth: '600px', margin: '0 auto', overflow: 'hidden' }}>
      
      {/* Stepper Header */}
      <div style={{ display: 'flex', backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
        {[1, 2, 3, 4].map(s => (
          <div key={s} style={{ 
            flex: 1, padding: '1rem 0', textAlign: 'center', 
            fontWeight: step === s ? '600' : '500',
            color: step === s ? '#0ea5e9' : (step > s ? '#10b981' : '#94a3b8'),
            borderBottom: step === s ? '3px solid #0ea5e9' : '3px solid transparent'
          }}>
            Step {s}
          </div>
        ))}
      </div>

      <div style={{ padding: '2rem' }}>
        <form onSubmit={handleSubmit(onSubmit)}>
          
          {/* STEP 1: Basic Info */}
          {step === 1 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <h2 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', color: '#0f172a' }}>Reason for Visit</h2>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Brief Reason</label>
                <textarea 
                  {...register('reason')} 
                  rows="3" 
                  placeholder="E.g., Follow up on blood test results"
                  style={{ width: '100%', borderColor: errors.reason ? '#ef4444' : '#cbd5e1' }}
                />
                {errors.reason && <span style={{ color: '#ef4444', fontSize: '0.875rem' }}>{errors.reason.message}</span>}
              </div>
              <button 
                type="button" 
                onClick={() => handleNext(['reason'])}
                style={{ padding: '0.75rem', backgroundColor: '#0f172a', color: 'white', borderRadius: '0.5rem', cursor: 'pointer', fontWeight: '500' }}
              >
                Next Step
              </button>
            </div>
          )}

          {/* STEP 2: Symptoms */}
          {step === 2 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <h2 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', color: '#0f172a' }}>Current Symptoms</h2>
              <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '-0.5rem' }}>Adding symptoms helps us prioritize your care.</p>
              
              <Controller
                control={control}
                name="symptoms"
                render={({ field }) => (
                  <SymptomInput symptoms={field.value} onChange={field.onChange} />
                )}
              />
              {errors.symptoms && <span style={{ color: '#ef4444', fontSize: '0.875rem' }}>{errors.symptoms.message}</span>}

              <button 
                type="button" 
                onClick={() => handleNext(['symptoms'])}
                style={{ padding: '0.75rem', backgroundColor: '#0f172a', color: 'white', borderRadius: '0.5rem', cursor: 'pointer', fontWeight: '500', marginTop: '1rem' }}
              >
                Next Step
              </button>
            </div>
          )}

          {/* STEP 3: Date & Time */}
          {step === 3 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <h2 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', color: '#0f172a' }}>Select Date & Time</h2>
              
              {estimate && (
                <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', padding: '1rem', borderRadius: '0.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                  <AlertCircle color="#10b981" />
                  <div>
                    <h4 style={{ margin: '0 0 0.25rem 0', color: '#065f46' }}>AI Priority Assessment</h4>
                    <p style={{ margin: 0, fontSize: '0.875rem', color: '#064e3b' }}>
                      Based on your symptoms, your priority is assessed as <strong>{estimate.priority.toUpperCase()}</strong>. 
                      Estimated wait time: ~{estimate.estimatedWaitMinutes} mins.
                    </p>
                  </div>
                </div>
              )}

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Preferred Slot</label>
                <input 
                  type="datetime-local" 
                  {...register('date_time')}
                  style={{ width: '100%', padding: '0.75rem', borderColor: errors.date_time ? '#ef4444' : '#cbd5e1' }}
                />
                {errors.date_time && <span style={{ color: '#ef4444', fontSize: '0.875rem' }}>{errors.date_time.message}</span>}
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button type="button" onClick={() => setStep(2)} style={{ flex: 1, padding: '0.75rem', backgroundColor: 'transparent', border: '1px solid #cbd5e1', borderRadius: '0.5rem', cursor: 'pointer', fontWeight: '500' }}>Back</button>
                <button type="button" onClick={() => handleNext(['date_time'])} style={{ flex: 2, padding: '0.75rem', backgroundColor: '#0f172a', color: 'white', borderRadius: '0.5rem', border: 'none', cursor: 'pointer', fontWeight: '500' }}>Review Booking</button>
              </div>
            </div>
          )}

          {/* STEP 4: Confirm */}
          {step === 4 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <h2 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', color: '#0f172a' }}>Review & Confirm</h2>
              
              <div style={{ backgroundColor: '#f8fafc', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#64748b', fontSize: '0.875rem' }}>Date & Time</span>
                  <span style={{ fontWeight: '500', display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Calendar size={16}/> {watch('date_time')}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#64748b', fontSize: '0.875rem' }}>Reason</span>
                  <span style={{ fontWeight: '500' }}>{watch('reason')}</span>
                </div>
                <div>
                  <span style={{ color: '#64748b', fontSize: '0.875rem', display: 'block', marginBottom: '0.5rem' }}>Symptoms</span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {watch('symptoms').map(s => (
                      <span key={s} style={{ backgroundColor: '#e2e8f0', padding: '0.25rem 0.5rem', borderRadius: '0.25rem', fontSize: '0.75rem' }}>{s}</span>
                    ))}
                  </div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '1rem', borderTop: '1px solid #cbd5e1' }}>
                  <span style={{ color: '#64748b', fontSize: '0.875rem' }}>Assessed Priority</span>
                  {isEstimating ? <Loader2 size={16} className="spin" /> : <PriorityBadge priority={estimate?.priority || 'routine'} />}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <button type="button" onClick={() => setStep(3)} style={{ flex: 1, padding: '0.75rem', backgroundColor: 'transparent', border: '1px solid #cbd5e1', borderRadius: '0.5rem', cursor: 'pointer', fontWeight: '500' }}>Edit</button>
                <button 
                  type="submit" 
                  disabled={isPending}
                  style={{ 
                    flex: 2, padding: '0.75rem', backgroundColor: '#0ea5e9', color: 'white', borderRadius: '0.5rem', 
                    border: 'none', cursor: isPending ? 'not-allowed' : 'pointer', fontWeight: '600',
                    display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem'
                  }}
                >
                  {isPending ? <Loader2 size={18} className="spin" /> : 'Confirm Booking'}
                </button>
              </div>
            </div>
          )}

        </form>
      </div>
      <style>{`.spin { animation: spin 1s linear infinite; }`}</style>
    </div>
  );
}
