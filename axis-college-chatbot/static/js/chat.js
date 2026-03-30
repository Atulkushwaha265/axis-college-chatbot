// Axis Colleges AI Chatbot - Frontend JavaScript

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offsetTop = target.offsetTop - 76; // Account for fixed navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.classList.add('fade-in');
                    observer.unobserve(img);
                }
            });
        });

        // Observe all images except hero image
        document.querySelectorAll('img:not(.hero-image)').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Navbar scroll effect
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        const currentScroll = window.pageYOffset;
        
        if (currentScroll <= 0) {
            navbar.classList.remove('scroll-up');
            return;
        }
        
        if (currentScroll > lastScroll && !navbar.classList.contains('scroll-down')) {
            navbar.classList.remove('scroll-up');
            navbar.classList.add('scroll-down');
        } else if (currentScroll < lastScroll && navbar.classList.contains('scroll-down')) {
            navbar.classList.remove('scroll-down');
            navbar.classList.add('scroll-up');
        }
        lastScroll = currentScroll;
    });

    // Initialize animations on scroll
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.animate-fade-in, .animate-fade-in-delay, .animate-fade-in-delay-2');
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementBottom = element.getBoundingClientRect().bottom;
            
            if (elementTop < window.innerHeight && elementBottom > 0) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Initial check
});

