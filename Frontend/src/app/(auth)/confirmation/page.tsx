import React from 'react';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import Link from 'next/link';

const ConfirmationPage = () => {
    return (
        <Card className="mx-auto max-w-md mt-20">
            <CardHeader>
                <CardTitle className="text-2xl">Registration Successful!</CardTitle>
                <CardDescription className="mt-2">
                    Thank you for registering. Please check your email and click the confirmation link to activate your
                    account.
                </CardDescription>
            </CardHeader>
            <CardContent className="text-center mt-4">
                <Link href="/" passHref>
                    <Button>Go to Home</Button>
                </Link>
            </CardContent>
        </Card>
    );
};

export default ConfirmationPage;
