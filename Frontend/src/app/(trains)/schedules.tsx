"use client";

import {useEffect, useState} from 'react';
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table";
import {fetchTrainSchedules} from "@/lib/train";
import {TrainSchedule} from "@/app/(trains)/train-models";


const TrainSchedules = () => {
    const [schedules, setSchedules] = useState<TrainSchedule[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const getSchedules = async () => {
            try {
                const data = await fetchTrainSchedules();
                setSchedules(data);
            } catch (err) {
                setError("Couldn't load train schedules");
            } finally {
                setLoading(false);
            }
        };

        getSchedules();
    }, []);

    return (
        <div className="container mx-auto">
            <h1 className="text-2xl font-bold my-4">Train Schedules</h1>

            {loading ? (
                <p>Loading...</p>
            ) : error ? (
                <p>{error}</p>
            ) : (
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Train Number</TableHead>
                            <TableHead>Departure Time</TableHead>
                            <TableHead>Arrival Time</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {schedules.map((schedule, index) => (
                            <TableRow key={index}>
                                <TableCell>{schedule.train_number}</TableCell>
                                <TableCell>{new Date(schedule.departure_time).toLocaleString()}</TableCell>
                                <TableCell>{new Date(schedule.arrival_time).toLocaleString()}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            )}
        </div>
    );
};

export default TrainSchedules;
