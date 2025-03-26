document.addEventListener("DOMContentLoaded", () => {
    // Constants for API and DOM elements
    const BUG_TRACKER_ENDPOINT = "/api/bugs"; // Replace with your API endpoint
    const BUG_LIST_CONTAINER = document.getElementById("bug-list");
    const BUG_FORM = document.getElementById("bug-form");
    const SEARCH_INPUT = document.getElementById("search-bugs");
    const STATUS_FILTER = document.getElementById("status-filter");
    const PRIORITY_FILTER = document.getElementById("priority-filter");

    // Fetch and render bugs
    const fetchBugs = async (query = "", status = "", priority = "") => {
        try {
            const url = new URL(BUG_TRACKER_ENDPOINT, window.location.origin);
            url.searchParams.append("query", query);
            url.searchParams.append("status", status);
            url.searchParams.append("priority", priority);

            const response = await fetch(url);
            if (!response.ok) throw new Error("Failed to fetch bugs");

            const data = await response.json();
            renderBugList(data.bugs);
        } catch (error) {
            console.error("Error fetching bugs:", error);
            BUG_LIST_CONTAINER.innerHTML = `<p class="error-message">Error loading bugs. Please try again later.</p>`;
        }
    };

    // Render bug list in the DOM
    const renderBugList = (bugs) => {
        BUG_LIST_CONTAINER.innerHTML = "";

        if (bugs.length === 0) {
            BUG_LIST_CONTAINER.innerHTML = `<p>No bugs found for the selected filters or search.</p>`;
            return;
        }

        bugs.forEach((bug) => {
            const bugItem = document.createElement("div");
            bugItem.classList.add("bug-item");

            bugItem.innerHTML = `
                <div class="bug-header">
                    <h3>${escapeHtml(bug.title)}</h3>
                    <span class="bug-status ${bug.status.toLowerCase()}">${bug.status}</span>
                </div>
                <div class="bug-details">
                    <p><strong>Priority:</strong> ${bug.priority}</p>
                    <p><strong>Reported By:</strong> ${escapeHtml(bug.reportedBy)}</p>
                    <p><strong>Description:</strong> ${escapeHtml(bug.description)}</p>
                    <p><strong>Created:</strong> ${new Date(bug.createdAt).toLocaleString()}</p>
                </div>
                <div class="bug-actions">
                    <button class="resolve-btn" data-id="${bug.id}">Resolve</button>
                    <button class="delete-btn" data-id="${bug.id}">Delete</button>
                </div>
            `;

            // Attach event listeners to actions
            bugItem.querySelector(".resolve-btn").addEventListener("click", () => resolveBug(bug.id));
            bugItem.querySelector(".delete-btn").addEventListener("click", () => deleteBug(bug.id));

            BUG_LIST_CONTAINER.appendChild(bugItem);
        });
    };

    // Add a new bug
    BUG_FORM.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData(BUG_FORM);
        const bugData = Object.fromEntries(formData.entries());

        try {
            const response = await fetch(BUG_TRACKER_ENDPOINT, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(bugData)
            });

            if (!response.ok) throw new Error("Failed to add bug");

            fetchBugs(); // Refresh the bug list
            BUG_FORM.reset();
        } catch (error) {
            console.error("Error adding bug:", error);
            alert("Failed to add the bug. Please try again.");
        }
    });

    // Resolve a bug
    const resolveBug = async (bugId) => {
        try {
            const response = await fetch(`${BUG_TRACKER_ENDPOINT}/${bugId}/resolve`, {
                method: "PATCH"
            });

            if (!response.ok) throw new Error("Failed to resolve bug");

            fetchBugs(); // Refresh the bug list
        } catch (error) {
            console.error("Error resolving bug:", error);
            alert("Failed to resolve the bug. Please try again.");
        }
    };

    // Delete a bug
    const deleteBug = async (bugId) => {
        try {
            const response = await fetch(`${BUG_TRACKER_ENDPOINT}/${bugId}`, {
                method: "DELETE"
            });

            if (!response.ok) throw new Error("Failed to delete bug");

            fetchBugs(); // Refresh the bug list
        } catch (error) {
            console.error("Error deleting bug:", error);
            alert("Failed to delete the bug. Please try again.");
        }
    };

    // Escape HTML for security
    const escapeHtml = (str) => {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    };

    // Search and filter functionality
    SEARCH_INPUT.addEventListener("input", () => {
        fetchBugs(SEARCH_INPUT.value, STATUS_FILTER.value, PRIORITY_FILTER.value);
    });

    STATUS_FILTER.addEventListener("change", () => {
        fetchBugs(SEARCH_INPUT.value, STATUS_FILTER.value, PRIORITY_FILTER.value);
    });

    PRIORITY_FILTER.addEventListener("change", () => {
        fetchBugs(SEARCH_INPUT.value, STATUS_FILTER.value, PRIORITY_FILTER.value);
    });

    // Initial fetch of bugs
    fetchBugs();
});
