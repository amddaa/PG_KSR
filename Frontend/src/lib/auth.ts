export const loginUser = async (credentials: { email: string; username: string; password: string }) => {
    const response = await fetch('/api/auth/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
        credentials: 'include',
    });

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('accessToken', data.access);
        return {ok: true, data};
    } else {
        const errorData = await response.json();
        return {ok: false, error: errorData.error || 'Login failed'};
    }
};

export const refreshAccessToken = async () => {
    const response = await fetch('/api/auth/token/refresh/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
    });

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('accessToken', data.access);
        return true;
    } else {
        throw new Error('Failed to refresh token');
    }
};

export const logoutUser = async () => {
    if (typeof window !== 'undefined') {
        try {
            await fetch('/api/auth/token/blacklist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
            });
            localStorage.removeItem('accessToken');
        } catch (error) {
            console.error('Error logging out:', error);
        }
    }
};

