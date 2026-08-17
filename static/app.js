const columns = [
    { id: "backlog", title: "Backlog", description: "Ideas and unscheduled work" },
    { id: "ready", title: "Ready", description: "Clear and ready to start" },
    { id: "in_progress", title: "In progress", description: "Actively being worked" },
    { id: "review", title: "Review", description: "Waiting for human verification" },
    { id: "done", title: "Done", description: "Verified and complete" },
];

const tasks = [
    {
        id: crypto.randomUUID(),
        title: "Define Mission Control task model",
        description: "Decide which task fields belong in SQLite before adding persistent storage.",
        status: "backlog",
        priority: "high",
        owner: "Kyle",
        tag: "Architecture",
    },
    {
        id: crypto.randomUUID(),
        title: "Complete offline Gateway protocol tests",
        description: "Keep protocol work independent from the dashboard presentation layer.",
        status: "ready",
        priority: "high",
        owner: "Blackbotv0.1",
        tag: "Gateway",
    },
    {
        id: crypto.randomUUID(),
        title: "Document OpenClaw to BlackBot boundary",
        description: "Record which knowledge transfers and which private data must remain isolated.",
        status: "in_progress",
        priority: "high",
        owner: "Kyle",
        tag: "Security",
    },
    {
        id: crypto.randomUUID(),
        title: "Review identity storage prototype",
        description: "Confirm the current Ed25519 work remains experimental before DPAPI hardening.",
        status: "review",
        priority: "medium",
        owner: "Kyle",
        tag: "Security",
    },
    {
        id: crypto.randomUUID(),
        title: "Create local FastAPI shell",
        description: "Serve the workspace locally without exposing Gateway credentials to the browser.",
        status: "done",
        priority: "medium",
        owner: "Blackbotv0.1",
        tag: "Backend",
    },
];

const activity = [
    { title: "Mission Control direction confirmed", detail: "The UI is now treated as an operations workspace.", time: "Now" },
    { title: "Gateway boundary preserved", detail: "Identity and protocol work remains backend-only.", time: "Audit" },
    { title: "Repository synchronized", detail: "Local main matched origin/main before the pivot.", time: "Earlier" },
];

const board = document.querySelector("#kanban-board");
const activityList = document.querySelector("#activity-list");
const searchInput = document.querySelector("#task-search");
const filterButton = document.querySelector("#filter-button");
const filterPanel = document.querySelector("#board-filters");
const taskDialog = document.querySelector("#task-dialog");
const taskForm = document.querySelector("#task-form");
const newTaskButton = document.querySelector("#new-task-button");
const cancelTaskButton = document.querySelector("#cancel-task-button");

let priorityFilter = "all";

function escapeText(value) {
    const element = document.createElement("span");
    element.textContent = value;
    return element.innerHTML;
}

function taskMatches(task) {
    const query = searchInput.value.trim().toLowerCase();
    const matchesPriority = priorityFilter === "all" || task.priority === priorityFilter;
    const searchable = `${task.title} ${task.description} ${task.owner} ${task.tag}`.toLowerCase();
    return matchesPriority && (!query || searchable.includes(query));
}

function renderBoard() {
    board.replaceChildren();

    columns.forEach((column) => {
        const columnTasks = tasks.filter((task) => task.status === column.id && taskMatches(task));
        const columnElement = document.createElement("section");
        columnElement.className = "kanban-column";
        columnElement.dataset.status = column.id;
        columnElement.innerHTML = `
            <header class="column-heading">
                <div>
                    <h3>${escapeText(column.title)}</h3>
                    <p>${escapeText(column.description)}</p>
                </div>
                <span>${columnTasks.length}</span>
            </header>
            <div class="task-stack" data-dropzone="${column.id}"></div>
        `;

        const stack = columnElement.querySelector(".task-stack");

        columnTasks.forEach((task) => {
            stack.append(createTaskCard(task));
        });

        if (columnTasks.length === 0) {
            const emptyState = document.createElement("div");
            emptyState.className = "empty-column";
            emptyState.textContent = "No matching tasks";
            stack.append(emptyState);
        }

        stack.addEventListener("dragover", handleDragOver);
        stack.addEventListener("dragleave", handleDragLeave);
        stack.addEventListener("drop", handleDrop);
        board.append(columnElement);
    });

    updateMetrics();
}

