import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LogoutButton() {
    const { logout } = useAuth();
    const navigate = useNavigate();

    async function handleLogout() {
        try {
            await logout();
        } finally {
            navigate('/login');
        }
    }

    return (
        <button onClick={handleLogout} style={styles.button}>
            Logout
        </button>
    );
}

const styles = {
    button: {
        backgroundColor: 'transparent',
        color: '#e5e7eb',
        border: '1px solid #4b5563',
        padding: '6px 14px',
        borderRadius: '6px',
        fontSize: '14px',
        fontWeight: '500',
        cursor: 'pointer',
    },
};
