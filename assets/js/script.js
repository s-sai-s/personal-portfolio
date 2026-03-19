"use strict";

// element toggle function
const elementToggleFunc = function (elem) {
  elem.classList.toggle("active");
};

// sidebar variables
const sidebar = document.querySelector("[data-sidebar]");
const sidebarBtn = document.querySelector("[data-sidebar-btn]");

// sidebar toggle functionality for mobile
sidebarBtn.addEventListener("click", function () {
  elementToggleFunc(sidebar);
});

// testimonials variables
const testimonialsItem = document.querySelectorAll("[data-testimonials-item]");
const modalContainer = document.querySelector("[data-modal-container]");
const modalCloseBtn = document.querySelector("[data-modal-close-btn]");
const overlay = document.querySelector("[data-overlay]");

// modal variable
const modalImg = document.querySelector("[data-modal-img]");
const modalTitle = document.querySelector("[data-modal-title]");
const modalText = document.querySelector("[data-modal-text]");

// modal toggle function
const testimonialsModalFunc = function () {
  modalContainer.classList.toggle("active");
  overlay.classList.toggle("active");
};

// add click event to all modal items
for (let i = 0; i < testimonialsItem.length; i++) {
  testimonialsItem[i].addEventListener("click", function () {
    modalImg.src = this.querySelector("[data-testimonials-avatar]").src;
    modalImg.alt = this.querySelector("[data-testimonials-avatar]").alt;
    modalTitle.innerHTML = this.querySelector(
      "[data-testimonials-title]"
    ).innerHTML;
    modalText.innerHTML = this.querySelector(
      "[data-testimonials-text]"
    ).innerHTML;

    testimonialsModalFunc();
  });
}

// add click event to modal close button
modalCloseBtn.addEventListener("click", testimonialsModalFunc);
overlay.addEventListener("click", testimonialsModalFunc);

// custom select variables
const select = document.querySelector("[data-select]");
const selectItems = document.querySelectorAll("[data-select-item]");
const selectValue = document.querySelector("[data-selecct-value]");
const filterBtn = document.querySelectorAll("[data-filter-btn]");

select.addEventListener("click", function () {
  elementToggleFunc(this);
});

// add event in all select items
for (let i = 0; i < selectItems.length; i++) {
  selectItems[i].addEventListener("click", function () {
    let selectedValue = this.innerText.toLowerCase();
    selectValue.innerText = this.innerText;
    elementToggleFunc(select);
    filterFunc(selectedValue);
  });
}

// filter variables
const filterItems = document.querySelectorAll("[data-filter-item]");

const filterFunc = function (selectedValue) {
  for (let i = 0; i < filterItems.length; i++) {
    if (selectedValue === "all") {
      filterItems[i].classList.add("active");
    } else if (selectedValue === filterItems[i].dataset.category) {
      filterItems[i].classList.add("active");
    } else {
      filterItems[i].classList.remove("active");
    }
  }
};

// add event in all filter button items for large screen
let lastClickedBtn = filterBtn[0];

for (let i = 0; i < filterBtn.length; i++) {
  filterBtn[i].addEventListener("click", function () {
    let selectedValue = this.innerText.toLowerCase();
    selectValue.innerText = this.innerText;
    filterFunc(selectedValue);

    lastClickedBtn.classList.remove("active");
    this.classList.add("active");
    lastClickedBtn = this;
  });
}

// contact form variables
const form = document.querySelector("[data-form]");
const formInputs = document.querySelectorAll("[data-form-input]");
const formBtn = document.querySelector("[data-form-btn]");

// add event to all form input field
for (let i = 0; i < formInputs.length; i++) {
  formInputs[i].addEventListener("input", function () {
    if (form.checkValidity()) {
      formBtn.removeAttribute("disabled");
    } else {
      formBtn.setAttribute("disabled", "");
    }
  });
}

// AJAX form submission to Formspree
form.addEventListener("submit", async function (e) {
  e.preventDefault();

  const statusEl = document.getElementById("form-status");
  const emailField = document.getElementById("email-field");

  formBtn.setAttribute("disabled", "");
  formBtn.querySelector("span").textContent = "Sending...";
  statusEl.textContent = "";
  statusEl.className = "form-status";

  try {
    const response = await fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: { Accept: "application/json" },
    });

    if (response.ok) {
      statusEl.textContent = "Message sent! I'll get back to you soon.";
      statusEl.classList.add("form-status--success");
      form.reset();
      formBtn.setAttribute("disabled", "");
    } else {
      const data = await response.json();
      const msg = data.errors ? data.errors.map(e => e.message).join(", ") : "Something went wrong. Please try again.";
      statusEl.textContent = msg;
      statusEl.classList.add("form-status--error");
      formBtn.removeAttribute("disabled");
    }
  } catch {
    statusEl.textContent = "Network error. Please check your connection and try again.";
    statusEl.classList.add("form-status--error");
    formBtn.removeAttribute("disabled");
  }

  formBtn.querySelector("span").textContent = "Send Message";
});

// page navigation variables
const navigationLinks = document.querySelectorAll("[data-nav-link]");
const pages = document.querySelectorAll("[data-page]");

