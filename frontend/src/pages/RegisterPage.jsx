import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../utils/api';

export default function RegisterPage() {
    /*
    Component for registration page
    */
    const navigate = useNavigate();

    const [firstname, setFirstname] = useState('');
    const [lastname, setLastname] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [submitting, setSubmitting] = useState(false);

    async function handleSubmit(e) {
        e.preventDefault();
        setError('');

        // Client-side validation
        if (!firstname || !lastname || !email || !password) {
            setError('All fields are required');
            return;
        }
        if (!email.includes('@') || !email.includes('.')) {
            setError('Invalid email format');
            return;
        }

        setSubmitting(true);
        try {
            await registerUser(firstname, lastname, email, password);
            navigate('/login', { state: { message: 'Account created! Please sign in.' } });
        } catch (err) {
            setError(err.message);
        } finally {
            setSubmitting(false);
        }
    }

    return (
        <div style={styles.page}>
            <div style={styles.card}>
                <h1 style={styles.title}>Create Account</h1>

                {error && (
                    <p style={styles.error}>{error}</p>
                )}

                <form onSubmit={handleSubmit} style={styles.form}>
                    <label style={styles.label}>First Name</label>
                    <input
                        type="text"
                        value={firstname}
                        onChange={e => setFirstname(e.target.value)}
                        required
                        style={styles.input}
                        autoComplete="given-name"
                    />

                    <label style={styles.label}>Last Name</label>
                    <input
                        type="text"
                        value={lastname}
                        onChange={e => setLastname(e.target.value)}
                        required
                        style={styles.input}
                        autoComplete="family-name"
                    />

                    <label style={styles.label}>Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        required
                        style={styles.input}
                        autoComplete="email"
                    />

                    <label style={styles.label}>Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        required
                        style={styles.input}
                        autoComplete="new-password"
                    />

                    <button type="submit" disabled={submitting} style={styles.button}>
                        {submitting ? 'Creating account...' : 'Create Account'}
                    </button>
                </form>

                <p style={styles.footer}>
                    Already have an account?{' '}
                    <span style={styles.link} onClick={() => navigate('/login')}>
                        Sign in
                    </span>
                </p>
            </div>
        </div>
    );
}

const styles = {
    page: {
        minHeight: '100vh',
        backgroundColor: '#111827',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px 20px',
    },
    card: {
        width: '100%',
        maxWidth: '400px',
        backgroundColor: '#1f2933',
        borderRadius: '10px',
        padding: '40px',
    },
    title: {
        fontSize: '28px',
        fontWeight: '600',
        color: '#ffffff',
        marginTop: '0',
        marginBottom: '24px',
        textAlign: 'center',
    },
    error: {
        color: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        border: '1px solid #ef4444',
        borderRadius: '6px',
        padding: '10px 14px',
        marginBottom: '16px',
        fontSize: '14px',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
    },
    label: {
        fontSize: '14px',
        color: '#9ca3af',
    },
    input: {
        padding: '10px 12px',
        borderRadius: '6px',
        border: '1px solid #374151',
        backgroundColor: '#111827',
        color: '#ffffff',
        fontSize: '16px',
        outline: 'none',
    },
    button: {
        marginTop: '8px',
        padding: '10px 18px',
        backgroundColor: '#60a5fa',
        color: '#ffffff',
        border: 'none',
        borderRadius: '8px',
        fontSize: '16px',
        fontWeight: '500',
        cursor: 'pointer',
    },
    footer: {
        marginTop: '20px',
        textAlign: 'center',
        fontSize: '14px',
        color: '#9ca3af',
    },
    link: {
        color: '#60a5fa',
        cursor: 'pointer',
        fontWeight: '500',
    },
};
