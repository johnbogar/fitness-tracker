import React, { useEffect, useState } from 'react';

function StreakPage() {
  const [streak, setStreak] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('http://localhost:5000/api/streak', { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        if (data.error) setError(data.error);
        else setStreak(data);
      })
      .catch(() => setError('Failed to load streak data.'));
  }, []);

  return (
    <div className="streak-page">
      <h2>🔥 Workout Streak</h2>
      {error && <p className="error">{error}</p>}
      {streak && (
        <div className="streak-cards">
          <div className="streak-card">
            <h3>Current Streak</h3>
            <p className="streak-number">{streak.currentStreak}</p>
            <p>day{streak.currentStreak !== 1 ? 's' : ''} in a row</p>
          </div>
          <div className="streak-card">
            <h3>Longest Streak</h3>
            <p className="streak-number">{streak.longestStreak}</p>
            <p>day{streak.longestStreak !== 1 ? 's' : ''}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default StreakPage;