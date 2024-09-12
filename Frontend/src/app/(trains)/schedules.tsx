"use client";

import {useEffect, useState} from "react";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table";
import {Button} from "@/components/ui/button";
import {fetchTrainSchedules} from "@/lib/trains";
import {
    checkReservationServiceHealth,
    checkReservationStatus,
    getStreamVersion,
    makeReservation
} from "@/lib/reservations";
import {Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle} from "@/components/ui/dialog";
import {useUser} from "@/context/user-context";
import {useRouter} from "next/navigation";
import {TrainSchedule} from "@/lib/train-models";
import {Loader} from "@/components/ui/loader";

const TrainSchedules = () => {
    const [schedules, setSchedules] = useState<TrainSchedule[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isReservationServiceUp, setIsReservationServiceUp] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);
    const [selectedTrain, setSelectedTrain] = useState<TrainSchedule | null>(null);
    const [seats, setSeats] = useState<number>(1);
    const [version, setVersion] = useState<string>('');
    const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
    const [reservationStatus, setReservationStatus] = useState('');
    const [loadingStatus, setLoadingStatus] = useState(false);
    const [pollingTimeout, setPollingTimeout] = useState<NodeJS.Timeout | null>(null);
    const {isLoggedIn} = useUser();
    const router = useRouter();

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

        const fetchVersion = async () => {
            try {
                const version = await getStreamVersion();
                setVersion(version);
            } catch (err) {
                setError("Couldn't fetch version");
            }
        };

        checkReservationServiceHealth(setIsReservationServiceUp);
        getSchedules();
        fetchVersion();
    }, []);

    const openModal = (schedule: TrainSchedule) => {
        if (!isLoggedIn) {
            router.push('/login');
        } else {
            setSelectedTrain(schedule);
            setSeats(1);
            setIsModalOpen(true);
        }
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setSelectedTrain(null);
    };

    const handleReservation = async () => {
        if (selectedTrain) {
            try {
                const result = await makeReservation(selectedTrain, seats, version);
                if (result.operation_id) {
                    if (pollingTimeout) {
                        clearTimeout(pollingTimeout);
                    }

                    const startTime = Date.now();
                    const timeoutDuration = 60000;

                    setPollingInterval(setInterval(async () => {
                        const elapsedTime = Date.now() - startTime;
                        if (elapsedTime >= timeoutDuration) {
                            setReservationStatus("Checking reservation status took too long. Please try again.");
                            clearInterval(pollingInterval!);
                            setLoadingStatus(false);
                            return;
                        }

                        try {
                            const status = await checkReservationStatus(result.operation_id);
                            const {
                                is_finished,
                                is_successful,
                                message
                            } = status;
                            setReservationStatus(message);


                            if (is_finished) {
                                clearInterval(pollingInterval!);
                                setPollingInterval(null);
                                setLoadingStatus(false);
                                if (is_successful) {
                                    // Handle successful reservation
                                } else {
                                    // Handle unsuccessful reservation
                                }
                            }
                        } catch (error) {
                            console.error("Failed to fetch reservation status:", error);
                            clearInterval(pollingInterval!);
                            setReservationStatus("Failed to check reservation status.");
                            setLoadingStatus(false);
                        }
                    }, 5000));

                    setIsStatusModalOpen(true);
                    setLoadingStatus(true);
                }
            } catch (error) {
                alert("An error occurred while making the reservation.");
            } finally {
                closeModal();
            }
        }
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

                    <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Reserve Train {selectedTrain?.train_number}</DialogTitle>
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
                                    onClick={handleReservation}
                                >
                                    Confirm Reservation
                                </Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>

                    <Dialog open={isStatusModalOpen} onOpenChange={() => setIsStatusModalOpen(false)}>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Reservation Status</DialogTitle>
                            </DialogHeader>
                            <div className="flex flex-col items-center">
                                {loadingStatus ? (
                                    <Loader/>
                                ) : (
                                    <p>{reservationStatus ? reservationStatus : "Unknown"}</p>
                                )}
                            </div>
                            <DialogFooter>
                                <Button variant="secondary" onClick={() => setIsStatusModalOpen(false)}>
                                    Close
                                </Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </>
            )}
        </div>
    );
};

export default TrainSchedules;
