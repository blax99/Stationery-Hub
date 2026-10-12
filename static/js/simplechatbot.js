document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('chat-toggle');
    const box = document.getElementById('chat-box');
    const input = document.getElementById('chat-input');
    const send = document.getElementById('chat-send');
    const messages = document.getElementById('chat-messages');

    // Toggle chat box
    toggle.addEventListener('click', () => {
        const isHidden = box.style.display === 'none';
        box.style.display = isHidden ? 'flex' : 'none';
        toggle.textContent = isHidden ? '✕' : '💬';
        if (isHidden) input.focus();
    });

    // Send message
    send.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;
        input.value = '';

        // Show user message
        messages.innerHTML += `<p style="margin:6px 0;text-align:right;color:#7c5cfc;font-size:13px;">${escapeHtml(text)}</p>`;
        messages.scrollTop = messages.scrollHeight;

        // Show "typing..." indicator
        const typingId = 'typing-' + Date.now();
        messages.innerHTML += `<p id="${typingId}" style="margin:6px 0;color:#999;font-size:13px;font-style:italic;">Typing...</p>`;
        messages.scrollTop = messages.scrollHeight;

        try {
            const res = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: 'message=' + encodeURIComponent(text)
            });

            const data = await res.json();

            // Remove typing indicator
            const typing = document.getElementById(typingId);
            if (typing) typing.remove();

            // Show bot reply
            messages.innerHTML += `<p style="margin:6px 0;color:#333;font-size:13px;">${escapeHtml(data.reply)}</p>`;
        } catch (err) {
            const typing = document.getElementById(typingId);
            if (typing) typing.remove();
            messages.innerHTML += `<p style="margin:6px 0;color:red;font-size:13px;">Error. Try again.</p>`;
        }

        messages.scrollTop = messages.scrollHeight;
    }

    function getCookie(name) {
        let v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return v ? v.pop() : '';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});   