function createTaskCard(task) {
    const card = document.createElement("article");
    card.className = "task-card";
    card.draggable = true;
    card.dataset.taskId = task.id;
    card.innerHTML = `
        <div class="task-card-topline">
            <span class="priority priority-${escapeText(task.priority)}">${escapeText(task.priority)}</span>
            <span class="task-tag">${escapeText(task.tag)}</span>
        </div>
        <h4>${escapeText(task.title)}</h4>
        <p>${escapeText(task.description)}</p>
        <footer>
            <span class="owner-avatar">${escapeText(task.owner.slice(0, 1).toUpperCase())}</span>
            <span>${escapeText(task.owner)}</span>
            <span class="drag-handle" aria-hidden="true">⠿</span>
        </footer>
    `;
    card.addEventListener("dragstart", handleDragStart);
    card.addEventListener("dragend", handleDragEnd);
    return card;
}

function renderActivity() {
    activityList.replaceChildren();

    activity.forEach((item) => {
        const entry = document.createElement("article");
        entry.className = "activity-entry";
        entry.innerHTML = `
            <span class="activity-marker"></span>
            <div>
                <strong>${escapeText(item.title)}</strong>
                <p>${escapeText(item.detail)}</p>
                <time>${escapeText(item.time)}</time>
            </div>
        `;
        activityList.append(entry);
    });
}

function updateMetrics() {
    document.querySelector("#task-count").textContent = tasks.length;
    document.querySelector("#open-task-count").textContent = tasks.filter((task) => task.status !== "done").length;
    document.querySelector("#active-task-count").textContent = tasks.filter((task) => task.status === "in_progress").length;
    document.querySelector("#review-task-count").textContent = tasks.filter((task) => task.status === "review").length;
}

function handleDragStart(event) {
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/plain", event.currentTarget.dataset.taskId);
    event.currentTarget.classList.add("dragging");
}

function handleDragEnd(event) {
    event.currentTarget.classList.remove("dragging");
    document.querySelectorAll(".task-stack").forEach((stack) => stack.classList.remove("drag-over"));
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add("drag-over");
}

function handleDragLeave(event) {
    if (!event.currentTarget.contains(event.relatedTarget)) {
        event.currentTarget.classList.remove("drag-over");
    }
}

function handleDrop(event) {
    event.preventDefault();
    const taskId = event.dataTransfer.getData("text/plain");
    const nextStatus = event.currentTarget.dataset.dropzone;
    const task = tasks.find((candidate) => candidate.id === taskId);

    event.currentTarget.classList.remove("drag-over");

    if (!task || task.status === nextStatus) {
        return;
    }

    const previousColumn = columns.find((column) => column.id === task.status);
    const nextColumn = columns.find((column) => column.id === nextStatus);
    task.status = nextStatus;
    activity.unshift({
        title: `Task moved to ${nextColumn.title}`,
        detail: `${task.title} left ${previousColumn.title}.`,
        time: "Just now",
    });
    renderBoard();
    renderActivity();
}

filterButton.addEventListener("click", () => {
    filterPanel.hidden = !filterPanel.hidden;
    filterButton.classList.toggle("selected", !filterPanel.hidden);
});

document.querySelectorAll(".filter-chip").forEach((button) => {
    button.addEventListener("click", () => {
        document.querySelectorAll(".filter-chip").forEach((chip) => chip.classList.remove("active"));
        button.classList.add("active");
        priorityFilter = button.dataset.priority;
        renderBoard();
    });
});

searchInput.addEventListener("input", renderBoard);

newTaskButton.addEventListener("click", () => {
    taskDialog.showModal();
    document.querySelector("#task-title").focus();
});

cancelTaskButton.addEventListener("click", () => taskDialog.close());

taskForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(taskForm);
    const title = formData.get("title").trim();

    if (!title) {
        return;
    }

    tasks.unshift({
        id: crypto.randomUUID(),
        title,
        description: formData.get("description").trim() || "No description provided.",
        status: "backlog",
        priority: formData.get("priority"),
        owner: formData.get("owner"),
        tag: "New",
    });
    activity.unshift({
        title: "Task created",
        detail: `${title} was added to Backlog.`,
        time: "Just now",
    });
    taskForm.reset();
    taskDialog.close();
    renderBoard();
    renderActivity();
});

document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => {
        if (button.dataset.view !== "tasks") {
            activity.unshift({
                title: `${button.textContent.trim()} view is planned`,
                detail: "The task board is the only implemented Mission Control view in this stage.",
                time: "Just now",
            });
            renderActivity();
            return;
        }

        document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
    });
});

renderBoard();
renderActivity();
