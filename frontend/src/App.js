import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import './styles/App.css';
import ViewGoals from "./pages/ViewGoals";
import Header from './components/Header';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import PersonalRecordsPage from './pages/PersonalRecordsPage';
import StreakPage from './pages/StreakPage';
import LogWorkoutPage from './pages/LogWorkoutPage';
import ViewWorkouts from './pages/ViewWorkouts';

// ProtectedRoute component defined here
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/view_goals" element={<ProtectedRoute><ViewGoals /></ProtectedRoute>} />
          <Route path="/personal_records" element={<ProtectedRoute><PersonalRecordsPage /></ProtectedRoute>} />
          <Route path="/streak" element={<ProtectedRoute><StreakPage /></ProtectedRoute>} />
          <Route path="/log_workout" element={<ProtectedRoute><LogWorkoutPage /></ProtectedRoute>} />
          <Route path="/view-workouts" element={<ProtectedRoute><ViewWorkouts /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;