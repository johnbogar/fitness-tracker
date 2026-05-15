import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import '../styles/ViewWorkouts.css';

const ViewWorkouts = () => {
  const [workouts, setWorkouts] = useState([]);
  const [goals, setGoals] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({ date: '', notes: '', goalId: '' });
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    fetchWorkouts();
    fetchGoals();
  }, []);

  const fetchWorkouts = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/workouts', { credentials: 'include' });
      if (res.ok) setWorkouts(await res.json());
    } catch (err) {
      setError('Failed to fetch workouts');
    }
  };

  const fetchGoals = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/view_goals', { credentials: 'include' });
      if (res.ok) setGoals(await res.json());
    } catch (err) {
      console.error('Failed to fetch goals');
    }
  };

  const getGoalName = (goal_id) => {
    const goal = goals.find(g => g.id === goal_id);
    return goal ? goal.goalname : goal_id ? `Goal #${goal_id}` : 'No goal';
  };

  const handleEditClick = (workout) => {
    setEditingId(workout.id);
    setEditForm({
      date: workout.date,
      notes: workout.notes || '',
      goalId: workout.goal_id ?? ''
    });
  };

  const handleSaveEdit = async () => {
    setError('');
    try {
      const res = await axios.put(
        `http://localhost:5000/api/workout/${editingId}`,
        {
          date: editForm.date,
          notes: editForm.notes,
          goalId: editForm.goalId === '' ? null : parseInt(editForm.goalId)
        },
        { withCredentials: true }
      );
      setWorkouts(workouts.map(w => w.id === editingId ? res.data : w));
      setEditingId(null);
      setSuccessMsg('Workout updated successfully!');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update workout');
    }
  };

  const handleDelete = async () => {
    setError('');
    try {
      await axios.delete(`http://localhost:5000/api/workout/${confirmDeleteId}`, { withCredentials: true });
      setWorkouts(workouts.filter(w => w.id !== confirmDeleteId));
      setConfirmDeleteId(null);
      setSuccessMsg('Workout deleted successfully!');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete workout');
      setConfirmDeleteId(null);
    }
  };

  return (
    <div className="vw-page">
      <div className="vw-card">
        <h1 className="vw-title">My Workouts</h1>

        {successMsg && <div className="vw-success">{successMsg}</div>}
        {error && <div className="vw-error">{error}</div>}

        {workouts.length === 0 ? (
          <div className="vw-empty-state">
            <h3>No workouts yet</h3>
            <p>Head to <Link to="/log_workout">Log Workout</Link> to get started 💪</p>
          </div>
        ) : (
          <div className="vw-list">
            {workouts.map(w => (
              <div key={w.id} className="vw-item">
                {editingId === w.id ? (
                  /* ── Inline edit form ── */
                  <div className="vw-edit-form">
                    <div>
                      <label className="vw-form-label">Date</label>
                      <input
                        type="date"
                        className="vw-form-input"
                        value={editForm.date}
                        onChange={e => setEditForm({ ...editForm, date: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="vw-form-label">Goal</label>
                      <select
                        className="vw-form-select"
                        value={editForm.goalId}
                        onChange={e => setEditForm({ ...editForm, goalId: e.target.value })}
                      >
                        <option value="">— No goal —</option>
                        {goals.map(g => (
                          <option key={g.id} value={g.id}>{g.goalname}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="vw-form-label">Notes</label>
                      <textarea
                        className="vw-form-textarea"
                        value={editForm.notes}
                        onChange={e => setEditForm({ ...editForm, notes: e.target.value })}
                        rows="3"
                        placeholder="How did it go?"
                      />
                    </div>
                    <div className="vw-actions">
                      <button onClick={handleSaveEdit} className="btn-primary">Save</button>
                      <button onClick={() => setEditingId(null)} className="btn-secondary">Cancel</button>
                    </div>
                  </div>
                ) : (
                  /* ── Read-only card view ── */
                  <>
                    <div className="vw-meta">
                      <span className="vw-date">{w.date}</span>
                      <span className="vw-goal-badge">{getGoalName(w.goal_id)}</span>
                    </div>
                    {w.notes && <p className="vw-notes">{w.notes}</p>}
                    <p className="vw-created">Created: {w.created_at?.split(' ')[0]}</p>
                    <div className="vw-actions">
                      <button onClick={() => handleEditClick(w)} className="btn-primary">Edit</button>
                      <button onClick={() => setConfirmDeleteId(w.id)} className="btn-danger">Delete</button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Delete confirmation modal ── */}
      {confirmDeleteId && (
        <div className="modal-overlay" onClick={() => setConfirmDeleteId(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3 style={{ marginBottom: '8px', color: 'var(--text)' }}>Delete Workout?</h3>
            <p style={{ color: 'var(--subtext)', marginBottom: '20px' }}>
              This action cannot be undone.
            </p>
            <div className="vw-modal-actions">
              <button onClick={handleDelete} className="btn-danger">Yes, Delete</button>
              <button onClick={() => setConfirmDeleteId(null)} className="btn-secondary">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ViewWorkouts;
