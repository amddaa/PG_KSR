import React, {createContext, ReactNode, useContext, useEffect, useState} from 'react';
import {loginUser, logoutUser, refreshAccessToken} from "@/lib/auth";
import {useRouter} from 'next/navigation';

interface UserContextType {
    isLoggedIn: boolean;
    login: (credentials: { email: string; username: string; password: string }) => Promise<{
        ok: boolean;
        error?: string
    }>;
    logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: ReactNode }> = ({children}) => {
    const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
    const router = useRouter();

    useEffect(() => {
        const checkLoginStatus = async () => {
            try {
                const success = await refreshAccessToken();
                setIsLoggedIn(success);
            } catch (error) {
                console.error('Error refreshing access token:', error);
                setIsLoggedIn(false);
            }
        };

        void checkLoginStatus();
    }, []);

    const login = async (credentials: { email: string; username: string; password: string }) => {
        try {
            const response = await loginUser(credentials);
            if (response.ok) {
                setIsLoggedIn(true);
                return {ok: true};
            } else {
                return {ok: false, error: response.error};
            }
        } catch (error) {
            console.error('Error logging in:', error);
            return {ok: false, error: 'An unexpected error occurred'};
        }
    };

    const logout = async () => {
        try {
            await logoutUser();
            setIsLoggedIn(false);
            router.push('/login');
        } catch (error) {
            console.error('Error logging out:', error);
        }
    };

    useEffect(() => {
        if (isLoggedIn) {
            router.push('/profile');
        }
    }, [isLoggedIn, router]);

    return (
        <UserContext.Provider value={{isLoggedIn, login, logout}}>
            {children}
        </UserContext.Provider>
    );
};

export const useUser = () => {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error('useUser must be used within a UserProvider');
    }
    return context;
};
