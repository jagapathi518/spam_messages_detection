// Spam Shield Interactive Web Application Logic
document.addEventListener('DOMContentLoaded', () => {
  // Navigation Tabs
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const panel = document.getElementById(targetId);
      if (panel) panel.classList.add('active');

      if (targetId === 'telemetry') loadTelemetry();
      if (targetId === 'batch' && !window.batchLoaded) runBatchScan();
    });
  });

  // Sample Presets
  const presets = {
    kyc: {
      text: 'Dear SBI Customer, your YONO account is blocked today due to pending PAN KYC. Update immediately at http://192.168.1.10/sbi-verify.apk to avoid permanent suspension.',
      sender: '+919876543210'
    },
    electricity: {
      text: 'Dear consumer, your electricity connection will be cut off tonight at 9:30 PM by electricity office because your previous month bill was not updated. Immediately contact officer 9876543210.',
      sender: '+919988776655'
    },
    challan: {
      text: 'Notice: Pending traffic fine of Rs 1,000 for vehicle DL01AB1234. Pay immediately or vehicle RC will be cancelled: http://echallan-parivahan.apk',
      sender: '+918888888888'
    },
    otp: {
      text: 'Your Swiggy verification code is 492810. Valid for 10 minutes. Do not share this OTP with anyone.',
      sender: 'AX-SWIGGY'
    },
    debit: {
      text: 'Dear SBI Customer, INR 5,000.00 debited from A/c XX1234 on 15-Oct-26 at 10:15:30. Avail Bal: INR 42,350.00. Call 1800112211 if not you.',
      sender: 'VM-SBINB'
    },
    upi: {
      text: 'Congratulations! You won Rs 50,000 cash bonus in PhonePe Diwali spin! Pay processing fee Rs 499 via UPI to claim immediately: upi://pay?pa=scam@upi',
      sender: '+917777777777'
    }
  };

  document.querySelectorAll('.preset-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const key = chip.getAttribute('data-preset');
      if (presets[key]) {
        document.getElementById('messageText').value = presets[key].text;
        document.getElementById('senderId').value = presets[key].sender;
      }
    });
  });

  // Paste from clipboard
  const pasteBtn = document.getElementById('pasteBtn');
  if (pasteBtn) {
    pasteBtn.addEventListener('click', async () => {
      try {
        const text = await navigator.clipboard.readText();
        if (text) document.getElementById('messageText').value = text;
      } catch (_) {
        showToast('Please press Ctrl+V to paste.', 'error');
      }
    });
  }

  // Scan Button Event
  const scanBtn = document.getElementById('scanBtn');
  if (scanBtn) {
    scanBtn.addEventListener('click', runSingleScan);
  }

  // Batch Filter Buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      filterBatchItems(btn.getAttribute('data-filter'));
    });
  });

  // Feedback Modal handlers
  const feedbackModal = document.getElementById('feedbackModal');
  const openFeedbackBtn = document.getElementById('openFeedbackBtn');
  const closeFeedbackBtn = document.getElementById('closeFeedbackBtn');
  const submitFeedbackBtn = document.getElementById('submitFeedbackBtn');

  if (openFeedbackBtn && feedbackModal) {
    openFeedbackBtn.addEventListener('click', () => {
      feedbackModal.classList.add('active');
    });
  }
  if (closeFeedbackBtn && feedbackModal) {
    closeFeedbackBtn.addEventListener('click', () => {
      feedbackModal.classList.remove('active');
    });
  }
  if (submitFeedbackBtn) {
    submitFeedbackBtn.addEventListener('click', submitFeedback);
  }

  // Auto-run initial scan and telemetry on load
  runSingleScan();
  loadTelemetry();
});

// Toast Notification
function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.className = `toast ${type}`;
  toast.style.display = 'block';
  setTimeout(() => {
    toast.style.display = 'none';
  }, 3500);
}

// Draw Animated Canvas Gauge
function drawGauge(score, color) {
  const canvas = document.getElementById('gaugeCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const size = 180;

  canvas.width = size * dpr;
  canvas.height = size * dpr;
  ctx.scale(dpr, dpr);

  const centerX = size / 2;
  const centerY = size / 2;
  const radius = size / 2 - 14;

  ctx.clearRect(0, 0, size, size);

  // Background arc
  ctx.beginPath();
  ctx.arc(centerX, centerY, radius, Math.PI * 0.75, Math.PI * 2.25);
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.lineWidth = 12;
  ctx.lineCap = 'round';
  ctx.stroke();

  // Active progress arc
  const sweep = Math.PI * 1.5 * Math.max(0.02, Math.min(score, 1.0));
  ctx.beginPath();
  ctx.arc(centerX, centerY, radius, Math.PI * 0.75, Math.PI * 0.75 + sweep);
  ctx.strokeStyle = color;
  ctx.lineWidth = 12;
  ctx.lineCap = 'round';
  ctx.stroke();
}

// Single Scan Execution
async function runSingleScan() {
  const textInput = document.getElementById('messageText');
  const senderInput = document.getElementById('senderId');
  const scanBtn = document.getElementById('scanBtn');

  const text = textInput ? textInput.value.trim() : '';
  const sender_id = senderInput ? senderInput.value.trim() : '';

  if (!text) {
    showToast('Please enter or paste a message to analyze.', 'error');
    return;
  }

  scanBtn.disabled = true;
  scanBtn.innerHTML = '<span>Analyzing Multi-Layer Defense...</span>';

  try {
    const t0 = performance.now();
    const res = await fetch('/api/v1/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, sender_id })
    });
    const data = await res.json();
    const latency = (performance.now() - t0).toFixed(1);

    renderScanResult(data, latency);
  } catch (err) {
    showToast('Server connection error. Ensure FastAPI is running.', 'error');
  } finally {
    scanBtn.disabled = false;
    scanBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg> <span>Scan Message</span>';
  }
}

