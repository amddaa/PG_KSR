export type Reservation = {
    train_number: string;
    arrival_time: string;
    reserved_seats: number;
    operation_id: string;
    is_finished: boolean;
    is_successful: boolean;
    message: string;
};