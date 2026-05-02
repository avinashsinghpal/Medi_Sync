import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './store/authStore';

// Pages
import LoginPage from './pages/LoginPage';
import DoctorDashboard from './pages/DoctorDashboard';
import PatientDashboard from './pages/PatientDashboard';
import ConsultationPage from './pages/ConsultationPage';
import AppointmentBookingPage from './pages/AppointmentBookingPage';
import PatientHistoryPage from './pages/PatientHistoryPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Protected Route Wrapper
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

function App() {
  const { isAuthenticated, user } = useAuthStore();

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route 
            path="/" 
            element={
              isAuthenticated 
                ? <Navigate to={user?.role === 'DOCTOR' || user?.role === 'ADMIN' ? "/doctor/dashboard" : "/patient/dashboard"} /> 
                : <Navigate to="/login" />
            } 
          />
          <Route path="/login" element={<LoginPage />} />
          
          <Route 
            path="/doctor/*" 
            element={
              <ProtectedRoute allowedRoles={['DOCTOR', 'ADMIN']}>
                <Routes>
                  <Route path="dashboard" element={<DoctorDashboard />} />
                  <Route path="consultation/:id" element={<ConsultationPage />} />
                  <Route path="patient/:id" element={<PatientHistoryPage />} />
                  {/* Add more doctor routes here */}
                </Routes>
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/patient/*" 
            element={
              <ProtectedRoute allowedRoles={['PATIENT']}>
                <Routes>
                  <Route path="dashboard" element={<PatientDashboard />} />
                  <Route path="book" element={<AppointmentBookingPage />} />
                  {/* Add more patient routes here */}
                </Routes>
              </ProtectedRoute>
            } 
          />

          <Route path="*" element={
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', flexDirection: 'column' }}>
              <h1>404 Not Found</h1>
              <p>The page you're looking for doesn't exist.</p>
            </div>
          } />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
