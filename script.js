/**
 * DOCUMIND AI - EXPANDED INTERACTIVE RUNTIME
 * Features: Multi-theme engine, direct in-browser PDF upload,
 * pricing calculator, API code switcher, and audio synthesizer.
 */

// ==========================================================================
// 1. THEME SWITCHER ENGINE (OLED, Cyberpunk Neon, Studio Light)
// ==========================================================================
function setupThemeSwitcher() {
  const themeBtns = document.querySelectorAll('.theme-pill-btn');
  const savedTheme = localStorage.getItem('documind-theme') || 'oled';

  applyTheme(savedTheme);

  themeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const theme = btn.dataset.theme;
      applyTheme(theme);
      sfx.playClick();
    });
  });
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('documind-theme', theme);

  document.querySelectorAll('.theme-pill-btn').forEach(b => {
    if (b.dataset.theme === theme) {
      b.classList.add('active');
    } else {
      b.classList.remove('active');
    }
  });
}

// ==========================================================================
// 2. AUDIO SYNTHESIZER (Web Audio API)
// ==========================================================================
class SoundFX {
  constructor() {
    this.enabled = true;
    this.ctx = null;
  }

  init() {
    if (!this.ctx && typeof window !== 'undefined') {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
  }

  toggle() {
    this.enabled = !this.enabled;
    return this.enabled;
  }

  playClick() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(640, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(880, this.ctx.currentTime + 0.04);
    gain.gain.setValueAtTime(0.04, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.04);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.04);
  }

  playSuccess() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();

    const now = this.ctx.currentTime;
    const osc1 = this.ctx.createOscillator();
    const osc2 = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc1.type = 'sine';
    osc2.type = 'triangle';
    osc1.frequency.setValueAtTime(523.25, now);
    osc1.frequency.setValueAtTime(659.25, now + 0.08);
    osc1.frequency.setValueAtTime(783.99, now + 0.16);
    osc1.frequency.setValueAtTime(1046.50, now + 0.24);

    gain.gain.setValueAtTime(0.05, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);

    osc1.connect(gain);
    osc2.connect(gain);
    gain.connect(this.ctx.destination);

    osc1.start(now);
    osc2.start(now);
    osc1.stop(now + 0.45);
    osc2.stop(now + 0.45);
  }

  playPulse() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(220, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(440, this.ctx.currentTime + 0.08);
    gain.gain.setValueAtTime(0.03, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.08);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.08);
  }
}

const sfx = new SoundFX();

// ==========================================================================
// 3. BACKGROUND PARTICLE CANVAS
// ==========================================================================
function initParticleCanvas() {
  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const particles = [];
  const count = Math.min(Math.floor((width * height) / 25000), 50);

  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      radius: Math.random() * 1.6 + 0.8,
      alpha: Math.random() * 0.35 + 0.15
    });
  }

  function render() {
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0, 242, 254, ${p.alpha})`;
      ctx.fill();

      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
        if (dist < 100) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(0, 242, 254, ${0.1 * (1 - dist / 100)})`;
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(render);
  }
  render();
}

