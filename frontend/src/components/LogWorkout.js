import { useState, useEffect } from 'react';

/**
 * Modal form component for logging a new workout.
 *
 * Props:
 *   onClose         – callback to close the modal
 *   onWorkoutLogged – callback fired after a successful submission
 */
function LogWorkout({ onClose, onWorkoutLogged }) {
  const [goalId, setGoalId] = useState('');
  const [date, setDate] = useState('');
  const [notes, setNotes] = useState('');
  const [goals, setGoals] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Fetch user's goals so they can optionally link the workout to one
  useEffect(() => {
    fetch('http://localhost:5000/api/view_goals', { credentials: 'include' })
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data)) setGoals(data);
      })
      .catch(() => {
        // Goals are optional — silently ignore if they can't be loaded
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Client-side validation
    if (notes.length > 1000) {
      setError('Notes must be under 1000 characters');
      return;
    }

    const payload = {
      goalId: goalId !== '' ? parseInt(goalId, 10) : null,
      date: date || undefined,
      notes,
    };

    try {
      const response = await fetch('http://localhost:5000/api/log_workout', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to log workout');
      }

      setSuccess('Workout logged successfully!');
      setError('');
      if (onWorkoutLogged) onWorkoutLogged(data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        {success ? (
          <>
            <p className="success-message">{success}</p>
            <button className="close-btn" onClick={onClose}>
              Close
            </button>
          </>
        ) : (
          <form className="add-goal-form" onSubmit={handleSubmit}>
            <h2 className="form-title">Log a Workout</h2>

            {error && <p className="error-message">{error}</p>}

            <label htmlFor="lw-goal" className="form-label">
              Goal (optional)
            </label>
            <select
              id="lw-goal"
              className="form-input"
              value={goalId}
              onChange={(e) => setGoalId(e.target.value)}
            >
              <option value="">— No goal —</option>
              {goals.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.goalname}
                </option>
              ))}
            </select>

            <label htmlFor="lw-date" className="form-label">
              Date
            </label>
            <input
              id="lw-date"
              className="form-input"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />

            <label htmlFor="lw-notes" className="form-label">
              Notes
            </label>
            <textarea
              id="lw-notes"
              className="form-text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="How did it go?"
              rows={4}
            />

            <div className="form-buttons">
              <button type="submit" className="submit-btn">
                Submit
              </button>
              <button type="button" className="close-btn" onClick={onClose}>
                Close
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default LogWorkout;