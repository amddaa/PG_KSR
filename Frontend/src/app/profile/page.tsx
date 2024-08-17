"use client";

import React, {useEffect} from 'react';
import {useRouter} from 'next/navigation';
import {useUser} from '@/context/user-context';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';

const ProfilePage = () => {
    const {isLoggedIn} = useUser();
    const router = useRouter();

    useEffect(() => {
        if (!isLoggedIn) {
            console.log('Redirecting to login...');
            router.push('/login');
        }
    }, [isLoggedIn, router]);

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
            <Card className="w-full max-w-md mx-auto bg-white shadow-lg rounded-lg">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold">Your Profile</CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                    <p className="text-gray-700 mb-4">Welcome to your profile page!</p>
                    <Button
                        onClick={() => router.push('/edit-profile')}
                        className="w-full bg-blue-500 text-white hover:bg-blue-600"
                    >
                        Edit Profile
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
};

export default ProfilePage;
