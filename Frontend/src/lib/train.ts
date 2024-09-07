import {TrainSchedule} from "@/app/(trains)/train-models";

export const fetchTrainSchedules = async (): Promise<TrainSchedule[]> => {
    const response = await fetch('/api/trains/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (response.ok) {
        return await response.json();
    } else {
        throw new Error('Failed to fetch train schedules');
    }
};
