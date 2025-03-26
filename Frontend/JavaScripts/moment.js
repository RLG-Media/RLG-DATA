// moment.js - Custom Date-Time Utility for RLG Data and RLG Fans

const Moment = (() => {
    const ONE_SECOND = 1000;
    const ONE_MINUTE = 60 * ONE_SECOND;
    const ONE_HOUR = 60 * ONE_MINUTE;
    const ONE_DAY = 24 * ONE_HOUR;

    const months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];

    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    const pad = (value, length = 2) => String(value).padStart(length, "0");

    // Parse and format dates
    const format = (date, formatStr = "YYYY-MM-DD HH:mm:ss") => {
        const d = new Date(date);
        if (isNaN(d)) throw new Error("Invalid date");

        return formatStr
            .replace("YYYY", d.getFullYear())
            .replace("MM", pad(d.getMonth() + 1))
            .replace("DD", pad(d.getDate()))
            .replace("HH", pad(d.getHours()))
            .replace("mm", pad(d.getMinutes()))
            .replace("ss", pad(d.getSeconds()));
    };

    const fromNow = (date) => {
        const now = Date.now();
        const inputDate = new Date(date).getTime();
        const diff = now - inputDate;

        if (diff < ONE_MINUTE) return `${Math.floor(diff / ONE_SECOND)} seconds ago`;
        if (diff < ONE_HOUR) return `${Math.floor(diff / ONE_MINUTE)} minutes ago`;
        if (diff < ONE_DAY) return `${Math.floor(diff / ONE_HOUR)} hours ago`;
        return `${Math.floor(diff / ONE_DAY)} days ago`;
    };

    const add = (date, amount, unit) => {
        const d = new Date(date);
        if (isNaN(d)) throw new Error("Invalid date");

        switch (unit) {
            case "seconds":
                d.setSeconds(d.getSeconds() + amount);
                break;
            case "minutes":
                d.setMinutes(d.getMinutes() + amount);
                break;
            case "hours":
                d.setHours(d.getHours() + amount);
                break;
            case "days":
                d.setDate(d.getDate() + amount);
                break;
            case "months":
                d.setMonth(d.getMonth() + amount);
                break;
            case "years":
                d.setFullYear(d.getFullYear() + amount);
                break;
            default:
                throw new Error("Invalid unit for date addition");
        }

        return d;
    };

    const difference = (date1, date2, unit = "milliseconds") => {
        const d1 = new Date(date1);
        const d2 = new Date(date2);

        if (isNaN(d1) || isNaN(d2)) throw new Error("Invalid date");

        const diff = d2 - d1;

        switch (unit) {
            case "seconds":
                return Math.floor(diff / ONE_SECOND);
            case "minutes":
                return Math.floor(diff / ONE_MINUTE);
            case "hours":
                return Math.floor(diff / ONE_HOUR);
            case "days":
                return Math.floor(diff / ONE_DAY);
            default:
                return diff;
        }
    };

    const getDayOfWeek = (date) => {
        const d = new Date(date);
        if (isNaN(d)) throw new Error("Invalid date");

        return days[d.getDay()];
    };

    const getMonthName = (date) => {
        const d = new Date(date);
        if (isNaN(d)) throw new Error("Invalid date");

        return months[d.getMonth()];
    };

    // Public API
    return {
        format,
        fromNow,
        add,
        difference,
        getDayOfWeek,
        getMonthName
    };
})();

// Example usage
console.log(Moment.format(new Date(), "YYYY-MM-DD HH:mm:ss")); // e.g., 2025-01-24 14:30:00
console.log(Moment.fromNow("2025-01-23T10:00:00")); // e.g., 1 day ago
console.log(Moment.add(new Date(), 10, "days")); // Add 10 days to the current date
console.log(Moment.difference("2025-01-01", "2025-01-24", "days")); // Difference in days
console.log(Moment.getDayOfWeek("2025-01-24")); // e.g., Friday
console.log(Moment.getMonthName("2025-01-24")); // e.g., January