// ==========================================================================
// 4. RAG KNOWLEDGE BASE & SIMULATION DATA
// ==========================================================================
const RAG_DATA = {
  "GRU.pdf": {
    name: "GRU.pdf",
    pages: 14,
    chunks: 48,
    hash: "e9b21a8f942c7d",
    queries: {
      "How does the GRU update gate differ from LSTM forget gate?": {
        answer: "In a Gated Recurrent Unit (GRU), the **update gate (z_t)** simultaneously controls both forgetting historical activations and incorporating new candidate content.\n\nUnlike an LSTM which employs **two distinct gates** (a separate forget gate `f_t` and input gate `i_t`), the GRU couples them into a single linear interpolation:\n\n`h_t = (1 - z_t) * h_{t-1} + z_t * h~_t`\n\nThis coupling reduces model parameters by approximately **25%** without sacrificing representational capacity.",
        retrievedChunks: [
          { page: 4, score: "0.948 (MMR Top-1)", content: "The update gate z_t decides how much the unit updates its activation: h_t = (1 - z_t) h_{t-1} + z_t h~_t." },
          { page: 5, score: "0.912 (MMR Top-2)", content: "In comparison with the standard LSTM, the GRU couples input and forget mechanisms, removing separate cell states." }
        ],
        latency: "412ms"
      },
      "What is the mathematical formulation of the candidate activation?": {
        answer: "The candidate activation **h~_t** in a GRU is computed as:\n\n`h~_t = tanh(W * x_t + U * (r_t ⊙ h_{t-1}))`\n\nWhere `r_t` is the reset gate vector. When `r_t = 0`, the unit completely resets previous hidden state memory, reading the current symbol anew.",
        retrievedChunks: [
          { page: 3, score: "0.961 (MMR Top-1)", content: "The candidate state h~_t = tanh(W x_t + U (r_t * h_{t-1})). The reset gate r_t modulates prior memory." }
        ],
        latency: "395ms"
      }
    }
  },
  "Attention_Paper.pdf": {
    name: "Attention_Is_All_You_Need.pdf",
    pages: 15,
    chunks: 52,
    hash: "3a88c7f0d41e61",
    queries: {
      "How is Scaled Dot-Product Attention calculated?": {
        answer: "Scaled Dot-Product Attention is computed via:\n\n`Attention(Q, K, V) = softmax( (Q * K^T) / sqrt(d_k) ) * V`\n\nScaling by `1/sqrt(d_k)` prevents vanishing gradients during softmax when key dimensions grow large.",
        retrievedChunks: [
          { page: 3, score: "0.970 (MMR Top-1)", content: "We compute the dot products of the query with all keys, divide each by sqrt(d_k), and apply a softmax function: Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V." }
        ],
        latency: "382ms"
      }
    }
  }
};

let currentDocKey = "GRU.pdf";
let isSimulating = false;

// ==========================================================================
// 5. DIRECT IN-BROWSER PDF DRAG & DROP HANDLER
// ==========================================================================
function setupDirectPDFUpload() {
  const dropzone = document.getElementById('direct-dropzone');
  const fileInput = document.getElementById('direct-file-input');

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleUploadedPDF(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      handleUploadedPDF(e.target.files[0]);
    }
  });
}

function handleUploadedPDF(file) {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    showToast('Please upload a valid .pdf file');
    return;
  }

  sfx.playSuccess();
  showToast(`Ingesting "${file.name}" into RAM...`);

  // Simulate dynamic extraction & vectorization
  const estPages = Math.max(1, Math.round(file.size / 65000));
  const estChunks = Math.max(4, Math.round(estPages * 3.4));
  const simHash = Math.random().toString(16).substring(2, 12);

  const customKey = file.name;
  RAG_DATA[customKey] = {
    name: file.name,
    pages: estPages,
    chunks: estChunks,
    hash: simHash,
    queries: {
      "What is the main topic or objective of this document?": {
        answer: `Based on your uploaded document **${file.name}**:\n\nThe document introduces core concepts and architectural criteria. The in-memory vector index extracted **${estChunks} chunks** across **${estPages} pages**. Queries are grounded against the extracted paragraphs with zero external hallucinations.`,
        retrievedChunks: [
          { page: 1, score: "0.952 (MMR Top-1)", content: `[${file.name}] Header metadata & introductory abstract: Document ingested and parsed with recursive splitting (chunk_size=1000, overlap=200).` },
          { page: 2, score: "0.898 (MMR Top-2)", content: "Extracted context segment: Core arguments and structured specifications indexed cleanly in ephemeral RAM." }
        ],
        latency: "390ms"
      },
      "Summarize the key conclusions and takeaways": {
        answer: `Key takeaways from **${file.name}**:\n\n• The analyzed data demonstrates strong structural consistency.\n• All cited statements directly match indexed page metadata.\n• Vector retrieval completed in RAM without disk contention.`,
        retrievedChunks: [
          { page: estPages, score: "0.934 (MMR Top-1)", content: `Concluding remarks from final page (${estPages}): Validated outcomes and future research considerations.` }
        ],
        latency: "410ms"
      }
    }
  };

  currentDocKey = customKey;

  // Add button to sample docs bar
  const container = document.getElementById('sample-docs-container');
  if (container) {
    const newBtn = document.createElement('button');
    newBtn.className = 'sim-doc-btn active';
    newBtn.dataset.doc = customKey;
    newBtn.innerHTML = `<span>📄 ${file.name}</span>`;

    container.querySelectorAll('.sim-doc-btn').forEach(b => b.classList.remove('active'));
    container.prepend(newBtn);

    newBtn.addEventListener('click', () => {
      sfx.playClick();
      container.querySelectorAll('.sim-doc-btn').forEach(b => b.classList.remove('active'));
      newBtn.classList.add('active');
      currentDocKey = customKey;
      updatePlaygroundUI(RAG_DATA[customKey]);
    });
  }

  updatePlaygroundUI(RAG_DATA[customKey]);
  showToast(`✅ "${file.name}" indexed successfully!`);
}

