const BASE_URL = 'http://localhost:5000';

const defaultOptions = {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
};

export async function loginUser(email, password) {
    const response = await fetch(`${BASE_URL}/api/login`, {
        method: 'POST',
        ...defaultOptions,
        body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Login failed');
    }
    return data;
}

export async function logoutUser() {
    const response = await fetch(`${BASE_URL}/api/logout`, {
        method: 'POST',
        ...defaultOptions,
    });
    if (!response.ok) {
        throw new Error('Logout failed');
    }
    return response.json();
}

export async function registerUser(firstname, lastname, email, password) {
    const response = await fetch(`${BASE_URL}/api/register`, {
        method: 'POST',
        ...defaultOptions,
        body: JSON.stringify({ firstname, lastname, email, password }),
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Registration failed');
    }
    return data;
}

export async function checkAuthStatus() {
    const response = await fetch(`${BASE_URL}/api/check-auth`, {
        method: 'GET',
        ...defaultOptions,
    });
    if (!response.ok) {
        throw new Error('Auth check failed');
    }
    return response.json();
}
