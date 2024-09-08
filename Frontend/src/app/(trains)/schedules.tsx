"use client";

import {useEffect, useState} from "react";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table";
import {Button} from "@/components/ui/button";
import {TrainSchedule} from "@/app/(trains)/train-models";
import {fetchTrainSchedules} from "@/lib/trains";
import {checkReservationServiceHealth} from "@/lib/reservations";
import {Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle} from "@/components/ui/dialog";

const TrainSchedules = () => {
    const [schedules, setSchedules] = useState<TrainSchedule[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isReservationServiceUp, setIsReservationServiceUp] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedTrain, setSelectedTrain] = useState<TrainSchedule | null>(null);
    const [seats, setSeats] = useState<number>(1); // Stan do przechowywania liczby miejsc

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

        checkReservationServiceHealth(setIsReservationServiceUp);
        getSchedules();
    }, []);

    const openModal = (schedule: TrainSchedule) => {
        setSelectedTrain(schedule);
        setSeats(1);
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setSelectedTrain(null);
    };

    return (
        <div className="container mx-auto">
            <h1 className="text-2xl font-bold my-4">Train Schedules</h1>

            {loading ? (
                <p>Loading...</p>
            ) : error ? (
                <p>{error}</p>
            ) : (
                <>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Train</TableHead>
                                <TableHead>Departure Time</TableHead>
                                <TableHead>Arrival Time</TableHead>
                                <TableHead>Action</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {schedules.map((schedule, index) => (
                                <TableRow key={index}>
                                    <TableCell>{schedule.train_number}</TableCell>
                                    <TableCell>{new Date(schedule.departure_time).toLocaleString()}</TableCell>
                                    <TableCell>{new Date(schedule.arrival_time).toLocaleString()}</TableCell>
                                    <TableCell>
                                        <Button
                                            variant={isReservationServiceUp ? "default" : "ghost"}
                                            disabled={!isReservationServiceUp}
                                            onClick={() => openModal(schedule)}
                                        >
                                            Reserve
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>

                    {isModalOpen && selectedTrain && (
                        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Reserve Train {selectedTrain.train_number}</DialogTitle>
                                </DialogHeader>
                                <p>Are you sure you want to reserve this train?</p>
                                <div className="mt-4">
                                    <label htmlFor="seats" className="block text-sm font-medium text-gray-700">
                                        Number of Seats
                                    </label>
                                    <select
                                        id="seats"
                                        value={seats}
                                        onChange={(e) => setSeats(parseInt(e.target.value))}
                                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                    >
                                        {Array.from({length: 10}, (_, num) => (
                                            <option key={num + 1} value={num + 1}>
                                                {num + 1}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <DialogFooter>
                                    <Button variant="secondary" onClick={closeModal}>
                                        Cancel
                                    </Button>
                                    <Button
                                        variant="default"
                                        onClick={() => {
                                            closeModal();
                                        }}
                                    >
                                        Confirm Reservation
                                    </Button>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    )}
                </>
            )}
        </div>
    );
};

export default TrainSchedules;
