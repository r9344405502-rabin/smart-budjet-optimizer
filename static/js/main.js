/* ===================================================================
   SMART BUDGET OPTIMISER - CLIENT APPLICATION LOGIC
   =================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initDemoCalculator();
    initChatAssistant();
});

// -------------------------------------------------------------
// PUBLIC INTERACTIVE AI DEMO ENGINE
// -------------------------------------------------------------
function initDemoCalculator() {
    const runDemoBtn = document.getElementById('run-demo-btn');
    if (!runDemoBtn) return;

    runDemoBtn.addEventListener('click', () => {
        const income = parseFloat(document.getElementById('demo-income').value) || 4500;
        const rent = parseFloat(document.getElementById('demo-rent').value) || 1400;
        const groceries = parseFloat(document.getElementById('demo-groceries').value) || 500;
        const dining = parseFloat(document.getElementById('demo-dining').value) || 350;
        const subs = parseFloat(document.getElementById('demo-subs').value) || 120;
        const other = parseFloat(document.getElementById('demo-other').value) || 400;

        const totalExpenses = rent + groceries + dining + subs + other;
        const netSavings = income - totalExpenses;
        const savingsRate = Math.round((netSavings / income) * 100);

        // Update UI
        document.getElementById('demo-total-expenses').innerText = `$${totalExpenses.toLocaleString()}`;
        document.getElementById('demo-remaining-balance').innerText = `$${netSavings.toLocaleString()}`;
        document.getElementById('demo-savings-rate').innerText = `${savingsRate}%`;

        // Flag unwanted expenses
        const flaggedList = document.getElementById('demo-flagged-list');
        flaggedList.innerHTML = '';

        const flags = [];
        if (subs > 80) {
            flags.push({
                item: 'Digital Subscriptions ($' + subs + ')',
                reason: 'Recurring SaaS/Streaming fees exceed 2% of net income. AI recommends auditing duplicate services for instant $40-60/mo savings.'
            });
        }
        if (dining > 250) {
            flags.push({
                item: 'Food Delivery & Dining Out ($' + dining + ')',
                reason: 'Dining and takeout represent a disproportionate spend compared to groceries. Capping to $200/mo creates immediate surplus.'
            });
        }
        if (rent > income * 0.4) {
            flags.push({
                item: 'Housing Ratio Alert ($' + rent + ')',
                reason: 'Rent exceeds 40% of income. Recommended healthy ceiling is 30-33%.'
            });
        }

        if (flags.length === 0) {
            flaggedList.innerHTML = '<div style="color: #10B981; font-weight: 500;">✨ Great fiscal discipline! No major unwanted or excessive expenses detected.</div>';
        } else {
            flags.forEach(f => {
                const item = document.createElement('div');
                item.style.cssText = 'background: rgba(244, 63, 94, 0.08); border-left: 3px solid #F43F5E; padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 0.5rem;';
                item.innerHTML = `<strong style="color: #F43F5E;">⚠️ ${f.item}</strong><p style="font-size: 0.85rem; color: #CBD5E1; margin-top: 0.2rem;">${f.reason}</p>`;
                flaggedList.appendChild(item);
            });
        }

        const resultsContainer = document.getElementById('demo-results');
        if (resultsContainer) {
            resultsContainer.style.display = 'block';
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
        }
    });
}

// -------------------------------------------------------------
// AI FINANCIAL ASSISTANT CHAT
// -------------------------------------------------------------
function initChatAssistant() {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');
    const messagesBox = document.getElementById('chat-messages');

    if (!chatInput || !sendBtn || !messagesBox) return;

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Append User Message
        appendBubble('user', text);
        chatInput.value = '';
        chatInput.disabled = true;
        sendBtn.disabled = true;

        // Show typing indicator
        const typingIndicator = appendBubble('assistant', '🤖 Analyzing your financial query...');

        try {
            const csrfToken = getCookie('csrftoken');
            const res = await fetch('/api/ai/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();
            typingIndicator.innerHTML = formatMarkdown(data.reply);
        } catch (err) {
            typingIndicator.innerText = "Error communicating with AI assistant. Please try again.";
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
            messagesBox.scrollTop = messagesBox.scrollHeight;
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function appendBubble(sender, text) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${sender}`;
        bubble.innerHTML = text;
        messagesBox.appendChild(bubble);
        messagesBox.scrollTop = messagesBox.scrollHeight;
        return bubble;
    }

    function formatMarkdown(content) {
        if (!content) return '';
        return content
            .replace(/### (.*?)\n/g, '<h4 style="margin: 0.5rem 0; font-weight:700;">$1</h4>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');
    }
}

// Helper to get Django CSRF Cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