// add event to all nav link
for (let i = 0; i < navigationLinks.length; i++) {
  navigationLinks[i].addEventListener("click", function () {
    for (let i = 0; i < pages.length; i++) {
      if (this.innerHTML.toLowerCase() === pages[i].dataset.page) {
        pages[i].classList.add("active");
        navigationLinks[i].classList.add("active");
        window.scrollTo(0, 0);
      } else {
        pages[i].classList.remove("active");
        navigationLinks[i].classList.remove("active");
      }
    }
  });
}

function navigateToContact() {
    // Find the "Contact" navigation link
    const contactNav = Array.from(navigationLinks).find(link => 
        link.innerHTML.toLowerCase() === 'contact'
    );
    
    // Simulate click on the contact navigation
    if (contactNav) {
        contactNav.click();
        
        // Wait for page transition to complete then scroll to form
        setTimeout(() => {
            const contactForm = document.querySelector('.contact-form');
            if (contactForm) {
                contactForm.scrollIntoView({ behavior: 'smooth' });
            }
        }, 300); // 300ms delay to account for page transition
    }
}

// Chatbot functionality
const API_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : '';

document.addEventListener('DOMContentLoaded', () => {
  const chatbotIcon = document.getElementById('chatbot-icon');
  const chatbotContainer = document.getElementById('chatbot-container');
  const chatbotClose = document.getElementById('chatbot-close');
  const chatbotInput = document.getElementById('chatbot-input');
  const chatbotSend = document.getElementById('chatbot-send');
  const chatbotMessages = document.getElementById('chatbot-messages');

  // Generate or retrieve session ID
  function getSessionId() {
    let sessionId = localStorage.getItem('chatSessionId');
    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('chatSessionId', sessionId);
    }
    return sessionId;
  }

  // Store messages in localStorage
  function storeLocalMessages(messages) {
    localStorage.setItem(`chatMessages_${getSessionId()}`, JSON.stringify(messages));
  }

  // Get messages from localStorage
  function getLocalMessages() {
    const messages = localStorage.getItem(`chatMessages_${getSessionId()}`);
    return messages ? JSON.parse(messages) : [];
  }

  // Load chat history from backend and merge with local storage
  async function loadChatHistory() {
    const sessionId = getSessionId();

    // First, display messages from localStorage immediately
    const localMessages = getLocalMessages();
    displayMessages(localMessages);

    try {
      const response = await fetch(`${API_URL}/api/chat/history/${sessionId}`);
      if (!response.ok) throw new Error('Failed to load chat history');
      
      const data = await response.json();
      
      // Update localStorage with backend data
      storeLocalMessages(data.history);
      
      // Display messages from backend
      displayMessages(data.history);
      
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  }

  // Display messages in the chat
  function displayMessages(messages) {
    chatbotMessages.innerHTML = ''; // Clear existing messages
    messages.forEach(msg => {
      addMessage(msg.content, msg.role, msg.timestamp);
    });
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }

  // Add message to chat
  function addMessage(content, sender, timestamp = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const messageTime = timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const renderedContent = content.replace(
      /\[contact form\]/gi,
      '<a href="javascript:void(0)" onclick="navigateToContact()" style="text-decoration:underline;cursor:pointer;">contact form</a>'
    );

    messageDiv.innerHTML = `
      <div class="message-content">${renderedContent}</div>
      <div class="message-timestamp">${messageTime}</div>
    `;
    
    chatbotMessages.appendChild(messageDiv);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;

    // Update local storage
    const messages = getLocalMessages();
    messages.push({
      role: sender,
      content: content,
      timestamp: timestamp || new Date().toISOString()
    });
    storeLocalMessages(messages);
  }

  async function sendMessage() {
    const message = chatbotInput.value.trim();
    if (!message) return;

    // Add user message
    addMessage(message, 'user');
    chatbotInput.value = '';
    chatbotInput.style.height = 'auto';

    // Show typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'message bot-message typing';
    typingIndicator.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    chatbotMessages.appendChild(typingIndicator);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          session_id: getSessionId()
        })
      });

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const data = await response.json();
      
      // Remove typing indicator
      typingIndicator.remove();

      // Add bot response to chat
      addMessage(data.response, 'bot');

    } catch (error) {
      console.error('Error:', error);
      
      // Remove typing indicator
      typingIndicator.remove();

      // Show error message
      addMessage("I'm sorry, I couldn't process your request at the moment. Please try again later.", 'bot');
    }
  }

  // Load chat history when page loads
  loadChatHistory();

  // Toggle chatbot
  chatbotIcon.addEventListener('click', () => {
    chatbotContainer.classList.toggle('active');
    
    // Reload chat history when opening chatbot
    if (chatbotContainer.classList.contains('active')) {
      loadChatHistory();
    }
  });

  chatbotClose.addEventListener('click', () => {
    chatbotContainer.classList.remove('active');
  });

  // Auto-resize input
  chatbotInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
  });

  // Send on enter (shift+enter for new line)
  chatbotInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  chatbotSend.addEventListener('click', sendMessage);
});

// Add typing indicator CSS
const typingIndicatorCSS = `
.typing-dots {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: var(--light-gray);
  border-radius: 50%;
  animation: typing 1s infinite ease-in-out;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.5); }
}
`;

// Add the CSS to the document
const style = document.createElement('style');
style.textContent = typingIndicatorCSS;
document.head.appendChild(style);