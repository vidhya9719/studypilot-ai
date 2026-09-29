/* ============================================================
   STUDYPILOT AI
   Frontend JavaScript
   ============================================================ */


/* ============================================================
   ELEMENTS
   ============================================================ */

const input =
    document.getElementById("questionInput");

const send =
    document.getElementById("sendButton");

const chat =
    document.getElementById("chatContainer");

const modeButtons =
    document.querySelectorAll("[data-mode]");

const uploadButton =
    document.getElementById("uploadButton");

const fileInput =
    document.getElementById("pdfInput");

const documentsList =
    document.getElementById("documentList");

const clearDocumentsButton =
    document.getElementById("clearDocuments");

const currentModeDisplay =
    document.getElementById("currentMode");


/* ============================================================
   STATE
   ============================================================ */

let selectedMode = "explain";

let conversation = [];


/* ============================================================
   MODE NAMES
   ============================================================ */

const modeNames = {

    explain:
        "💡 Explain",

    summarize:
        "📚 Summarize",

    quiz:
        "📝 Quiz Me",

    improve:
        "✨ Improve Answer",

    plan:
        "🎯 Study Plan",

    timetable:
        "🗓️ Timetable",

    simple:
        "🌱 Simple Explanation",

    keypoints:
        "🔑 Key Points",

    deep_analysis:
        "🔍 Deep Analysis",

    exam_answer:
        "📝 Exam Answer",

    adaptive_quiz:
        "🧠 Adaptive Quiz",

    teach_back:
        "🎓 Teach-Back",

    weak_topics:
        "📊 Weak Topic Analysis",

    smart_revision:
        "🔄 Smart Revision",

    concept_connections:
        "🕸️ Concept Connections",

    study_roadmap:
        "🗺️ Study Roadmap"

};


/* ============================================================
   ESCAPE HTML
   ============================================================ */

function escapeHTML(value) {

    return String(value)

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");
}


/* ============================================================
   FORMAT AI ANSWER
   ============================================================ */

function formatAnswer(text) {

    if (!text) {
        return "";
    }

    let safe =
        escapeHTML(text);


    /* Code blocks */

    safe = safe.replace(
        /```([\s\S]*?)```/g,
        function(match, code) {

            return `
                <pre><code>${code.trim()}</code></pre>
            `;

        }
    );


    /* Headings */

    safe = safe.replace(
        /^### (.*)$/gm,
        "<h4>$1</h4>"
    );

    safe = safe.replace(
        /^## (.*)$/gm,
        "<h3>$1</h3>"
    );

    safe = safe.replace(
        /^# (.*)$/gm,
        "<h2>$1</h2>"
    );


    /* Bold */

    safe = safe.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );


    /* Italic */

    safe = safe.replace(
        /\*(.*?)\*/g,
        "<em>$1</em>"
    );


    /* Bullet points */

    safe = safe.replace(
        /^\s*[-•]\s+(.*)$/gm,
        "<li>$1</li>"
    );


    safe = safe.replace(
        /(<li>.*?<\/li>)/gs,
        function(match) {

            return `<ul>${match}</ul>`;

        }
    );


    /* Numbered lists */

    safe = safe.replace(
        /^\s*\d+\.\s+(.*)$/gm,
        "<li>$1</li>"
    );


    /* Blockquotes */

    safe = safe.replace(
        /^>\s?(.*)$/gm,
        "<blockquote>$1</blockquote>"
    );


    /*
       Convert remaining line breaks.

       Do not modify breaks inside pre blocks.
    */

    const parts =
        safe.split(
            /(<pre>[\s\S]*?<\/pre>)/
        );


    for (
        let i = 0;
        i < parts.length;
        i++
    ) {

        if (
            !parts[i].startsWith("<pre>")
        ) {

            parts[i] =
                parts[i].replace(
                    /\n/g,
                    "<br>"
                );

        }

    }


    return parts.join("");
}


/* ============================================================
   ADD USER MESSAGE
   ============================================================ */

function addUserMessage(text) {

    if (!chat) {
        return;
    }


    const message =
        document.createElement("div");

    message.className =
        "chat-message user";


    message.innerHTML = `

        <div class="message-avatar">
            👤
        </div>

        <div class="message-bubble">
            ${escapeHTML(text)}
        </div>

    `;


    chat.appendChild(message);


    chat.scrollTop =
        chat.scrollHeight;
}


/* ============================================================
   ADD AI MESSAGE
   ============================================================ */

