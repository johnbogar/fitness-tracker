import React, { useState, useEffect } from 'react';
import axios from 'axios';
import LogWorkout from '../components/LogWorkout';
import '../styles/workout.css';

/**
 * Page that displays the user's past workouts and a button to log a new one.
 */
export default function LogWorkoutPage() {
  const [workouts, setWorkouts] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState('');

  const fetchWorkouts = () => {
    axios
      .get('http://localhost:5000/api/workouts', { withCredentials: true })
      .then((res) => setWorkouts(res.data))
      .catch((err) => setError(err.response?.data?.error || 'Failed to load workouts'));
  };

  useEffect(() => {
    fetchWorkouts();
  }, []);

  return (
    <div className="workout-page">
      <div className="workout-card">
        <h1 className="workout-title">Your Workouts</h1>

        {error && <p className="error-message">{error}</p>}

        <div className="workout-list">
          {workouts.length === 0 ? (
            <div className="empty-state">
              <h3>No workouts logged yet</h3>
              <p>Click "Log a Workout" to get started 💪</p>
            </div>
          ) : (
            workouts.map((w) => (
              <div key={w.id} className="workout-item">
                <div className="workout-meta">
                  <span className="workout-date">{w.date}</span>
                  {w.goal_id && (
                    <span className="workout-goal-badge">Goal #{w.goal_id}</span>
                  )}
                </div>
                {w.notes && <p className="workout-notes">{w.notes}</p>}
              </div>
            ))
          )}
        </div>

        <button className="log-workout-btn" onClick={() => setShowForm(true)}>
          Log a Workout
        </button>
      </div>

      {showForm && (
        <LogWorkout
          onClose={() => setShowForm(false)}
          onWorkoutLogged={() => {
            fetchWorkouts();
            setTimeout(() => setShowForm(false), 800);
          }}
        />
      )}
    </div>
  );
}