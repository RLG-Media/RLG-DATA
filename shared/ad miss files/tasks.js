// tasks.js
document.addEventListener("DOMContentLoaded", () => {
    const taskList = document.getElementById("taskList");
    const statusFilter = document.getElementById("statusFilter");
    const priorityFilter = document.getElementById("priorityFilter");
    const applyFilters = document.getElementById("applyFilters");
    const addTaskForm = document.getElementById("addTaskForm");
    const taskModal = document.getElementById("taskModal");
    const taskDetails = document.getElementById("taskDetails");
    const markComplete = document.getElementById("markComplete");
    const closeModal = document.querySelector(".close-modal");

    let tasks = []; // Store all tasks locally for easy filtering and manipulation

    // Fetch tasks from the backend on load
    const fetchTasks = async () => {
        try {
            const response = await axios.get("/api/tasks");
            tasks = response.data.tasks;
            renderTaskList(tasks);
        } catch (error) {
            console.error("Error fetching tasks:", error);
            alert("Failed to fetch tasks. Please try again later.");
        }
    };

    // Render task list
    const renderTaskList = (tasksToRender) => {
        taskList.innerHTML = ""; // Clear existing tasks
        if (tasksToRender.length === 0) {
            taskList.innerHTML = "<li>No tasks found.</li>";
            return;
        }

        tasksToRender.forEach((task) => {
            const taskItem = document.createElement("li");
            taskItem.className = `task-item ${task.status}`;
            taskItem.innerHTML = `
                <div>
                    <h3>${task.name}</h3>
                    <p>${task.description}</p>
                    <p><strong>Priority:</strong> ${task.priority}</p>
                    <p><strong>Status:</strong> ${task.status}</p>
                </div>
                <div>
                    <button class="btn-secondary view-task" data-id="${task.id}">View</button>
                </div>
            `;
            taskList.appendChild(taskItem);
        });

        // Attach event listeners for view buttons
        document.querySelectorAll(".view-task").forEach((btn) =>
            btn.addEventListener("click", (e) => {
                const taskId = e.target.dataset.id;
                openTaskModal(taskId);
            })
        );
    };

    // Apply filters
    const filterTasks = () => {
        const status = statusFilter.value;
        const priority = priorityFilter.value;

        const filteredTasks = tasks.filter((task) => {
            const statusMatch = status === "all" || task.status === status;
            const priorityMatch = priority === "all" || task.priority === priority;
            return statusMatch && priorityMatch;
        });

        renderTaskList(filteredTasks);
    };

    // Open task modal
    const openTaskModal = (taskId) => {
        const task = tasks.find((t) => t.id === taskId);
        if (!task) {
            alert("Task not found.");
            return;
        }

        taskDetails.innerHTML = `
            <h3>${task.name}</h3>
            <p>${task.description}</p>
            <p><strong>Priority:</strong> ${task.priority}</p>
            <p><strong>Status:</strong> ${task.status}</p>
            <p><strong>Due Date:</strong> ${new Date(task.dueDate).toLocaleDateString()}</p>
        `;
        markComplete.dataset.id = taskId;
        taskModal.style.display = "block";
    };

    // Close task modal
    const closeTaskModal = () => {
        taskModal.style.display = "none";
    };

    // Mark task as complete
    const completeTask = async (taskId) => {
        try {
            await axios.put(`/api/tasks/${taskId}`, { status: "completed" });
            tasks = tasks.map((task) =>
                task.id === taskId ? { ...task, status: "completed" } : task
            );
            filterTasks(); // Re-render the list with updated task status
            closeTaskModal();
        } catch (error) {
            console.error("Error marking task as complete:", error);
            alert("Failed to update task. Please try again later.");
        }
    };

    // Add a new task
    const addTask = async (e) => {
        e.preventDefault();
        const formData = new FormData(addTaskForm);
        const newTask = {
            name: formData.get("taskName"),
            description: formData.get("taskDescription"),
            priority: formData.get("taskPriority"),
            dueDate: formData.get("taskDueDate"),
            status: "pending",
        };

        try {
            const response = await axios.post("/api/tasks", newTask);
            tasks.push(response.data.task); // Add new task to the local list
            filterTasks(); // Re-render the list
            addTaskForm.reset(); // Clear the form
        } catch (error) {
            console.error("Error adding task:", error);
            alert("Failed to add task. Please try again later.");
        }
    };

    // Event listeners
    applyFilters.addEventListener("click", filterTasks);
    addTaskForm.addEventListener("submit", addTask);
    closeModal.addEventListener("click", closeTaskModal);
    markComplete.addEventListener("click", (e) => {
        const taskId = e.target.dataset.id;
        completeTask(taskId);
    });

    // Initial fetch and render
    fetchTasks();
});