function addAIMessage(
    text,
    sources = [],
    demoMode = false
) {

    if (!chat) {
        return;
    }


    const message =
        document.createElement("div");

    message.className =
        "chat-message assistant";


    let sourcesHTML = "";


    if (
        Array.isArray(sources) &&
        sources.length > 0
    ) {

        sourcesHTML = `

            <div class="sources">

                <div class="sources-title">
                    📚 Sources
                </div>

                ${sources.map(
                    source => `

                        <span class="source-item">
                            ${escapeHTML(
                                source.filename ||
                                source.name ||
                                String(source)
                            )}
                        </span>

                    `
                ).join("")}

            </div>

        `;

    }


    const demoHTML =
        demoMode
            ? `
                <div class="sources">
                    <div class="sources-title">
                        ✨ StudyPilot
                    </div>
                    <span class="source-item">
                        Demo response
                    </span>
                </div>
            `
            : "";


    message.innerHTML = `

        <div class="message-avatar">
            🧠
        </div>

        <div class="message-bubble">

            ${formatAnswer(text)}

            ${sourcesHTML}

            ${demoHTML}

        </div>

    `;


    chat.appendChild(message);


    chat.scrollTop =
        chat.scrollHeight;
}


/* ============================================================
   LOADING MESSAGE
   ============================================================ */

function addLoadingMessage() {

    if (!chat) {
        return;
    }


    const message =
        document.createElement("div");

    message.className =
        "chat-message assistant";

    message.id =
        "loading-message";


    message.innerHTML = `

        <div class="message-avatar">
            🧠
        </div>

        <div class="message-bubble">

            <div class="loading-message">

                <span>
                    StudyPilot is thinking
                </span>

                <div class="loading-dots">

                    <span></span>
                    <span></span>
                    <span></span>

                </div>

            </div>

        </div>

    `;


    chat.appendChild(message);


    chat.scrollTop =
        chat.scrollHeight;
}


/* ============================================================
   REMOVE LOADING MESSAGE
   ============================================================ */

function removeLoadingMessage() {

    const loading =
        document.getElementById(
            "loading-message"
        );


    if (loading) {
        loading.remove();
    }
}


/* ============================================================
   SEND QUESTION
   ============================================================ */

async function sendQuestion() {

    if (!input) {
        return;
    }


    const text =
        input.value.trim();


    /* Empty question */

    if (!text) {

        input.focus();

        return;
    }


    /* Add user message */

    addUserMessage(text);


    /* Clear input */

    input.value = "";


    /* Disable send */

    if (send) {
        send.disabled = true;
    }


    /* Loading */

    addLoadingMessage();


    try {

        const response =
            await fetch(
                "/ask",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({

                            message: text,

                            mode:
                                selectedMode,

                            style:
                                "intermediate",

                            history:
                                conversation.slice(-8)

                        })

                }
            );


        let data;


        try {

            data =
                await response.json();

        }

        catch (jsonError) {

            throw new Error(
                "The server returned an invalid response."
            );

        }


        removeLoadingMessage();


        /* Server error */

        if (!response.ok) {

            addAIMessage(

                data.error ||
                "StudyPilot could not process your question."

            );

            return;
        }


        /* Save conversation */

        conversation.push({

            role: "user",

            content: text

        });


        conversation.push({

            role: "assistant",

            content:
                data.response || ""

        });


        /* Keep history manageable */

        if (
            conversation.length > 20
        ) {

            conversation =
                conversation.slice(-20);

        }


        /* Display answer */

        addAIMessage(

            data.response ||
            "I could not generate an answer.",

            data.sources || [],

            data.demo_mode || false

        );

    }


    catch (error) {

        removeLoadingMessage();


        console.error(
            "StudyPilot error:",
            error
        );


        addAIMessage(

            "⚠️ StudyPilot could not connect to the local AI service. " +
            "Please make sure Ollama is running and " +
            "the llama3.2:3b model is installed."

        );

    }


    finally {

        if (send) {
            send.disabled = false;
        }

        input.focus();

    }

}


/* ============================================================
   SEND BUTTON
   ============================================================ */

if (send) {

    send.addEventListener(
        "click",
        sendQuestion
    );

}


/* ============================================================
   ENTER KEY
   ============================================================ */

if (input) {

    input.addEventListener(
        "keydown",
        function(event) {

            /*
               Enter = send
               Shift + Enter = new line
            */

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendQuestion();

            }

        }
    );

}


/* ============================================================
   STUDY MODE BUTTONS
   ============================================================ */

modeButtons.forEach(
    button => {

        button.addEventListener(
            "click",
            function() {

                selectedMode =
                    this.dataset.mode ||
                    "explain";


                /* Remove active state */

                modeButtons.forEach(
                    btn =>
                        btn.classList.remove(
                            "active"
                        )
                );


                /* Add active state */

                this.classList.add(
                    "active"
                );


                /* Update current mode */

                if (
                    currentModeDisplay
                ) {

                    currentModeDisplay.textContent =
                        modeNames[
                            selectedMode
                        ] ||
                        "💡 Explain";

                }

            }
        );

    }
);


/* ============================================================
   PDF UPLOAD
   ============================================================ */

if (uploadButton) {

    uploadButton.addEventListener(
        "click",
        function() {

            if (fileInput) {

                fileInput.click();

            }

        }
    );

}


/* ============================================================
   HANDLE SELECTED PDF
   ============================================================ */