// ==========================================================================
// 6. PLAYGROUND CONTROLLER
// ==========================================================================
function setupPlayground() {
  const docBtns = document.querySelectorAll('.sim-doc-btn');
  const simInput = document.getElementById('sim-custom-input');
  const simSubmitBtn = document.getElementById('sim-submit-btn');

  docBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      sfx.playClick();
      docBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const doc = btn.dataset.doc;
      if (RAG_DATA[doc]) {
        currentDocKey = doc;
        updatePlaygroundUI(RAG_DATA[doc]);
      }
    });
  });

  if (simSubmitBtn && simInput) {
    simSubmitBtn.addEventListener('click', () => {
      const q = simInput.value.trim();
      if (q) triggerSimulatedQA(q);
    });

    simInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const q = simInput.value.trim();
        if (q) triggerSimulatedQA(q);
      }
    });
  }

  updatePlaygroundUI(RAG_DATA[currentDocKey]);
}

function updatePlaygroundUI(data) {
  const nameEl = document.getElementById('sim-active-filename');
  const pagesEl = document.getElementById('sim-active-pages');
  const chunksEl = document.getElementById('sim-active-chunks');
  const queriesContainer = document.getElementById('preset-queries-container');

  if (nameEl) nameEl.textContent = data.name;
  if (pagesEl) pagesEl.textContent = `${data.pages} Pages`;
  if (chunksEl) chunksEl.textContent = `${data.chunks} Chunks`;

  if (queriesContainer) {
    let html = '';
    Object.keys(data.queries).forEach(q => {
      html += `<button class="query-chip" data-query="${q}">
        <span>💬 ${q}</span>
        <span>→</span>
      </button>`;
    });
    queriesContainer.innerHTML = html;

    queriesContainer.querySelectorAll('.query-chip').forEach(c => {
      c.addEventListener('click', () => {
        sfx.playClick();
        triggerSimulatedQA(c.dataset.query);
      });
    });
  }
}

async function triggerSimulatedQA(question) {
  if (isSimulating) return;
  isSimulating = true;

  const doc = RAG_DATA[currentDocKey];
  let res = doc.queries[question];

  if (!res) {
    res = {
      answer: `Based on **${doc.name}**:\n\nRegarding **"${question}"**, the document establishes clear operational principles. Vector search retrieved 4 candidate chunks via MMR, and the answer was synthesized with Gemini 3.5 without external hallucinations.`,
      retrievedChunks: [
        { page: 2, score: "0.924 (MMR Top-1)", content: `Extracted context segment for: "${question}". Validated against document tokens.` },
        { page: 4, score: "0.871 (MMR Top-2)", content: "Recursive text splitter preserves semantic continuity across chunk breaks." }
      ],
      latency: "405ms"
    };
  }

  const steps = [
    document.getElementById('pstep-1'),
    document.getElementById('pstep-2'),
    document.getElementById('pstep-3'),
    document.getElementById('pstep-4'),
    document.getElementById('pstep-5'),
    document.getElementById('pstep-6')
  ];

  steps.forEach(s => s && s.classList.remove('active', 'completed'));

  const ansEl = document.getElementById('sim-answer-target');
  const chunksEl = document.getElementById('sim-chunks-target');

  if (ansEl) {
    ansEl.innerHTML = `<span style="color: var(--cyan-primary);">⚡ Running LangChain MMR retrieval & Gemini synthesis...</span>`;
  }

  for (let i = 0; i < steps.length; i++) {
    if (steps[i]) {
      steps[i].classList.add('active');
      sfx.playPulse();
    }
    await new Promise(r => setTimeout(r, 140));
    if (steps[i]) {
      steps[i].classList.remove('active');
      steps[i].classList.add('completed');
    }
  }

  sfx.playSuccess();

  // Chunks
  if (chunksEl) {
    let chHtml = '';
    res.retrievedChunks.forEach(c => {
      chHtml += `<div class="chunk-card">
        <div class="chunk-meta">
          <span>📄 Page ${c.page}</span>
          <span>${c.score}</span>
        </div>
        <div>${c.content}</div>
      </div>`;
    });
    chunksEl.innerHTML = chHtml;
  }

  // Answer
  if (ansEl) {
    ansEl.innerHTML = res.answer
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/`(.*?)`/g, '<code style="background: rgba(0,242,254,0.15); color: var(--cyan-primary); padding: 2px 6px; border-radius: 4px; font-family: monospace;">$1</code>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n• /g, '<br>• ');
  }

  const badge = document.getElementById('sim-latency-badge');
  if (badge) badge.textContent = `⚡ Latency: ${res.latency}`;

  isSimulating = false;
}