// Render Results
function renderScanResult(data, clientLatency) {
  const resultCard = document.getElementById('resultCard');
  if (!resultCard) return;

  const scoreEl = document.getElementById('gaugeScore');
  const pillEl = document.getElementById('verdictPill');
  const latencyEl = document.getElementById('latencyVal');
  const layersCountEl = document.getElementById('layersCount');
  const reasonsListEl = document.getElementById('reasonsList');
  const layerTagsEl = document.getElementById('layerTags');

  const riskPct = Math.round(data.risk_score * 100);
  let color = '#10b981'; // Green
  let pillClass = 'safe';

  if (data.label === 'SPAM') {
    color = '#ef4444'; // Red
    pillClass = 'spam';
  } else if (data.label === 'SUSPICIOUS') {
    color = '#f59e0b'; // Amber
    pillClass = 'suspicious';
  }

  drawGauge(data.risk_score, color);

  if (scoreEl) {
    scoreEl.textContent = `${riskPct}%`;
    scoreEl.style.color = color;
  }

  if (pillEl) {
    pillEl.className = `verdict-pill ${pillClass}`;
    pillEl.innerHTML = `<span>${data.label}</span> <span style="font-size:11px; opacity:0.85;">(${(data.confidence * 100).toFixed(0)}% conf)</span>`;
  }

  if (latencyEl) latencyEl.textContent = `${data.latency_ms || clientLatency} ms`;
  if (layersCountEl) layersCountEl.textContent = `${(data.layers_used || []).length} Layers`;

  // Reasons list
  if (reasonsListEl) {
    reasonsListEl.innerHTML = (data.reasons || []).map(r => `
      <div class="reason-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        <span>${escapeHtml(r)}</span>
      </div>
    `).join('');
  }

  // Layer badges
  if (layerTagsEl) {
    layerTagsEl.innerHTML = (data.layers_used || []).map(l => `
      <span class="layer-tag">${escapeHtml(l)}</span>
    `).join('');
  }

  // Store for feedback
  window.lastScannedText = data.text_preview || document.getElementById('messageText').value;
  window.lastPredictedLabel = data.label;
}

// Batch Inbox Scanner
window.batchResults = [];
async function runBatchScan() {
  const batchContainer = document.getElementById('inboxList');
  if (!batchContainer) return;

  batchContainer.innerHTML = '<div style="text-align:center; padding:32px; color:var(--text-secondary);">Scanning mobile inbox batch...</div>';

  const sampleInbox = [
    { sender_id: 'VM-HDFCBK', text: 'Dear Customer, your NetBanking access is locked due to unverified KYC. Click http://192.168.0.12/hdfc-kyc to update immediately.' },
    { sender_id: 'AX-SWIGGY', text: 'Your Swiggy order from Biryani Blues is arriving in 15 mins. Track your rider on app.' },
    { sender_id: '+919988776655', text: 'Electricity Alert: Power will be disconnected tonight at 9:30 PM for unpaid bill. Call 9876543210 immediately to pay.' },
    { sender_id: 'VK-SBINB', text: 'Dear Customer, INR 3,500.00 debited from A/c XX8921 on 15-Oct-26. Avail Bal: INR 28,140.00. If not you, call 1800112211.' },
    { sender_id: '+918888888888', text: 'You have won Rs 50,000 cash reward in lucky draw! Pay 499 processing fee via UPI to claim prize now: upi://pay?pa=scam@upi' },
    { sender_id: '+919123456789', text: 'Hey Rahul, let us catch up this weekend for coffee!' },
    { sender_id: '+917777777777', text: 'Part-time job: Earn Rs 4,000 daily from home by liking videos. Contact HR on Telegram @scamjob' },
    { sender_id: 'AX-ZEPTO', text: 'Your Zepto groceries order #ZP-9812 has been delivered. Enjoy 10-min delivery!' }
  ];

  try {
    const res = await fetch('/api/v1/scan/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: sampleInbox })
    });
    const data = await res.json();
    window.batchResults = data.results || [];
    window.batchLoaded = true;

    // Update KPIs
    document.getElementById('kpiTotal').textContent = data.total;
    document.getElementById('kpiSpam').textContent = data.spam_count;
    document.getElementById('kpiSuspicious').textContent = data.suspicious_count;
    document.getElementById('kpiSafe').textContent = data.safe_count;

    renderBatchList(window.batchResults);
  } catch (err) {
    batchContainer.innerHTML = '<div style="text-align:center; padding:32px; color:var(--spam-red);">Failed to load batch inbox.</div>';
  }
}

