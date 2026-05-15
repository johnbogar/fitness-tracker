import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import EditUser from './EditUser';

const Header = () => {
  const { user, isAuthenticated, logout, checkAuth } = useAuth();
  const [showEditUser, setShowEditUser] = useState(false);
  const [showResetPassword, setShowResetPassword] = useState(false);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  function fetchUserData() {
    checkAuth();
  }

  async function handleResetPassword(e) {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const res = await fetch('http://localhost:5000/api/reset-password', {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          currentPassword,
          newPassword
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Failed to reset password');
      }

      setSuccess('Password updated successfully!');
      setCurrentPassword('');
      setNewPassword('');
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <header style={{
      backgroundColor: '#1f2937',
      padding: '1rem 2rem',
      borderBottom: '1px solid #374151'
    }}>
      <nav style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>

        <div style={{ display: 'flex', gap: '2rem' }}>
          {isAuthenticated && (
            <>
              <Link to="/" style={{ color: '#fff' }}>Home</Link>
              <Link to="/view_goals" style={{ color: '#fff' }}>View Goals</Link>
              <Link to="/view-workouts" style={{ color: '#fff' }}>View Workouts</Link>
            </>
          )}
        </div>

        {isAuthenticated && (
          <div style={{ display: 'flex', gap: '10px' }}>

            <button
              onClick={() => setShowEditUser(true)}
              style={{
                backgroundColor: 'transparent',
                color: '#e5e7eb',
                border: '1px solid #4b5563',
                padding: '6px 14px',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Edit Profile
            </button>

            <button
              onClick={() => setShowResetPassword(true)}
              style={{
                backgroundColor: 'transparent',
                color: '#e5e7eb',
                border: '1px solid #4b5563',
                padding: '6px 14px',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Reset Password
            </button>

            <button
              onClick={logout}
              style={{
                backgroundColor: '#ef4444',
                color: '#fff',
                padding: '6px 14px',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Logout
            </button>

          </div>
        )}

      </nav>
      {showEditUser && isAuthenticated && (
        <EditUser
          userId={user.id}
          firstname={user.firstname}
          lastname={user.lastname}
          email={user.email}
          onClose={() => setShowEditUser(false)}
          onUserUpdated={() => {
            fetchUserData();
            setShowEditUser(false);
          }}
        />
      )}

      {showResetPassword && isAuthenticated && (
        <div className="modal-overlay">
          <div className="modal">

            <h2 className="form-title">Reset Password</h2>

            {error && <p className="error-message">{error}</p>}
            {success && <p className="success-message">{success}</p>}

            <form onSubmit={handleResetPassword}>
              <label className="form-label">Current Password</label>
              <input
                type="password"
                className="form-input"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
              />

              <label className="form-label">New Password</label>
              <input
                type="password"
                className="form-input"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />

              <div className="form-buttons">
                <button type="submit" className="submit-btn">
                  Update
                </button>

                <button
                  type="button"
                  className="close-btn"
                  onClick={() => setShowResetPassword(false)}
                >
                  Close
                </button>
              </div>
            </form>

          </div>
        </div>
      )}

    </header>
  );
};

export default Header;