// ==========================================================================
// 7. PRICING CALCULATOR TOGGLE
// ==========================================================================
function setupPricingToggle() {
  const pills = document.querySelectorAll('.pricing-pill');
  const proPrice = document.getElementById('pro-price');
  const entPrice = document.getElementById('ent-price');
  const cycleLabels = document.querySelectorAll('.price-cycle');

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      sfx.playClick();
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');

      const isAnnual = pill.dataset.billing === 'annual';
      if (proPrice) proPrice.textContent = isAnnual ? '22' : '29';
      if (entPrice) entPrice.textContent = isAnnual ? '79' : '99';

      cycleLabels.forEach(l => {
        l.textContent = isAnnual ? '/month (billed annually)' : '/month';
      });
    });
  });
}

// ==========================================================================
// 8. API CODE TAB SWITCHER
// ==========================================================================
const API_SNIPPETS = {
  python: `# Python SDK
import documind

client = documind.Client(api_key="your_api_key")

# 1. Ingest PDF
doc = client.documents.upload("./pdfs/GRU.pdf")

# 2. Query with MMR RAG
response = client.rag.query(
    document_id=doc.id,
    question="How does the update gate work?",
    retrieval_strategy="mmr",
    k=4
)

print(response.answer)
print("Cited Pages:", response.sources)`,

  curl: `# cURL / REST API
curl -X POST https://api.documind.ai/v1/rag/query \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "document_id": "doc_e9b21a8f",
    "question": "What is the reset gate equation?",
    "search_type": "mmr",
    "k": 4
  }'`,

  node: `// Node.js / TypeScript
import { DocuMindClient } from '@documind/sdk';

const client = new DocuMindClient({ apiKey: process.env.DOCUMIND_API_KEY });

const result = await client.rag.ask({
  documentId: 'doc_e9b21a8f',
  question: 'Summarize candidate activation',
  options: { mmr: true, k: 4 }
});

console.log(result.answer);`
};

function setupAPITabs() {
  const tabs = document.querySelectorAll('.api-tab-btn');
  const codeEl = document.getElementById('api-code-target');
  const copyBtn = document.getElementById('api-copy-btn');

  let currentTab = 'python';

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      sfx.playClick();
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      currentTab = tab.dataset.lang;
      if (codeEl && API_SNIPPETS[currentTab]) {
        codeEl.textContent = API_SNIPPETS[currentTab];
      }
    });
  });

  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const code = API_SNIPPETS[currentTab];
      navigator.clipboard.writeText(code).then(() => {
        sfx.playSuccess();
        showToast('Code copied to clipboard!');
      });
    });
  }
}

// ==========================================================================
// 9. TOAST & MODALS
// ==========================================================================
function showToast(message) {
  const toast = document.getElementById('toast-notification');
  const text = document.getElementById('toast-text');
  if (!toast || !text) return;
  text.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2600);
}

function setupModals() {
  const launchBtns = document.querySelectorAll('.open-launch-modal');
  const modal = document.getElementById('launch-modal');
  const closeBtn = document.getElementById('modal-close-btn');

  launchBtns.forEach(b => {
    b.addEventListener('click', (e) => {
      e.preventDefault();
      sfx.playClick();
      if (modal) modal.classList.add('open');
    });
  });

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => modal.classList.remove('open'));
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('open');
    });
  }
}

// ==========================================================================
// 10. INITIALIZATION
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  setupThemeSwitcher();
  initParticleCanvas();
  setupDirectPDFUpload();
  setupPlayground();
  setupPricingToggle();
  setupAPITabs();
  setupModals();

  // Sound toggle button in navbar
  const soundBtn = document.getElementById('sound-toggle-btn');
  if (soundBtn) {
    soundBtn.addEventListener('click', () => {
      const active = sfx.toggle();
      soundBtn.style.opacity = active ? '1' : '0.4';
      showToast(active ? 'Audio Cues Active' : 'Audio Cues Muted');
    });
  }
});
