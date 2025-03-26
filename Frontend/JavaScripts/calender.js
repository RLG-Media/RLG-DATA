// calendar.js - Handles the interactive calendar for scheduling and event management

document.addEventListener("DOMContentLoaded", () => {
    initializeCalendar();
    setupEventListeners();
    console.log("Calendar.js loaded successfully!");
});

// Global Variables
const calendarEl = document.getElementById("calendar"); // Calendar container
const eventApiUrl = "/api/events"; // Endpoint to fetch and manage events

let calendar; // FullCalendar instance

// Initialize Calendar
function initializeCalendar() {
    if (!calendarEl) {
        console.warn("Calendar element not found.");
        return;
    }

    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        headerToolbar: {
            start: "prev,next today", // Buttons for navigation
            center: "title",         // Calendar title
            end: "dayGridMonth,timeGridWeek,timeGridDay,listWeek" // View toggles
        },
        selectable: true,
        editable: true,
        eventClick: handleEventClick,
        dateClick: handleDateClick,
        events: fetchEvents,
        eventDrop: handleEventDrop,
        eventResize: handleEventResize,
        loading: toggleLoadingState
    });

    calendar.render();
}

// Fetch Events from API
function fetchEvents(fetchInfo, successCallback, failureCallback) {
    fetch(eventApiUrl)
        .then((response) => response.json())
        .then((data) => {
            if (data && Array.isArray(data.events)) {
                successCallback(data.events);
            } else {
                console.error("Invalid events data format.");
                failureCallback("Error fetching events.");
            }
        })
        .catch((error) => {
            console.error("Error fetching events:", error);
            failureCallback("Failed to load events. Please try again.");
        });
}

// Handle Date Click (Adding New Event)
function handleDateClick(info) {
    const eventTitle = prompt("Enter event title:");
    if (eventTitle) {
        const newEvent = {
            title: eventTitle,
            start: info.dateStr,
            allDay: true
        };

        // Add event to calendar and API
        calendar.addEvent(newEvent);
        saveEventToApi(newEvent);
    }
}

// Handle Event Click (Viewing/Editing Event)
function handleEventClick(info) {
    const { title, id } = info.event;

    const options = prompt(`Edit event title (Leave empty to delete):`, title);
    if (options === null) {
        return; // User canceled
    }

    if (options.trim() === "") {
        // Delete the event
        info.event.remove();
        deleteEventFromApi(id);
    } else {
        // Update the event
        info.event.setProp("title", options.trim());
        updateEventInApi(id, { title: options.trim() });
    }
}

// Handle Event Drag/Drop
function handleEventDrop(info) {
    const updatedEvent = {
        id: info.event.id,
        start: info.event.startStr,
        end: info.event.endStr
    };
    updateEventInApi(info.event.id, updatedEvent);
}

// Handle Event Resize
function handleEventResize(info) {
    const resizedEvent = {
        id: info.event.id,
        start: info.event.startStr,
        end: info.event.endStr
    };
    updateEventInApi(info.event.id, resizedEvent);
}

// Save Event to API
function saveEventToApi(event) {
    fetch(eventApiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(event)
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to save event.");
            }
            return response.json();
        })
        .then((data) => {
            console.log("Event saved successfully:", data);
        })
        .catch((error) => {
            console.error("Error saving event:", error);
            alert("Failed to save event. Please try again.");
        });
}

// Update Event in API
function updateEventInApi(eventId, updatedData) {
    fetch(`${eventApiUrl}/${eventId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedData)
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to update event.");
            }
            return response.json();
        })
        .then((data) => {
            console.log("Event updated successfully:", data);
        })
        .catch((error) => {
            console.error("Error updating event:", error);
            alert("Failed to update event. Please try again.");
        });
}

// Delete Event from API
function deleteEventFromApi(eventId) {
    fetch(`${eventApiUrl}/${eventId}`, { method: "DELETE" })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to delete event.");
            }
            console.log("Event deleted successfully.");
        })
        .catch((error) => {
            console.error("Error deleting event:", error);
            alert("Failed to delete event. Please try again.");
        });
}

// Show/Hide Loading State
function toggleLoadingState(isLoading) {
    const loader = document.getElementById("loading-indicator");
    if (loader) {
        loader.style.display = isLoading ? "block" : "none";
    }
}

// Utility: Show Notifications
function showNotification(message, type = "success") {
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
