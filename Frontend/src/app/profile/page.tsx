"use client";

import React, {useEffect, useState} from 'react';
import {useRouter} from 'next/navigation';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {useUser} from "@/context/user-context";
import {getReservations} from "@/lib/reservations";
import {Reservation} from "@/lib/reservation-models";

const ProfilePage = () => {
    const {isLoggedIn, isLoading} = useUser();
    const [reservations, setReservations] = useState<Reservation[]>([]);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !isLoggedIn) {
            router.push('/login');
        }
    }, [isLoggedIn, isLoading, router]);

    useEffect(() => {
        if (isLoggedIn) {
            const fetchReservations = async () => {
                try {
                    const data = await getReservations();
                    setReservations(data);
                } catch (err) {
                    setError('Failed to fetch reservations.');
                }
            };

            fetchReservations();
        }
    }, [isLoggedIn]);


    if (isLoading) {
        return <p>Loading...</p>;
    }

    if (!isLoggedIn) {
        return <p>Redirecting to login...</p>;
    }

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
            <Card className="w-full max-w-md mx-auto bg-white shadow-lg rounded-lg mb-4">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold">Your Profile</CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                    <Button
                        onClick={() => router.push('/edit-profile')}
                        className="w-full bg-blue-500 text-white hover:bg-blue-600"
                    >
                        Edit Profile
                    </Button>
                </CardContent>
            </Card>

            <div className="w-full max-w-md mx-auto">
                {error && <p className="text-red-500 mb-4">{error}</p>}
                {reservations.length === 0 ? (
                    <p>No reservations found.</p>
                ) : (
                    reservations.map(reservation => (
                        <ReservationCard key={reservation.operation_id} reservation={reservation}/>
                    ))
                )}
            </div>
        </div>
    );
};

const ReservationCard = ({reservation}: { reservation: Reservation }) => {
    return (
        <Card className="w-full mb-4 bg-white shadow-lg rounded-lg">
            <CardHeader>
                <CardTitle className="text-xl font-bold">Reservation for: {reservation.train_number}</CardTitle>
            </CardHeader>
            <CardContent className="p-4">
                <p><strong>Reserved Seats:</strong> {reservation.reserved_seats}</p>
                <p><strong>Status:</strong> {reservation.is_successful ? 'Successful' : 'Failed'}</p>
                <p><strong>Notes:</strong> {reservation.message}</p>
            </CardContent>
        </Card>
    );
};

export default ProfilePage;
