/**
 * script.js
 * =========
 * Frontend JavaScript for Sunrise College AI Chatbot
 * Features: send messages, typing effect, auto-scroll, dark/light theme, quick chips
 */

// ─── DOM References ──────────────────────────────────────────────────────────
const chatMessages   = document.getElementById('chatMessages');
const userInput      = document.getElementById('userInput');
const sendBtn        = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const themeToggle    = document.getElementById('themeToggle');
const clearHistory   = document.getElementById('clearHistory');

// ─── State ───────────────────────────────────────────────────────────────────
let isDark = localStorage.getItem('theme') === 'dark';
let isBotTyping = false;

// ─── Init ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Apply saved theme
  applyTheme(isDark);

  // Show welcome message
  showWelcomeMessage();

  // Auto-resize textarea
  userInput.addEventListener('input', autoResize);

  // Attach event listeners
  sendBtn.addEventListener('click', handleSend);
  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  // Quick topic chips
  document.querySelectorAll('.topic-chip, .sidebar-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const query = btn.dataset.query;
      if (query) {
        // Scroll to chat
        document.querySelector('.chatbot-section').scrollIntoView({ behavior: 'smooth' });
        setTimeout(() => sendMessage(query), 600);
      }
    });
  });

  // Theme toggle
  themeToggle.addEventListener('click', () => {
    isDark = !isDark;
    applyTheme(isDark);
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  });

  // Clear history
  clearHistory.addEventListener('click', async () => {
    chatMessages.innerHTML = '';
    showWelcomeMessage();
    // Clear on server too
    try {
      await fetch('/api/clear', { method: 'POST' });
    } catch (e) { /* Silently ignore */ }
  });

  // Active nav highlighting on scroll
  setupScrollNav();
});

// ─── Theme ───────────────────────────────────────────────────────────────────
function applyTheme(dark) {
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  themeToggle.textContent = dark ? '☀️' : '🌙';
  themeToggle.title = dark ? 'Switch to Light Mode' : 'Switch to Dark Mode';
}

// ─── Welcome Message ─────────────────────────────────────────────────────────
function showWelcomeMessage() {
  const welcomeDiv = document.createElement('div');
  welcomeDiv.className = 'welcome-msg';
  welcomeDiv.innerHTML = `
    <span class="welcome-icon">🎓</span>
    <h3>Welcome to Sunrise College!</h3>
    <p>Hi there! I'm <strong>SunBot</strong>, your AI college assistant.<br/>
    Ask me anything about admissions, courses, fees, hostel, placement and more!</p>
  `;
  chatMessages.appendChild(welcomeDiv);

  // Add initial bot greeting after a short delay
  setTimeout(() => {
    addMessage(
      "Hello! 👋 Welcome to Sunrise College. I'm SunBot, your personal AI assistant.\n\nYou can ask me about:\n• 🎓 Admissions & Eligibility\n• 📚 Courses & Programs\n• 💰 Fees & Scholarships\n• 🏠 Hostel Facilities\n• 🏢 Placements\n• 📅 Exams\n• 👨‍🏫 Faculty\n• 📞 Contact Details\n\nHow can I help you today?",
      'bot'
    );
  }, 500);
}

// ─── Add Message to Chat ──────────────────────────────────────────────────────
function addMessage(text, sender) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}`;

  const now = new Date();
  const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const avatarEmoji = sender === 'user' ? '👤' : '🤖';

  msgDiv.innerHTML = `
    <div class="msg-avatar">${avatarEmoji}</div>
    <div class="msg-content">
      <div class="msg-bubble">${formatMessage(text)}</div>
      <span class="msg-time">${time}</span>
    </div>
  `;

  chatMessages.appendChild(msgDiv);
  scrollToBottom();
  return msgDiv;
}

// ─── Format Bot Response Text ────────────────────────────────────────────────
function formatMessage(text) {
  // Convert **bold** to <strong>
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Convert line breaks to <br>
  text = text.replace(/\n/g, '<br/>');

  // Convert bullet points (•) — keep as-is (they're unicode)
  // Convert numbered lists: "1. Item" formatting
  text = text.replace(/(\d+\.\s)/g, '<span style="color:var(--primary);font-weight:600;">$1</span>');

  // Convert ✅ ❌ 📋 style emojis as-is (browsers handle them natively)
  return text;
}

// ─── Typing Effect for Bot ───────────────────────────────────────────────────
function showTyping() {
  typingIndicator.classList.add('visible');
  scrollToBottom();
}

function hideTyping() {
  typingIndicator.classList.remove('visible');
}

// ─── Scroll to Bottom ────────────────────────────────────────────────────────
function scrollToBottom() {
  setTimeout(() => {
    chatMessages.scrollTo({
      top: chatMessages.scrollHeight,
      behavior: 'smooth'
    });
  }, 50);
}

// ─── Send Message ─────────────────────────────────────────────────────────────
async function sendMessage(text) {
  if (isBotTyping) return;

  const message = (text || userInput.value).trim();
  if (!message) return;

  // Clear input
  userInput.value = '';
  userInput.style.height = 'auto';
  sendBtn.disabled = true;
  isBotTyping = true;

  // Show user's message
  addMessage(message, 'user');

  // Show typing indicator with a small delay
  setTimeout(() => showTyping(), 100);

  try {
    // Call the Flask backend API
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();

    // Simulate realistic typing delay (500ms – 1500ms based on response length)
    const typingDelay = Math.min(1500, Math.max(600, data.response.length * 5));

    setTimeout(() => {
      hideTyping();
      addMessage(data.response, 'bot');
      sendBtn.disabled = false;
      isBotTyping = false;
    }, typingDelay);

  } catch (error) {
    console.error('Chat error:', error);
    setTimeout(() => {
      hideTyping();
      addMessage(
        "⚠️ I'm having trouble connecting right now. Please check that the Flask server is running, or try again in a moment.",
        'bot'
      );
      sendBtn.disabled = false;
      isBotTyping = false;
    }, 800);
  }
}

// ─── Handle Send (from button or Enter key) ───────────────────────────────────
function handleSend() {
  sendMessage();
}

// ─── Auto-resize Textarea ────────────────────────────────────────────────────
function autoResize() {
  userInput.style.height = 'auto';
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
}

// ─── Active Nav Link on Scroll ───────────────────────────────────────────────
function setupScrollNav() {
  const sections = ['home', 'chatbot', 'about', 'contact'];
  const navLinks = document.querySelectorAll('.nav-link');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navLinks.forEach(link => link.classList.remove('active'));
        const activeLink = document.querySelector(`.nav-link[href="#${entry.target.id}"]`);
        if (activeLink) activeLink.classList.add('active');
      }
    });
  }, { threshold: 0.3 });

  sections.forEach(id => {
    const el = document.getElementById(id);
    if (el) observer.observe(el);
  });
}

// ─── Minimize Chat (header button) ───────────────────────────────────────────
const minimizeBtn = document.getElementById('minimizeBtn');
if (minimizeBtn) {
  minimizeBtn.addEventListener('click', () => {
    const chatMain = document.querySelector('.chat-main');
    const isMinimized = chatMain.style.opacity === '0.3';
    chatMain.style.opacity = isMinimized ? '1' : '0.3';
    minimizeBtn.textContent = isMinimized ? '–' : '+';
  });
}