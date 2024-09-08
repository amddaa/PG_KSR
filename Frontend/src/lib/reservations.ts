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