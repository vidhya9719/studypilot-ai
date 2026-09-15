const toolCards = document.querySelectorAll(".tool-card");

const workspaceTitle = document.getElementById("workspaceTitle");
const workspaceDescription = document.getElementById("workspaceDescription");

const userInput = document.getElementById("userInput");
const characterCount = document.getElementById("characterCount");

const generateBtn = document.getElementById("generateBtn");
const buttonIcon = document.getElementById("buttonIcon");
const buttonText = document.getElementById("buttonText");

const outputSection = document.getElementById("outputSection");
const output = document.getElementById("output");

const errorBox = document.getElementById("errorBox");
const loadingBox = document.getElementById("loadingBox");

const timetableOptions = document.getElementById("timetableOptions");

const studyHours = document.getElementById("studyHours");
const studyDays = document.getElementById("studyDays");

const copyBtn = document.getElementById("copyBtn");


let selectedTool = "explain";


const toolInfo = {

    explain: {
        title: "Explain a Topic",
        description: "Enter a topic or question you want to understand.",
        placeholder: "Example: Explain DBMS and its important topics in simple English...",
        button: "Generate Explanation",
        icon: "💡"
    },

    summarize: {
        title: "Summarize Your Notes",
        description: "Paste your notes and turn them into quick revision material.",
        placeholder: "Paste your class notes here...",
        button: "Summarize Notes",
        icon: "📝"
    },

    quiz: {
        title: "Generate a Quiz",
        description: "Enter a topic or notes and create practice questions.",
        placeholder: "Example: DBMS keys, relational schema and normalization...",
        button: "Generate Quiz",
        icon: "🧠"
    },

    improve: {
        title: "Improve Your Answer",
        description: "Paste your answer and StudyPilot will help improve it.",
        placeholder: "Paste your exam answer here...",
        button: "Improve Answer",
        icon: "✍️"
    },

    plan: {
        title: "Create a Study Plan",
        description: "Tell StudyPilot what you need to learn.",
        placeholder: "Example: I have to learn DBMS transactions, normalization and SQL...",
        button: "Create Study Plan",
        icon: "🌱"
    },

    timetable: {
        title: "Smart Timetable",
        description: "Create a timetable with priority topics and practice questions.",
        placeholder: "Example: DBMS — ER model, keys, relational schema, SQL, normalization...",
        button: "Generate Smart Timetable",
        icon: "🗓️"
    }
};


function selectTool(tool) {

    selectedTool = tool;

    toolCards.forEach(card => {

        card.classList.remove("active");

        if (card.dataset.tool === tool) {
            card.classList.add("active");
        }

    });

    const info = toolInfo[tool];

    workspaceTitle.textContent = info.title;
    workspaceDescription.textContent = info.description;

    userInput.placeholder = info.placeholder;

    buttonText.textContent = info.button;
    buttonIcon.textContent = info.icon;

    if (tool === "timetable") {
        timetableOptions.classList.remove("hidden");
    } else {
        timetableOptions.classList.add("hidden");
    }

    clearMessages();
}


toolCards.forEach(card => {

    card.addEventListener("click", () => {
        selectTool(card.dataset.tool);
    });

});


userInput.addEventListener("input", () => {

    characterCount.textContent =
        `${userInput.value.length} / 6000`;

});


function clearMessages() {

    errorBox.textContent = "";
    errorBox.classList.add("hidden");

    outputSection.classList.add("hidden");
    output.textContent = "";
}


function showError(message) {

    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}


generateBtn.addEventListener("click", async () => {

    clearMessages();

    const text = userInput.value.trim();

    if (!text) {

        showError(
            "Please enter a topic, question, notes, or answer first."
        );

        userInput.focus();

        return;
    }

    if (text.length > 6000) {

        showError(
            "Please keep your input below 6000 characters."
        );

        return;
    }

    let finalInput = text;


    if (selectedTool === "timetable") {

        const hours = studyHours.value;
        const days = studyDays.value;

        if (!hours || Number(hours) <= 0) {

            showError(
                "Please enter your available study hours."
            );

            return;
        }

        if (!days || Number(days) <= 0) {

            showError(
                "Please enter the number of study days."
            );

            return;
        }

        finalInput = `
Subject / Topic / Syllabus:
${text}

Available study time per day:
${hours} hours

Number of study days:
${days} days

Create the smart timetable.
Identify high-priority topics and important practice questions.
`;
    }


    generateBtn.disabled = true;

    buttonText.textContent = "Generating...";
    buttonIcon.textContent = "⏳";

    loadingBox.classList.remove("hidden");


    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                input: finalInput,
                tool: selectedTool
            })

        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Something went wrong. Please try again."
            );
        }


        output.textContent = data.response;

        outputSection.classList.remove("hidden");


        outputSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });


    } catch (error) {

        showError(
            error.message ||
            "StudyPilot could not connect to the AI service."
        );

    } finally {

        loadingBox.classList.add("hidden");

        generateBtn.disabled = false;

        buttonText.textContent =
            toolInfo[selectedTool].button;

        buttonIcon.textContent =
            toolInfo[selectedTool].icon;
    }

});


copyBtn.addEventListener("click", async () => {

    const text = output.textContent.trim();

    if (!text) {
        return;
    }

    try {

        await navigator.clipboard.writeText(text);

        copyBtn.textContent = "✅ Copied!";

        setTimeout(() => {
            copyBtn.textContent = "📋 Copy";
        }, 1500);

    } catch {

        copyBtn.textContent = "Copy failed";

        setTimeout(() => {
            copyBtn.textContent = "📋 Copy";
        }, 1500);
    }

});


selectTool("explain");