function filterBatchItems(filter) {
  if (!window.batchResults) return;
  if (filter === 'ALL') {
    renderBatchList(window.batchResults);
  } else {
    renderBatchList(window.batchResults.filter(i => i.label === filter));
  }
}

function renderBatchList(items) {
  const container = document.getElementById('inboxList');
  if (!container) return;

  if (items.length === 0) {
    container.innerHTML = '<div style="text-align:center; padding:32px; color:var(--text-secondary);">No messages in this category.</div>';
    return;
  }

  container.innerHTML = items.map(item => {
    let color = '#10b981';
    if (item.label === 'SPAM') color = '#ef4444';
    else if (item.label === 'SUSPICIOUS') color = '#f59e0b';

    return `
      <div class="inbox-item" onclick="loadItemIntoScanner('${escapeQuote(item.text_preview || '')}', '${escapeQuote(item.sender_id || '')}')">
        <div class="inbox-header">
          <span class="inbox-sender">${escapeHtml(item.sender_id || 'Unknown Sender')}</span>
          <span style="font-size:11px; font-weight:800; color:${color}; padding:2px 8px; border-radius:4px; background:${color}22; border:1px solid ${color}44;">
            ${item.label}
          </span>
        </div>
        <div class="inbox-text">${escapeHtml(item.text_preview || '')}</div>
        <div style="font-size:11px; color:var(--text-muted); margin-top:8px;">
          ${escapeHtml(item.reasons?.[0] || 'Evaluated')} • ${item.latency_ms} ms
        </div>
      </div>
    `;
  }).join('');
}

function loadItemIntoScanner(text, sender) {
  document.getElementById('messageText').value = text;
  document.getElementById('senderId').value = sender;
  document.querySelector('.tab-btn[data-tab="scanner"]').click();
  runSingleScan();
}

// Telemetry & Stats
async function loadTelemetry() {
  try {
    const res = await fetch('/api/v1/stats');
    const data = await res.json();

    document.getElementById('statTotalScans').textContent = data.total_scans;
    document.getElementById('statSpamDetected').textContent = data.spam_detected;
    document.getElementById('statCleanVerified').textContent = data.safe_verified;
    document.getElementById('statAvgLatency').textContent = `${data.avg_latency_ms} ms`;
    document.getElementById('storageBadge').textContent = data.storage;

    // Recent Scans Table
    const tableBody = document.getElementById('recentScansBody');
    if (tableBody && data.recent_scans) {
      tableBody.innerHTML = data.recent_scans.map(s => {
        let col = '#10b981';
        if (s.label === 'SPAM') col = '#ef4444';
        else if (s.label === 'SUSPICIOUS') col = '#f59e0b';

        return `
          <tr>
            <td style="padding:10px; border-bottom:1px solid var(--border-color); font-size:12px; font-family:monospace;">${s.id.slice(0, 8)}...</td>
            <td style="padding:10px; border-bottom:1px solid var(--border-color); font-size:13px; max-width:280px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${escapeHtml(s.text_preview)}</td>
            <td style="padding:10px; border-bottom:1px solid var(--border-color);"><span style="font-size:11px; font-weight:bold; color:${col};">${s.label}</span></td>
            <td style="padding:10px; border-bottom:1px solid var(--border-color); font-size:12px;">${(s.confidence * 100).toFixed(0)}%</td>
            <td style="padding:10px; border-bottom:1px solid var(--border-color); font-size:12px; color:var(--text-muted);">${s.latency_ms} ms</td>
          </tr>
        `;
      }).join('');
    }
  } catch (_) {}
}

// Submit Feedback
async function submitFeedback() {
  const correctionEl = document.querySelector('input[name="correction"]:checked');
  const commentsEl = document.getElementById('feedbackComments');

  const payload = {
    text: window.lastScannedText || document.getElementById('messageText').value,
    predicted_label: window.lastPredictedLabel || 'SAFE',
    user_correction: correctionEl ? correctionEl.value : 'SPAM',
    comments: commentsEl ? commentsEl.value.trim() : ''
  };

  try {
    const res = await fetch('/api/v1/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      document.getElementById('feedbackModal').classList.remove('active');
      showToast('Thank you! Your feedback helps continuously improve our ML models.');
      loadTelemetry();
    }
  } catch (_) {
    showToast('Failed to record feedback.', 'error');
  }
}

// Utility Helpers
function escapeHtml(str) {
  return str.replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[tag] || tag));
}

function escapeQuote(str) {
  return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}
