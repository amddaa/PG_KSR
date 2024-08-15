'use client';

import React, {useEffect, useState} from 'react';
import {Button} from '@/components/ui/button';
import {Card, CardContent, CardFooter, CardHeader, CardTitle} from '@/components/ui/card';

const VerifyEmailComponent = ({uidb64, token}: { uidb64: string; token: string; }) => {
    const [message, setMessage] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const verifyEmail = async () => {
            try {
                const response = await fetch(`/api/auth/verify-email/${uidb64}/${token}/`, {
                    method: 'GET',
                });
                const data = await response.json();

                if (response.ok) {
                    setMessage(data.detail || 'Email verified successfully!');
                } else {
                    setMessage(data.detail || 'Invalid verification link');
                }
            } catch (error) {
                setMessage('Verification failed. Please try again.');
            } finally {
                setLoading(false);
            }
        };

        void verifyEmail();
    }, [uidb64, token]);

    return (
        <div className="flex items-center justify-center min-h-screen">
            <Card className="w-96">
                <CardHeader>
                    <CardTitle>Email Verification</CardTitle>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <p>Verifying your email...</p>
                    ) : (
                        <p>{message}</p>
                    )}
                </CardContent>
                <CardFooter>
                    <Button onClick={() => window.location.href = '/login'}>Go to Login</Button>
                </CardFooter>
            </Card>
        </div>
    );
};

const VerifyEmailPage = ({params}: { params: { uidb64: string; token: string } }) => {
    return (
        <React.Suspense fallback={<div>Loading...</div>}>
            <VerifyEmailComponent uidb64={params.uidb64} token={params.token}/>
        </React.Suspense>
    );
};

export default VerifyEmailPage;
