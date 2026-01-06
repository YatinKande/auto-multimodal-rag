
const API_URL = "http://localhost:8000";

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadStatus = document.getElementById('upload-status');
const fileList = document.getElementById('file-list');
const apiStatus = document.getElementById('api-status');
const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// --- Initialization ---
async function init() {
    checkHealth();
    fetchUploadedFiles();
}

async function checkHealth() {
    try {
        const res = await fetch(`${API_URL}/health`);
        if (res.ok) {
            const data = await res.json();
            apiStatus.innerHTML = `<span class="indicator online"></span> Backend: Online (Docs: ${data.faiss_index_size})`;
        } else {
            throw new Error("Backend Error");
        }
    } catch (e) {
        apiStatus.innerHTML = `<span class="indicator"></span> Backend: Offline`;
    }
}

async function fetchUploadedFiles() {
    try {
        const res = await fetch(`${API_URL}/list_uploaded`);
        const data = await res.json();
        fileList.innerHTML = "";
        if (data.files.length === 0) {
            fileList.innerHTML = "<li><small>No files loaded.</small></li>";
            return;
        }
        data.files.forEach(file => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="fas fa-file-alt"></i> ${file}`;
            fileList.appendChild(li);
        });
    } catch (e) {
        console.error("Failed to list files");
    }
}

// --- Upload Logic ---
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "#00f0ff";
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "#30363d";
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "#30363d";
    handleUpload(e.dataTransfer.files);
});

fileInput.addEventListener('change', () => {
    handleUpload(fileInput.files);
});

async function handleUpload(files) {
    if (!files.length) return;

    uploadStatus.innerHTML = `<small style="color: #00f0ff;">Uploading & Indexing...</small>`;
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }

    try {
        const res = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        let successCount = data.results.filter(r => r.status === 'indexed').length;
        uploadStatus.innerHTML = `<small style="color: #00ff88;">Success: ${successCount}/${files.length}</small>`;

        init(); // Refresh list and health
    } catch (e) {
        uploadStatus.innerHTML = `<small style="color: #ff3b3b;">Upload Failed</small>`;
    }
}

// --- Chat Logic ---
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    userInput.value = '';

    // Show loading
    const loadingId = addMessage('Analyzing vehicle data...', 'bot', true);

    try {
        const res = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: text })
        });
        const data = await res.json();

        // Remove loading
        removeMessage(loadingId);

        if (data.error) {
            addMessage(`Error: ${data.error}`, 'bot');
        } else {
            addMessage(data.answer, 'bot', false, data.sources);
        }
    } catch (e) {
        removeMessage(loadingId);
        addMessage(`Connection Error: ${e.message}`, 'bot');
    }
}

function addMessage(text, sender, isLoading = false, sources = []) {
    const id = Date.now();
    const wrapper = document.createElement('div');
    wrapper.className = `message ${sender}`;
    wrapper.id = `msg-${id}`;

    const icon = sender === 'bot' ? 'fas fa-robot' : 'fas fa-user';

    let contentHtml = isLoading ? `<i>${text}</i>` : marked.parse(text);

    if (sources && sources.length > 0) {
        contentHtml += `<div class="sources-list"><small>SOURCES:</small>`;
        sources.forEach(s => {
            contentHtml += `
                <div class="source-item">
                    <span>${s.filename} ${s.page ? `(p.${s.page})` : ''}</span>
                    <span class="source-type">${s.type}</span>
                </div>`;
        });
        contentHtml += `</div>`;
    }

    wrapper.innerHTML = `
        <div class="avatar"><i class="${icon}"></i></div>
        <div class="content">${contentHtml}</div>
    `;

    chatHistory.appendChild(wrapper);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(`msg-${id}`);
    if (el) el.remove();
}

// Start
init();
