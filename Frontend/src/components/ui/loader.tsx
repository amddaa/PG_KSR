import {cn} from "@/lib/utils";

export const Loader = () => {
    return (
        <div className={cn("flex justify-center items-center h-64")}>
            <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500"></div>
        </div>
    );
};