class ChatBot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.chatForm = document.getElementById('chatForm');
        this.sendButton = document.getElementById('sendButton');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.clearChatBtn = document.getElementById('clearChat');
        
        // Advanced AI features
        this.sessionId = this.generateSessionId();
        this.messageHistory = [];
        this.isTyping = false;
        
        this.init();
    }
    
    generateSessionId() {
        // Generate unique session ID for context memory
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    init() {
        // Event Listeners
        this.chatForm.addEventListener('submit', (e) => this.sendMessage(e));
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage(e);
            }
        });
        
        this.clearChatBtn.addEventListener('click', () => this.clearChat());
        
        // Quick action buttons
        document.querySelectorAll('.quick-action').forEach(button => {
            button.addEventListener('click', () => {
                const query = button.getAttribute('data-query');
                this.messageInput.value = query;
                this.sendMessage(new Event('submit'));
            });
        });
        
        // Auto-resize textarea if needed
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
        
        // Focus on input
        this.messageInput.focus();
        
        // Load chat history from localStorage
        this.loadChatHistory();
    }

    async sendMessage(e) {
        e.preventDefault();
        
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Disable send button
        this.setSendButtonState(false);
        
        try {
            // Send message to backend with session ID
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message,
                    session_id: this.sessionId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add bot response
            this.addMessage(data.response, 'bot', data.timestamp);
            
            // Save to localStorage
            this.saveChatHistory();
            
            // Scroll to bottom
            this.scrollToBottom();
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again later.', 'bot');
        } finally {
            // Re-enable send button
            this.setSendButtonState(true);
            this.messageInput.focus();
        }
    }

    addMessage(content, sender, timestamp = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message} mb-3`;
        
        const time = timestamp || new Date().toLocaleString();
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="d-flex">
                    <div class="message-content">
                        <div class="message-bubble">
                            <p class="mb-0">${this.escapeHtml(content)}</p>
                        </div>
                        <div class="message-time small text-muted mt-1 text-end">
                            <i class="far fa-clock me-1"></i>${this.formatTime(time)}
                        </div>
                    </div>
                    <div class="bot-avatar ms-2">
                        <i class="fas fa-user"></i>
                    </div>
                </div>
            `;
        } else {
            // Format bot message with markdown-like syntax
            const formattedContent = this.formatBotMessage(content);
            messageDiv.innerHTML = `
                <div class="d-flex">
                    <div class="bot-avatar me-2">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-bubble">
                            ${formattedContent}
                        </div>
                        <div class="message-time small text-muted mt-1">
                            <i class="far fa-clock me-1"></i>${this.formatTime(time)}
                        </div>
                    </div>
                </div>
            `;
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Add animation
        setTimeout(() => {
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 10);
    }

    formatBotMessage(content) {
        // Convert markdown-like formatting to HTML
        let formatted = this.escapeHtml(content);
        
        // Bold text **text** -> <strong>text</strong>
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic text *text* -> <em>text</em>
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert line breaks to <br>
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Convert bullet points
        formatted = formatted.replace(/• (.*)/g, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        // Convert numbered lists
        formatted = formatted.replace(/^\d+\. (.*)/gm, '<li>$1</li>');
        
        // Convert emojis (basic support)
        const emojiMap = {
            '🎓': '🎓',
            '💰': '💰',
            '📚': '📚',
            '📅': '📅',
            '📋': '📋',
            '📝': '📝',
            '🏢': '🏢',
            '💼': '💼',
            '📊': '📊',
            '🎯': '🎯',
            '📞': '📞',
            '📧': '📧',
            '📍': '📍',
            '🕐': '🕐',
            '🎉': '🎉',
            '🗓️': '🗓️',
            '👋': '👋',
            '❓': '❓',
            '💡': '💡',
            '🔒': '🔒',
            '📈': '📈',
            '🏆': '🏆',
            '🌟': '🌟'
        };
        
        Object.keys(emojiMap).forEach(emoji => {
            const regex = new RegExp(emoji.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
            formatted = formatted.replace(regex, emojiMap[emoji]);
        });
        
        // Convert URLs to links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        formatted = formatted.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
        
        // Convert email addresses to mailto links
        const emailRegex = /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
        formatted = formatted.replace(emailRegex, '<a href="mailto:$1">$1</a>');
        
        // Convert phone numbers to tel links
        const phoneRegex = /(\+?[\d\s-]{10,})/g;
        formatted = formatted.replace(phoneRegex, '<a href="tel:$1">$1</a>');
        
        return formatted;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) {
            return 'Just now';
        } else if (diffMins < 60) {
            return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        } else if (diffMins < 1440) {
            const hours = Math.floor(diffMins / 60);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        }
    }

    showTypingIndicator() {
        this.typingIndicator.classList.remove('d-none');
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.typingIndicator.classList.add('d-none');
    }

    setSendButtonState(enabled) {
        this.sendButton.disabled = !enabled;
        if (enabled) {
            this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        } else {
            this.sendButton.innerHTML = '<span class="loading"></span>';
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            // Keep only the welcome message
            const messages = this.chatMessages.querySelectorAll('.message');
            messages.forEach((message, index) => {
                if (index > 0) {
                    message.remove();
                }
            });
            
            // Clear localStorage
            localStorage.removeItem('axisChatHistory');
            
            // Show confirmation
            this.addMessage('Chat history cleared. How can I help you today?', 'bot');
        }
    }

    saveChatHistory() {
        try {
            const messages = [];
            const messageElements = this.chatMessages.querySelectorAll('.message');
            
            messageElements.forEach(element => {
                const isUser = element.classList.contains('user-message');
                const content = element.querySelector('.message-bubble').textContent.trim();
                const time = element.querySelector('.message-time').textContent.trim();
                
                if (content && !content.includes('Welcome to Axis Colleges AI Assistant!')) {
                    messages.push({
                        sender: isUser ? 'user' : 'bot',
                        content: content,
                        time: time
                    });
                }
            });
            
            localStorage.setItem('axisChatHistory', JSON.stringify(messages));
        } catch (error) {
            console.error('Error saving chat history:', error);
        }
    }

    loadChatHistory() {
        try {
            const savedHistory = localStorage.getItem('axisChatHistory');
            if (savedHistory) {
                const messages = JSON.parse(savedHistory);
                messages.forEach(message => {
                    this.addMessage(message.content, message.sender, message.time);
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    // Utility function to check if online
    isOnline() {
        return navigator.onLine;
    }

    // Show connection status
    showConnectionStatus() {
        if (!this.isOnline()) {
            this.addMessage('You appear to be offline. Some features may not work properly.', 'bot');
        }
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const chatBot = new ChatBot();
    
    // Show connection status
    chatBot.showConnectionStatus();
    
    // Listen for online/offline events
    window.addEventListener('online', () => {
        console.log('Back online');
    });
    
    window.addEventListener('offline', () => {
        console.log('Gone offline');
        chatBot.addMessage('You appear to be offline. Please check your internet connection.', 'bot');
    });
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            chatBot.messageInput.focus();
            chatBot.messageInput.select();
        }
        
        // Escape to clear input
        if (e.key === 'Escape') {
            chatBot.messageInput.value = '';
            chatBot.messageInput.blur();
        }
    });
    
    // Service Worker registration for PWA (optional)
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    }
});

// Error handling
window.addEventListener('error', (e) => {
    console.error('JavaScript error:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
});

// Performance monitoring
window.addEventListener('load', () => {
    if ('performance' in window) {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        console.log(`Page load time: ${loadTime}ms`);
    }
});
