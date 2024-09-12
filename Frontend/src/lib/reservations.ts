import {TrainSchedule} from "@/lib/train-models";

export const checkReservationServiceHealth = async (setIsReservationServiceUp: React.Dispatch<React.SetStateAction<boolean>>) => {
    try {
        const res = await fetch('/api/reservations/health/');
        if (res.ok) {
            setIsReservationServiceUp(true);
        }
    } catch (err) {
        console.error("Reservation service health check failed");
    }
};

export const getStreamVersion = async (): Promise<string> => {
    const response = await fetch('/api/reservations/version/');
    if (!response.ok) {
        throw new Error("Couldn't fetch stream version");
    }
    const data = await response.json();
    return data.version;
};

export const makeReservation = async (train: TrainSchedule, seats: number, version: string): Promise<any> => {
    const accessToken = localStorage.getItem('accessToken');
    const response = await fetch('/api/reservations/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            train_number: train.train_number,
            departure_time: train.departure_time,
            arrival_time: train.arrival_time,
            reserved_seats: seats.toString(),
            version: version
        })
    });

    if (!response.ok && response.status !== 202) {
        throw new Error("Reservation failed");
    }

    return response.json();
};

export const checkReservationStatus = async (operationId: string) => {
    const accessToken = localStorage.getItem('accessToken');
    const response = await fetch('/api/reservations/status/${operationId}', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
        },
    });

    if (!response.ok) {
        throw new Error("Failed to fetch reservation status");
    }
    return response.json();
};