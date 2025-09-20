document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    // A single source of truth for the entire application's data.
    const state = {
        profile: { patientName: null, guardianName: null, guardianPhone: null, avatar: null },
        schedule: [ { id: 1, name: 'Metformin', time: '08:00', compartment: 1 }, { id: 2, name: 'Lisinopril', time: '14:30', compartment: 2 }, { id: 3, name: 'Aspirin', time: '20:00', compartment: 3 } ],
        pillStatus: [ { id: 1, pills: 7, total: 7 }, { id: 2, pills: 7, total: 7 }, { id: 3, pills: 6, total: 7 }, { id: 4, pills: 5, total: 7 }, { id: 5, pills: 4, total: 7 }, { id: 6, pills: 2, total: 7 }, { id: 7, pills: 0, total: 7 } ],
        adherence: [95, 100, 100, 85, 100, 100, 90],
        logs: { dispense: [ { time: '08:01 AM', msg: "Dispensed 'Metformin'", status: 'success' }, { time: 'Yesterday', msg: "Alert: 'Aspirin' not taken", status: 'warning' } ], images: [ { time: '08:01 AM', url: 'https://placehold.co/400x300/e2e8f0/64748b?text=Pill' } ] },
        chatHistory: []
    };

    // --- UI ELEMENT SELECTORS ---
    // Caching all major DOM elements for performance and easy access.
    const app = {
        sidebar: document.getElementById('sidebar'),
        mainContent: document.getElementById('main-content'),
        navLinks: document.querySelectorAll('.nav-link'),
        sidebarAvatar: document.getElementById('sidebarAvatar'),
        sidebarPatientName: document.getElementById('sidebarPatientName'),
        // Modals
        modalBackdrop: document.getElementById('modalBackdrop'),
        scheduleModal: document.getElementById('scheduleModal'),
        aiResultModal: document.getElementById('aiResultModal'),
        loadingModal: document.getElementById('loadingModal'),
    };

    // --- INITIALIZATION ---
    function init() {
        lucide.createIcons();
        const savedProfile = localStorage.getItem('amar_profile');
        if (savedProfile) {
            state.profile = JSON.parse(savedProfile);
            showApp();
        } else {
            app.sidebar.style.display = 'none';
            showPage('setup');
        }
        attachEventListeners();
    }
    
    // --- EVENT LISTENERS (Centralized)---
    function attachEventListeners() {
        window.addEventListener('hashchange', navigate);
        document.body.addEventListener('submit', handleFormSubmits);
        document.body.addEventListener('click', handleClicks);
        document.body.addEventListener('change', handleChanges);
    }

    // --- EVENT HANDLER ROUTERS ---
    function handleFormSubmits(e) {
        e.preventDefault();
        const form = e.target;
        const actions = {
            'setupForm': () => handleSetupSubmit(form),
            'scheduleForm': () => handleScheduleFormSubmit(form),
            'profileForm': () => handleProfileUpdate(form),
            'chatForm': () => handleChatSubmit(form),
        };
        actions[form.id]?.();
    }

    function handleClicks(e) {
        const target = e.target.closest('button');
        if (!target) return;

        const actions = {
            'emergencyButton': () => window.location.hash = 'emergency',
            'deactivateEmergencyBtn': () => window.location.hash = 'dashboard',
            'addNewScheduleBtn': () => openScheduleModal(),
            'cancelScheduleBtn': closeScheduleModal,
            'generateSummaryBtn': handleGenerateSummary,
            'analyzeLogBtn': handleAnalyzeLog,
            'closeAiResultBtn': closeAiResultModal,
        };
        
        if (actions[target.id]) {
            actions[target.id]();
        } else if (target.matches('.edit-schedule-btn')) {
            openScheduleModal(target.dataset.id);
        } else if (target.matches('.delete-schedule-btn')) {
            handleDeleteSchedule(target.dataset.id);
        } else if (target.matches('.tab-link')) {
            handleTabClick(target);
        }
    }
    
    function handleChanges(e) {
        if (e.target.id === 'avatarUpload') handleAvatarUpload(e.target);
    }

    // --- NAVIGATION & PAGE RENDERING ---
    function navigate() {
        if (!state.profile.patientName) return; // Guard against navigation before setup
        const hash = window.location.hash.substring(1) || 'dashboard';
        showPage(hash);
    }
    
    function showPage(pageId) {
        app.mainContent.innerHTML = '';
        // STABILITY FIX: Always fetch the template from the DOM dynamically.
        const template = document.getElementById(`${pageId}-template`);
        
        if (template) {
            app.mainContent.appendChild(template.content.cloneNode(true));
        } else {
            app.mainContent.innerHTML = `<div class="card p-8"><h2>Error: Page not found for ID: ${pageId}</h2><p>Please check the template IDs in your HTML.</p></div>`;
            console.error(`Template not found for ID: ${pageId}-template`);
            return;
        }

        app.navLinks.forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === `#${pageId}`);
        });

        // STABILITY FIX: A map ensures render functions are only called for existing pages.
        const renderMap = {
            dashboard: renderDashboard,
            schedule: renderSchedule,
            monitoring: renderMonitoring,
            profile: renderProfile,
            assistant: renderAssistant,
            emergency: renderEmergency,
        };
        
        renderMap[pageId]?.(); // Call the render function only if it exists.
        
        lucide.createIcons();
    }
    
    function showApp() {
        app.sidebar.style.display = 'flex';
        updateProfileInfo();
        navigate();
    }

    // --- PAGE-SPECIFIC RENDER FUNCTIONS ---
    function updateProfileInfo() {
        if (!state.profile.patientName) return;
        const { patientName, avatar } = state.profile;
        const initials = patientName.split(' ').map(n => n[0]).join('').toUpperCase();
        const placeholder = (size) => `https://placehold.co/${size}x${size}/e0e7ff/3730a3?text=${initials}`;
        
        app.sidebarAvatar.src = avatar || placeholder(48);
        app.sidebarPatientName.textContent = patientName;
        
        // Update elements only if they exist on the current page.
        const patientNameDisplay = document.getElementById('patientNameDisplay');
        if (patientNameDisplay) patientNameDisplay.textContent = patientName;

        const profilePicture = document.getElementById('profilePicture');
        if (profilePicture) profilePicture.src = avatar || placeholder(160);
    }

    function renderDashboard() {
        updateProfileInfo();
        const hour = new Date().getHours();
        const timeOfDay = hour < 12 ? "Morning" : hour < 18 ? "Afternoon" : "Evening";
        document.getElementById('greeting').querySelector('h2').innerHTML = `Good ${timeOfDay}, <span id="patientNameDisplay">${state.profile.patientName}</span>`;
        renderAdherenceChart();
        renderPillStatus();
    }

    function renderSchedule() {
        const listEl = document.getElementById('scheduleList');
        listEl.innerHTML = state.schedule.length === 0 ? `<p class="text-center text-gray-500 py-8">No schedules added yet.</p>` : '';
        state.schedule.sort((a,b) => a.time.localeCompare(b.time)).forEach(item => {
            listEl.insertAdjacentHTML('beforeend', `
                <div class="schedule-item">
                    <div class="schedule-item-info">
                        <i data-lucide="pill"></i>
                        <div><p>${item.name}</p><p>Compartment ${item.compartment}</p></div>
                    </div>
                    <div class="schedule-item-details">
                        <p>${formatTime(item.time)}</p>
                        <div class="schedule-item-actions">
                            <button class="edit-schedule-btn" data-id="${item.id}"><i data-lucide="edit-3"></i></button>
                            <button class="delete-schedule-btn" data-id="${item.id}"><i data-lucide="trash-2"></i></button>
                        </div>
                    </div>
                </div>`);
        });
    }
    
    function renderMonitoring() {
        const logList = document.getElementById('dispenseLogList');
        logList.innerHTML = '';
        state.logs.dispense.forEach(log => {
            const icon = log.status === 'success' ? 'check-circle' : log.status === 'warning' ? 'alert-triangle' : 'x-circle';
            logList.insertAdjacentHTML('beforeend', `<li class="log-item"><i data-lucide="${icon}" class="${log.status}"></i><div><p>${log.msg}</p><p>${log.time}</p></div></li>`);
        });

        const imageGrid = document.getElementById('imageLogGrid');
        imageGrid.innerHTML = '';
        state.logs.images.forEach(img => {
            imageGrid.insertAdjacentHTML('beforeend', `<div class="image-item"><img src="${img.url}" alt="Dispense Image"><div class="image-item-overlay">${img.time}</div></div>`);
        });
    }

    function renderProfile() {
        updateProfileInfo();
        document.getElementById('profilePatientName').value = state.profile.patientName;
        document.getElementById('profileGuardianName').value = state.profile.guardianName;
        document.getElementById('profileGuardianPhone').value = state.profile.guardianPhone;
    }
    
    function renderAssistant() {
        const chatWindow = document.getElementById('chatWindow');
        chatWindow.innerHTML = `<div class="chat-message ai"><i data-lucide="robot"></i><div class="chat-bubble"><p>Hello! I'm AMAR. Ask me about medications or general health questions. Please remember, I am not a doctor.</p></div></div>`;
        state.chatHistory.forEach(msg => addChatMessageToDOM(msg.message, msg.role));
    }

    function renderEmergency() {
        document.getElementById('emergencyTimestamp').textContent = `Activated at: ${new Date().toLocaleTimeString()}`;
    }

    function renderAdherenceChart() { const ctx = document.getElementById('adherenceChart')?.getContext('2d'); if(!ctx) return; new Chart(ctx, { type: 'bar', data: { labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], datasets: [{ label: 'Adherence', data: state.adherence, backgroundColor: 'rgba(13, 110, 253, 0.7)', borderColor: 'rgba(13, 110, 253, 1)', borderWidth: 1, borderRadius: 8, barThickness: 20, }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100, ticks: { callback: value => `${value}%` } }, x: { grid: { display: false } } } } }); }
    function renderPillStatus() { const c=document.getElementById('pillCompartments'); if(!c) return; c.innerHTML=''; let i=false; state.pillStatus.forEach(p=>{const t=(p.pills/p.total)*100;let o='fg-green';if(t<=30&&t>0){o='fg-orange';i=true;}else if(t===0){o='fg-red';} c.insertAdjacentHTML('beforeend',`<div class="pill-status-item"><div class="progress-circle"><svg viewBox="0 0 36 36"><path class="bg" stroke-width="4" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" /><path class="${o}" stroke-width="4" stroke-dasharray="${t}, 100" stroke-linecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" /></svg><div class="text">${p.pills}</div></div><p>Day ${p.id}</p></div>`);}); const w=document.getElementById('refillWarning');if(i){document.getElementById('refillMessage').textContent='Some compartments are running low.';w.classList.remove('hidden');}else{w.classList.add('hidden');} }

    // --- FORM & ACTION HANDLERS ---
    function handleSetupSubmit(form) { state.profile.patientName = form.patientNameInput.value; state.profile.guardianName = form.guardianNameInput.value; state.profile.guardianPhone = form.guardianPhoneInput.value; localStorage.setItem('amar_profile', JSON.stringify(state.profile)); showApp(); }
    function handleProfileUpdate(form) { state.profile.guardianName = form.profileGuardianName.value; state.profile.guardianPhone = form.profileGuardianPhone.value; localStorage.setItem('amar_profile', JSON.stringify(state.profile)); alert('Profile updated!'); updateProfileInfo(); }
    function handleAvatarUpload(input) { const f=input.files[0]; if(!f) return; const r=new FileReader(); r.onload=(e)=>{state.profile.avatar=e.target.result; localStorage.setItem('amar_profile',JSON.stringify(state.profile)); updateProfileInfo();}; r.readAsDataURL(f); }
    function handleTabClick(tab) { const tabContainer = tab.parentElement; const contentContainer = tabContainer.nextElementSibling; tabContainer.querySelectorAll('.tab-link').forEach(t=>t.classList.remove('active')); tab.classList.add('active'); contentContainer.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active')); contentContainer.querySelector(`#${tab.dataset.tab}`).classList.add('active'); }
    function handleDeleteSchedule(id) { if(confirm('Delete this schedule?')) { state.schedule = state.schedule.filter(s => s.id != id); renderSchedule(); lucide.createIcons(); } }
    
    // --- MODAL & AI LOGIC ---
    function openScheduleModal(id = null) {
        const form = document.getElementById('scheduleForm');
        form.reset();
        form.dataset.id = '';
        const title = document.getElementById('scheduleModalTitle');
        if(id) {
            const item = state.schedule.find(s => s.id == id);
            if (!item) return;
            title.textContent = 'Edit Schedule';
            form.dataset.id = id;
            form.medName.value = item.name;
            form.medTime.value = item.time;
            form.medCompartment.value = item.compartment;
        } else {
            title.textContent = 'Add New Schedule';
        }
        app.modalBackdrop.style.display = 'block';
        app.scheduleModal.style.display = 'block';
    }
    function closeScheduleModal() { app.modalBackdrop.style.display = 'none'; app.scheduleModal.style.display = 'none'; }
    function handleScheduleFormSubmit(form) { const id = form.dataset.id; const scheduleData = { id: id || Date.now(), name: form.medName.value, time: form.medTime.value, compartment: form.medCompartment.value }; const index = state.schedule.findIndex(s => s.id == id); if (index > -1) state.schedule[index] = scheduleData; else state.schedule.push(scheduleData); renderSchedule(); lucide.createIcons(); closeScheduleModal(); }

    async function callGeminiAPI(prompt) {
        app.loadingModal.style.display = 'flex';
        try {
            console.log("Calling Gemini with prompt:", prompt);
            await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate network delay
            return `This is a simulated response from the AI based on your query about: "${prompt.substring(0, 50)}...". For real medical advice, always consult a qualified healthcare professional.`;
        } catch (error) {
            console.error("API Error:", error);
            return "Sorry, there was an error contacting the AI.";
        } finally {
            // This 'finally' block ensures the loading modal is always hidden.
            app.loadingModal.style.display = 'none';
        }
    }
    async function handleGenerateSummary() { const summary = await callGeminiAPI(`Summarize this schedule: ${JSON.stringify(state.schedule)}`); showAiResultModal('AI Schedule Summary', `<p>${summary}</p>`); }
    async function handleAnalyzeLog() { const analysis = await callGeminiAPI(`Analyze this log: ${JSON.stringify(state.logs.dispense)}`); showAiResultModal('AI Log Analysis', `<p>${analysis}</p>`); }
    function showAiResultModal(title, content) { document.getElementById('aiResultTitle').innerHTML = `<i data-lucide="sparkles"></i>${title}`; document.getElementById('aiResultContent').innerHTML = content; app.modalBackdrop.style.display = 'block'; app.aiResultModal.style.display = 'block'; lucide.createIcons(); }
    function closeAiResultModal() { app.modalBackdrop.style.display = 'none'; app.aiResultModal.style.display = 'none'; }

    async function handleChatSubmit(form) {
        const input = form.querySelector('input');
        const userMessage = input.value.trim();
        if (!userMessage) return;
        
        state.chatHistory.push({ role: 'user', message: userMessage });
        addChatMessageToDOM(userMessage, 'user');
        input.value = '';
        input.disabled = true;

        const typingIndicator = addChatMessageToDOM('...', 'ai', true);
        const aiResponse = await callGeminiAPI(userMessage);
        typingIndicator.remove();
        
        state.chatHistory.push({ role: 'ai', message: aiResponse });
        addChatMessageToDOM(aiResponse, 'ai');
        input.disabled = false;
        input.focus();
    }

    function addChatMessageToDOM(message, role, isTyping = false) {
        const chatWindow = document.getElementById('chatWindow');
        const initials = state.profile.patientName.split(' ').map(n=>n[0]).join('').toUpperCase();
        const avatar = role === 'user' 
            ? `<img src="${state.profile.avatar || `https://placehold.co/40x40/e0e7ff/3730a3?text=${initials}`}" alt="User">` 
            : `<i data-lucide="robot"></i>`;
        
        const messageEl = document.createElement('div');
        messageEl.className = `chat-message ${role}`;
        messageEl.innerHTML = `${avatar}<div class="chat-bubble"><p>${message}</p></div>`;
        
        if (role === 'user') {
            const temp = messageEl.querySelector('img');
            messageEl.appendChild(temp);
        }

        chatWindow.appendChild(messageEl);
        lucide.createIcons();
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return messageEl;
    }
    
    // --- UTILITY ---
    const formatTime = (t) => { const [h,m]=t.split(':');const n=parseInt(h);const a=n>=12?'PM':'AM';const f=n%12||12;return`${String(f).padStart(2,'0')}:${m} ${a}`; };
    
    // --- START APP ---
    init();
});

