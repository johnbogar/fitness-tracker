import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, logoutUser, checkAuthStatus } from '../utils/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkAuth();
    }, []);

    async function checkAuth() {
        try {
            const data = await checkAuthStatus();
            if (data.authenticated) {
                setIsAuthenticated(true);
                setUser(data.user);
            } else {
                setIsAuthenticated(false);
                setUser(null);
            }
        } catch {
            setIsAuthenticated(false);
            setUser(null);
        } finally {
            setLoading(false);
        }
    }

    async function login(email, password) {
        const data = await loginUser(email, password);
        setIsAuthenticated(true);
        setUser(data.user);
    }

    async function logout() {
        try {
            await logoutUser();
        } finally {
            setIsAuthenticated(false);
            setUser(null);
        }
    }

    const value = { isAuthenticated, user, loading, login, logout, checkAuth };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
