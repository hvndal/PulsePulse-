const API_BASE = "http://127.0.0.1:8000/api";

let currentProject = null;
let voices = [];

document.addEventListener("DOMContentLoaded", async () => {
    await loadVoices();
    await loadProjects();
    setupEventListeners();
});

async function loadVoices() {
    try {
        const res = await fetch(`${API_BASE}/voices`);
        voices = await res.json();
        const select = document.getElementById("voice-select");
        select.innerHTML = voices.map(v => `<option value="${v.id}">${v.name} (${v.gender})</option>`).join("");
        updateVoiceDetails();
    } catch (e) {
        console.error("Failed to load voices", e);
    }
}

async function loadProjects() {
    try {
        const res = await fetch(`${API_BASE}/projects`);
        const projects = await res.json();
        const select = document.getElementById("project-select");
        select.innerHTML = projects.map(p => `<option value="${p.id}">${p.title}</option>`).join("");
        if (projects.length > 0) {
            currentProject = projects[0];
            renderProject();
        }
    } catch (e) {
        console.error("Failed to load projects", e);
    }
}

function updateVoiceDetails() {
    const vId = document.getElementById("voice-select").value;
    const v = voices.find(x => x.id === vId);
    if (v) {
        document.getElementById("voice-details").innerHTML = `
            <p class="subtitle" style="margin-top: 6px;">${v.description}</p>
            <span class="badge">Sample Rate: ${v.sample_rate}Hz</span>
        `;
    }
}

function renderProject() {
    if (!currentProject) return;
    document.getElementById("project-meta").innerHTML = `
        <p style="margin-top: 6px;"><strong>Author:</strong> ${currentProject.author}</p>
        <p class="subtitle">${currentProject.genre} — ${currentProject.description}</p>
    `;

    const scriptContainer = document.getElementById("script-container");
    scriptContainer.innerHTML = "";

    currentProject.chapters.forEach(ch => {
        const chHeading = document.createElement("h3");
        chHeading.style.margin = "12px 0";
        chHeading.innerText = ch.title;
        scriptContainer.appendChild(chHeading);

        ch.paragraphs.forEach(p => {
            const card = document.createElement("div");
            card.className = `paragraph-card ${p.status}`;
            card.innerHTML = `
                <p><strong>Paragraph ${p.order}:</strong> ${p.text}</p>
                <div class="paragraph-actions">
                    <span class="badge">Status: ${p.status}</span>
                    <div>
                        <button class="btn btn-secondary btn-sm" onclick="inspectContext("${ch.id}", "${p.id}")">Context</button>
                        <button class="btn btn-primary btn-sm" onclick="generateParagraph("${currentProject.id}", "${p.id}")">Generate Speech</button>
                        ${p.audio_url ? `<button class="btn btn-success btn-sm" onclick="playAudio("${p.audio_url}", "Paragraph ${p.order}")">Play</button>` : ""}
                    </div>
                </div>
            `;
            scriptContainer.appendChild(card);
        });
    });
}

async function generateParagraph(projectId, paragraphId) {
    try {
        const res = await fetch(`${API_BASE}/projects/${projectId}/generate-paragraph/${paragraphId}`, { method: "POST" });
        const result = await res.json();

        // Refresh project data
        const prRes = await fetch(`${API_BASE}/projects/${projectId}`);
        currentProject = await prRes.json();
        renderProject();
    } catch (e) {
        console.error("Failed to generate speech", e);
    }
}

function inspectContext(chapterId, paragraphId) {
    const inspector = document.getElementById("context-inspector");
    inspector.innerHTML = `
        <p><strong>Inspecting Paragraph:</strong> ${paragraphId}</p>
        <span class="badge">Hierarchical Context Window Applied</span>
        <p style="margin-top: 8px;" class="subtitle">Tone: Authoritative / Dynamic | Pacing: Natural Narrative Flow</p>
    `;
}

function playAudio(url, title) {
    const player = document.getElementById("main-audio-player");
    player.src = url;
    player.play();
    document.getElementById("now-playing-title").innerText = `Playing: ${title}`;
    document.getElementById("now-playing-qc").innerText = "QC Status: Normalized (-3dB Peak)";
}

function setupEventListeners() {
    document.getElementById("voice-select").addEventListener("change", updateVoiceDetails);

    document.getElementById("btn-pronunciation").addEventListener("click", () => {
        document.getElementById("pronunciation-modal").classList.remove("hidden");
    });

    document.getElementById("btn-close-modal").addEventListener("click", () => {
        document.getElementById("pronunciation-modal").classList.add("hidden");
    });

    document.getElementById("btn-export").addEventListener("click", async () => {
        if (!currentProject) return;
        window.open(`${API_BASE}/export?project_id=${currentProject.id}&format=wav`);
    });
}
