import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';



const DashboardPage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/dashboard', {
          withCredentials: true
        });
        setData(response.data);
        setLoading(false);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load dashboard');
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#fff' }}>
        Loading dashboard...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#ff6b6b' }}>
        Error: {error}
      </div>
    );
  }

  const cardStyle = {
    background: '#1e2a3a',
    borderRadius: '12px',
    padding: '1.5rem',
    textAlign: 'center',
    flex: '1',
    minWidth: '140px',
  };

  const sectionStyle = {
    background: '#1e2a3a',
    borderRadius: '12px',
    padding: '1.5rem',
    marginBottom: '1.5rem',
  };

  const hasWorkouts = data?.totalWorkouts > 0;
  const goalProgress = data.goalProgress || [];
  const mostActiveGoal = goalProgress.length > 0 ? goalProgress[0] : null;

  return (
    <div style={{ padding: '2rem', color: '#fff', maxWidth: '1100px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '1.5rem' }}>Dashboard</h1>

      {/* ── Stats Row ── */}
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
        <div style={cardStyle}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4fc3f7' }}>
            {data.totalWorkouts}
          </div>
          <div style={{ color: '#9ca3af', marginTop: '0.25rem' }}>Total Workouts</div>
        </div>

        <div style={cardStyle}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4fc3f7' }}>
            {data.activeGoalsCount}
          </div>
          <div style={{ color: '#9ca3af', marginTop: '0.25rem' }}>Active Goals</div>
        </div>

        <div style={{ ...cardStyle, borderLeft: '3px solid #f97316' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>🔥</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f97316' }}>
            {data.currentStreak ?? 0}
          </div>
          <div style={{ color: '#9ca3af', marginTop: '0.25rem' }}>
            Day{data.currentStreak !== 1 ? 's' : ''} Streak
          </div>
        </div>

        <div style={{ ...cardStyle, borderLeft: '3px solid #a78bfa' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>🏅</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#a78bfa' }}>
            {data.longestStreak ?? 0}
          </div>
          <div style={{ color: '#9ca3af', marginTop: '0.25rem' }}>Longest Streak</div>
        </div>
      </div>


      {/* ── Goal Progress Rings ── */}
      {goalProgress.length > 0 ? (
        <div style={{ backgroundColor: '#1f2937', padding: '1.5rem', borderRadius: '8px', marginBottom: '2rem' }}>
          <h2 style={{ color: '#fff', marginBottom: '1.5rem' }}>Goal Progress</h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '2rem'
          }}>
            {goalProgress.map(goal => (
              <div key={goal.id} style={{ textAlign: 'center' }}>
                <div style={{ width: '140px', margin: '0 auto 1rem' }}>
                  <CircularProgressbar
                    value={goal.progressPct}
                    text={`${Math.round(goal.progressPct)}%`}
                    styles={buildStyles({
                      pathColor: goal.progressPct >= 100 ? '#22c55e' : '#3b82f6',
                      textColor: '#ffffff',
                      trailColor: '#374151',
                      textSize: '18px',
                      pathTransitionDuration: 0.8,
                    })}
                  />
                </div>

                <div style={{ color: '#ffffff', fontWeight: '600', marginBottom: '4px', fontSize: '0.95rem' }}>
                  {goal.goalName}
                </div>

                <div style={{ color: '#9ca3af', fontSize: '0.82rem' }}>
                  {goal.workoutCount} of {goal.estimatedWorkouts} workouts
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div style={{ backgroundColor: '#1f2937', padding: '2.5rem', borderRadius: '8px', textAlign: 'center', marginBottom: '2rem' }}>
          <p style={{ color: '#9ca3af', fontSize: '1rem', margin: 0 }}>
            No goals yet.{' '}
            <Link to="/view_goals" style={{ color: '#3b82f6', textDecoration: 'none', fontWeight: '600' }}>
              Add a goal
            </Link>
          </p>
        </div>
      )}

      {/* ── Recent Workouts ── */}
      <div style={sectionStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 style={{ color: '#9ca3af', fontSize: '1rem', textTransform: 'uppercase', letterSpacing: '0.05em', margin: 0 }}>
            Recent Workouts
          </h2>

          <Link to="/log_workout" style={{ color: '#4fc3f7', fontSize: '0.875rem', textDecoration: 'none' }}>
            + Log Workout
          </Link>
        </div>

        {data.recentWorkouts && data.recentWorkouts.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #374151' }}>
                <th style={{ padding: '0.75rem', textAlign: 'left', color: '#9ca3af' }}>Date</th>
                <th style={{ padding: '0.75rem', textAlign: 'left', color: '#9ca3af' }}>Goal</th>
                <th style={{ padding: '0.75rem', textAlign: 'left', color: '#9ca3af' }}>Notes</th>
              </tr>
            </thead>

            <tbody>
              {data.recentWorkouts.map((workout, idx) => (
                <tr
                  key={workout.id}
                  style={{
                    borderBottom: '1px solid #374151',
                    backgroundColor: idx % 2 === 0 ? '#0f172a' : 'transparent'
                  }}
                >
                  <td style={{ padding: '0.75rem', color: '#fff' }}>{workout.date}</td>
                  <td style={{ padding: '0.75rem', color: '#fff' }}>{workout.goalName || 'No goal'}</td>
                  <td style={{ padding: '0.75rem', color: '#9ca3af' }}>{workout.notes || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#6b7280' }}>No workouts logged yet.</p>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;