if (fileInput) {

    fileInput.addEventListener(
        "change",
        async function() {

            if (
                !fileInput.files ||
                !fileInput.files.length
            ) {

                return;
            }


            const file =
                fileInput.files[0];


            /* Check file */

            if (
                !file.name
                    .toLowerCase()
                    .endsWith(".pdf")
            ) {

                addAIMessage(
                    "⚠️ Please select a PDF file."
                );

                fileInput.value = "";

                return;
            }


            /* File size */

            const maxSize =
                15 * 1024 * 1024;


            if (
                file.size > maxSize
            ) {

                addAIMessage(
                    "⚠️ This PDF is larger than 15 MB. Please choose a smaller file."
                );

                fileInput.value = "";

                return;
            }


            const formData =
                new FormData();


            formData.append(
                "file",
                file
            );


            uploadButton.disabled =
                true;


            addAIMessage(
                `📄 Reading "${file.name}"...`
            );


            try {

                const response =
                    await fetch(
                        "/upload",
                        {

                            method: "POST",

                            body:
                                formData

                        }
                    );


                let data;


                try {

                    data =
                        await response.json();

                }

                catch (error) {

                    throw new Error(
                        "The server returned an invalid response."
                    );

                }


                if (!response.ok) {

                    throw new Error(
                        data.error ||
                        "PDF upload failed."
                    );

                }


                /* Refresh document list */

                await loadDocuments();


                /* Success message */

                addAIMessage(

                    data.message ||

                    `✅ "${file.name}" is ready. You can now ask questions about your PDF.`

                );

            }


            catch (error) {

                console.error(
                    "Upload error:",
                    error
                );


                addAIMessage(

                    `⚠️ Could not upload the PDF. ${
                        error.message ||
                        "Please try again."
                    }`

                );

            }


            finally {

                uploadButton.disabled =
                    false;

                fileInput.value = "";

            }

        }
    );

}


/* ============================================================
   LOAD DOCUMENTS
   ============================================================ */

async function loadDocuments() {

    if (!documentsList) {
        return;
    }


    try {

        const response =
            await fetch(
                "/documents"
            );


        const data =
            await response.json();


        documentsList.innerHTML =
            "";


        const documents =
            data.documents || [];


        if (
            documents.length === 0
        ) {

            documentsList.innerHTML = `

                <div
                    style="
                        padding:8px;
                        color:#60718b;
                        font-size:9px;
                        text-align:center;
                    "
                >
                    No PDFs yet ✨
                </div>

            `;

            return;
        }


        documents.forEach(
            doc => {

                const item =
                    document.createElement(
                        "div"
                    );


                item.className =
                    "document-item";


                const filename =
                    doc.filename ||
                    doc.name ||
                    "Document";


                const chunks =
                    doc.chunks ||
                    0;


                item.innerHTML = `

                    <span>📄</span>

                    <div
                        style="
                            min-width:0;
                            overflow:hidden;
                        "
                    >

                        <strong
                            style="
                                display:block;
                                overflow:hidden;
                                text-overflow:ellipsis;
                                white-space:nowrap;
                                color:#b7c8df;
                                font-size:9px;
                            "
                        >
                            ${escapeHTML(
                                filename
                            )}
                        </strong>

                        <small
                            style="
                                color:#61738d;
                                font-size:8px;
                            "
                        >
                            ${chunks} chunks
                        </small>

                    </div>

                `;


                documentsList.appendChild(
                    item
                );

            }
        );

    }


    catch (error) {

        console.error(
            "Could not load documents:",
            error
        );

    }

}


/* ============================================================
   CLEAR DOCUMENTS
   ============================================================ */

if (clearDocumentsButton) {

    clearDocumentsButton.addEventListener(
        "click",
        async function() {

            const confirmed =
                window.confirm(
                    "Clear all uploaded study documents?"
                );


            if (!confirmed) {
                return;
            }


            try {

                const response =
                    await fetch(
                        "/clear-documents",
                        {
                            method: "POST"
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.error ||
                        "Could not clear documents."
                    );

                }


                await loadDocuments();


                addAIMessage(
                    "🗑️ Your uploaded documents have been cleared."
                );

            }


            catch (error) {

                console.error(
                    "Clear documents error:",
                    error
                );


                addAIMessage(
                    "⚠️ Could not clear the documents. Please try again."
                );

            }

        }
    );

}


/* ============================================================
   FOCUS QUESTION
   ============================================================ */

function focusQuestion(text) {

    if (!input) {
        return;
    }


    input.value =
        text || "";


    input.focus();


    /*
       Put cursor at the end
       so the student can immediately
       continue typing.
    */

    try {

        input.selectionStart =
            input.value.length;

        input.selectionEnd =
            input.value.length;

    }

    catch (error) {

        console.log(
            "Cursor positioning unavailable."
        );

    }

}


/* ============================================================
   MAKE focusQuestion AVAILABLE TO HTML
   ============================================================ */

window.focusQuestion =
    focusQuestion;


/* ============================================================
   INITIALIZE
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        loadDocuments();


        /*
           Make sure Explain starts active.
        */

        modeButtons.forEach(
            button => {

                if (
                    button.dataset.mode ===
                    "explain"
                ) {

                    button.classList.add(
                        "active"
                    );

                }

            }
        );

    }
);