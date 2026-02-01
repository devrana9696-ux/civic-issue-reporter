// API Base URL
const API_BASE = '/api';

// Global state
let currentUser = null;
let allIssues = [];
let currentIssue = null;
let categoryChart = null;
let severityChart = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    console.log('🚀 Initializing Civic Reporter App...');
    setupNavigation();
    setupModals();
    setupForms();
    loadRecentIssues();
    
    // Auto-suggestions on title input
    const titleInput = document.getElementById('issueTitle');
    if (titleInput) {
        titleInput.addEventListener('input', debounce(handleTitleInput, 300));
    }
    
    // AI Prediction on description input - trigger on both title and description
    const descInput = document.getElementById('issueDescription');
    if (descInput) {
        descInput.addEventListener('input', debounce(getAIPrediction, 500));
    }
    if (titleInput) {
        titleInput.addEventListener('input', debounce(getAIPrediction, 800));
    }
}

// ========== NAVIGATION ==========
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const pageId = link.dataset.page;
            
            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Show corresponding page
            pages.forEach(p => p.classList.remove('active'));
            const targetPage = document.getElementById(pageId + 'Page');
            if (targetPage) {
                targetPage.classList.add('active');
            }
            
            // Load data based on page
            if (pageId === 'admin') {
                loadAdminDashboard();
            } else if (pageId === 'track') {
                loadAllIssues();
            } else if (pageId === 'citizen') {
                loadRecentIssues();
            }
        });
    });
}

// ========== MODALS ==========
function setupModals() {
    const modals = document.querySelectorAll('.modal');
    const closeBtns = document.querySelectorAll('.close');
    
    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal').classList.remove('active');
        });
    });
    
    window.addEventListener('click', (e) => {
        modals.forEach(modal => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// ========== FORMS ==========
function setupForms() {
    // Report Form
    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        reportForm.addEventListener('submit', handleReportSubmit);
    }
    
    // Login Form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Admin Filters
    const filterStatus = document.getElementById('filterStatus');
    const filterSeverity = document.getElementById('filterSeverity');
    
    if (filterStatus) {
        filterStatus.addEventListener('change', loadAdminIssues);
    }
    if (filterSeverity) {
        filterSeverity.addEventListener('change', loadAdminIssues);
    }
}

// ========== AUTO-SUGGESTIONS ==========
async function handleTitleInput(e) {
    const text = e.target.value;
    const suggestionsContainer = document.getElementById('suggestions');
    
    if (text.length < 2) {
        if (suggestionsContainer) {
            suggestionsContainer.classList.remove('active');
        }
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/ai/suggestions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ partial_text: text })
        });
        
        if (response.ok) {
            const data = await response.json();
            showSuggestions(data.suggestions || []);
        }
    } catch (error) {
        console.error('Error fetching suggestions:', error);
    }
}

function showSuggestions(suggestions) {
    const container = document.getElementById('suggestions');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (suggestions.length === 0) {
        container.classList.remove('active');
        return;
    }
    
    suggestions.forEach(suggestion => {
        const div = document.createElement('div');
        div.className = 'suggestion-item';
        div.textContent = suggestion;
        div.addEventListener('click', () => {
            document.getElementById('issueTitle').value = suggestion;
            container.classList.remove('active');
            getAIPrediction();
        });
        container.appendChild(div);
    });
    
    container.classList.add('active');
}

// ========== AI PREDICTION ==========
async function getAIPrediction() {
    const title = document.getElementById('issueTitle').value;
    const description = document.getElementById('issueDescription').value;
    const predictionBox = document.getElementById('aiPrediction');
    
    if (!title || !description || title.length < 5 || description.length < 10) {
        if (predictionBox) {
            predictionBox.style.display = 'none';
        }
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/ai/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description })
        });
        
        if (response.ok) {
            const data = await response.json();
            displayPrediction(data);
        }
    } catch (error) {
        console.error('Error getting prediction:', error);
    }
}

function displayPrediction(data) {
    const elements = {
        category: document.getElementById('predictedCategory'),
        severity: document.getElementById('predictedSeverity'),
        dept: document.getElementById('predictedDept'),
        priority: document.getElementById('predictedPriority'),
        box: document.getElementById('aiPrediction')
    };
    
    if (elements.category) elements.category.textContent = data.category;
    if (elements.severity) {
        elements.severity.textContent = data.severity.toUpperCase();
        elements.severity.className = 'value badge badge-' + data.severity;
    }
    if (elements.dept) elements.dept.textContent = data.department;
    if (elements.priority) elements.priority.textContent = Math.round(data.priority_score) + '/100';
    if (elements.box) elements.box.style.display = 'block';
}

// ========== SUBMIT ISSUE REPORT (FIXED - USING JSON) ==========
async function handleReportSubmit(e) {
    e.preventDefault();
    
    // Collect form data as JSON object (NOT FormData)
    const issueData = {
        title: document.getElementById('issueTitle').value,
        description: document.getElementById('issueDescription').value,
        location: document.getElementById('issueLocation').value,
        reporter_name: document.getElementById('reporterName').value,
        reporter_contact: document.getElementById('reporterContact').value || null
    };
    
    console.log('📤 Submitting issue:', issueData);
    
    try {
        const response = await fetch(`${API_BASE}/issues`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'  // ✅ Send as JSON
            },
            body: JSON.stringify(issueData)
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Backend error:', errorText);
            throw new Error(`Failed to submit: ${response.status}`);
        }
        
        const issue = await response.json();
        console.log('✅ Issue created:', issue);
        
        showAlert('success', `🎉 Issue #${issue.id} reported successfully! Status: ${issue.status}`);
        
        // Reset form
        e.target.reset();
        
        // Hide AI prediction box
        const predictionBox = document.getElementById('aiPrediction');
        if (predictionBox) predictionBox.style.display = 'none';
        
        // Hide suggestions
        const suggestions = document.getElementById('suggestions');
        if (suggestions) suggestions.classList.remove('active');
        
        // Reload recent issues
        loadRecentIssues();
        
    } catch (error) {
        console.error('❌ Submit error:', error);
        showAlert('error', 'Failed to submit issue. Please try again.');
    }
}

// ========== LOGIN ==========
async function handleLogin(e) {
    e.preventDefault();
    
    const credentials = {
        username: document.getElementById('loginUsername').value,
        password: document.getElementById('loginPassword').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials)
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = { 
                username: credentials.username, 
                role: 'admin', 
                token: data.access_token 
            };
            hideModal('loginModal');
            loadAdminDashboard();
            showAlert('success', '✅ Login successful!');
        } else {
            showAlert('error', '❌ Invalid credentials. Try: admin / admin123');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('error', 'Login failed. Check your connection.');
    }
}

// ========== LOAD RECENT ISSUES ==========
async function loadRecentIssues() {
    try {
        const response = await fetch(`${API_BASE}/issues?limit=10`);
        if (response.ok) {
            const issues = await response.json();
            displayRecentIssues(issues);
        }
    } catch (error) {
        console.error('Error loading recent issues:', error);
    }
}

function displayRecentIssues(issues) {
    const container = document.getElementById('recentIssues');
    if (!container) return;
    
    if (issues.length === 0) {
        container.innerHTML = '<p class="text-muted">📭 No issues reported yet. Be the first!</p>';
        return;
    }
    
    container.innerHTML = issues.map(issue => `
        <div class="issue-item" onclick="showIssueDetail(${issue.id})">
            <h3>#${issue.id} - ${issue.title}</h3>
            <p>${issue.description.substring(0, 100)}${issue.description.length > 100 ? '...' : ''}</p>
            <div class="issue-meta">
                <span class="badge badge-${issue.status}">${formatStatus(issue.status)}</span>
                <span class="badge badge-${issue.severity}">${issue.severity.toUpperCase()}</span>
                <span><i class="fas fa-map-marker-alt"></i> ${issue.location}</span>
            </div>
        </div>
    `).join('');
}

// ========== ADMIN DASHBOARD ==========
async function loadAdminDashboard() {
    console.log('📊 Loading admin dashboard...');
    await loadAnalytics();
    await loadAdminIssues();
}

async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/analytics`);
        if (!response.ok) {
            throw new Error('Analytics fetch failed');
        }
        
        const data = await response.json();
        console.log('Analytics data:', data);
        
        // Update stats
        updateElement('statTotal', data.total_issues || 0);
        updateElement('statPending', data.pending || 0);
        updateElement('statProgress', data.in_progress || 0);
        updateElement('statResolved', data.resolved || 0);
        
        // Update charts
        updateCategoryChart(data.by_category || {});
        updateSeverityChart(data.by_severity || {});
        
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function updateElement(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function updateCategoryChart(data) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    if (labels.length === 0) {
        ctx.getContext('2d').clearRect(0, 0, ctx.width, ctx.height);
        return;
    }
    
    categoryChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
                    '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function updateSeverityChart(data) {
    const ctx = document.getElementById('severityChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (severityChart) {
        severityChart.destroy();
    }
    
    const severityOrder = ['low', 'medium', 'high', 'critical'];
    const labels = severityOrder.map(s => s.toUpperCase());
    const values = severityOrder.map(s => data[s] || 0);
    
    severityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Issues',
                data: values,
                backgroundColor: ['#10b981', '#f59e0b', '#f97316', '#ef4444']
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

async function loadAdminIssues() {
    const status = document.getElementById('filterStatus')?.value || '';
    const severity = document.getElementById('filterSeverity')?.value || '';
    
    let url = `${API_BASE}/issues?limit=50`;
    if (status) url += `&status=${status}`;
    if (severity) url += `&severity=${severity}`;
    
    try {
        const response = await fetch(url);
        if (response.ok) {
            const issues = await response.json();
            displayAdminIssues(issues);
        }
    } catch (error) {
        console.error('Error loading admin issues:', error);
    }
}

function displayAdminIssues(issues) {
    const container = document.getElementById('adminIssuesTable');
    if (!container) return;
    
    if (issues.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">📭 No issues found matching filters</p>';
        return;
    }
    
    const table = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Severity</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${issues.map(issue => `
                    <tr>
                        <td>#${issue.id}</td>
                        <td>${issue.title.substring(0, 50)}${issue.title.length > 50 ? '...' : ''}</td>
                        <td>${issue.category}</td>
                        <td><span class="badge badge-${issue.severity}">${issue.severity}</span></td>
                        <td><span class="badge badge-${issue.status}">${formatStatus(issue.status)}</span></td>
                        <td>${Math.round(issue.priority_score || 0)}/100</td>
                        <td>
                            <button onclick="showIssueDetail(${issue.id})" class="btn btn-sm btn-primary">
                                <i class="fas fa-eye"></i> View
                            </button>
                            <button onclick="updateIssueStatus(${issue.id})" class="btn btn-sm btn-success">
                                <i class="fas fa-edit"></i> Update
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

// ========== TRACK ISSUES ==========
async function loadAllIssues() {
    try {
        const response = await fetch(`${API_BASE}/issues?limit=100`);
        if (response.ok) {
            allIssues = await response.json();
            displayAllIssues(allIssues);
        }
    } catch (error) {
        console.error('Error loading all issues:', error);
    }
}

function displayAllIssues(issues) {
    const container = document.getElementById('allIssues');
    if (!container) return;
    
    if (issues.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">📭 No issues found</p>';
        return;
    }
    
    container.innerHTML = issues.map(issue => `
        <div class="issue-card" onclick="showIssueDetail(${issue.id})">
            <h3>#${issue.id} - ${issue.title}</h3>
            <p>${issue.description.substring(0, 120)}${issue.description.length > 120 ? '...' : ''}</p>
            <div class="issue-meta">
                <span class="badge badge-${issue.status}">${formatStatus(issue.status)}</span>
                <span class="badge badge-${issue.severity}">${issue.severity}</span>
            </div>
            <p class="mt-2"><i class="fas fa-map-marker-alt"></i> ${issue.location}</p>
            <p><i class="fas fa-building"></i> ${issue.department || 'Not assigned'}</p>
        </div>
    `).join('');
}

async function searchIssues() {
    const issueId = document.getElementById('searchIssueId')?.value;
    const category = document.getElementById('searchCategory')?.value;
    
    let filteredIssues = [...allIssues];
    
    if (issueId) {
        filteredIssues = filteredIssues.filter(i => i.id === parseInt(issueId));
    }
    
    if (category) {
        filteredIssues = filteredIssues.filter(i => i.category === category);
    }
    
    displayAllIssues(filteredIssues);
    
    if (filteredIssues.length > 0) {
        showIssueDetail(filteredIssues[0].id);
    }
}

// ========== ISSUE DETAILS ==========
async function showIssueDetail(issueId) {
    try {
        const [issueResponse, historyResponse] = await Promise.all([
            fetch(`${API_BASE}/issues/${issueId}`),
            fetch(`${API_BASE}/issues/${issueId}/history`)
        ]);
        
        if (!issueResponse.ok) {
            throw new Error('Failed to fetch issue');
        }
        
        const issue = await issueResponse.json();
        const history = historyResponse.ok ? await historyResponse.json() : [];
        
        currentIssue = issue;
        displayIssueDetail(issue, history);
    } catch (error) {
        console.error('Error loading issue detail:', error);
        showAlert('error', 'Failed to load issue details');
    }
}

function displayIssueDetail(issue, history) {
    const html = generateIssueDetailHTML(issue, history);
    
    // Display in tracking page detail panel
    const detailContainer = document.getElementById('issueDetails');
    if (detailContainer) {
        detailContainer.innerHTML = html;
    }
    
    // Also show in modal
    const modalContent = document.getElementById('modalContent');
    if (modalContent) {
        modalContent.innerHTML = html;
        showModal('issueModal');
    }
}

function generateIssueDetailHTML(issue, history) {
    return `
        <div class="issue-details">
            <h2>#${issue.id} - ${issue.title}</h2>
            
            <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span class="badge badge-${issue.status}">${formatStatus(issue.status)}</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Severity:</span>
                <span class="badge badge-${issue.severity}">${issue.severity.toUpperCase()}</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Category:</span>
                <span class="detail-value">${issue.category}</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Department:</span>
                <span class="detail-value">${issue.department || 'Not assigned'}</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Location:</span>
                <span class="detail-value">${issue.location}</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Priority Score:</span>
                <span class="detail-value">${Math.round(issue.priority_score || 0)}/100</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Reporter:</span>
                <span class="detail-value">${issue.reporter_name}</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Contact:</span>
                <span class="detail-value">${issue.reporter_contact || 'N/A'}</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Reported On:</span>
                <span class="detail-value">${formatDate(issue.created_at)}</span>
            </div>
            
            ${issue.assigned_to ? `
                <div class="detail-row">
                    <span class="detail-label">Assigned To:</span>
                    <span class="detail-value">${issue.assigned_to}</span>
                </div>
            ` : ''}
            
            ${issue.resolved_at ? `
                <div class="detail-row">
                    <span class="detail-label">Resolved On:</span>
                    <span class="detail-value">${formatDate(issue.resolved_at)}</span>
                </div>
            ` : ''}
            
            <h3 class="mt-2">Description</h3>
            <p>${issue.description}</p>
            
            ${issue.admin_notes ? `
                <h3 class="mt-2">Admin Notes</h3>
                <p>${issue.admin_notes}</p>
            ` : ''}
            
            <h3 class="mt-2">📅 Status History</h3>
            <div class="timeline">
                ${history.length > 0 ? history.map(h => `
                    <div class="timeline-item">
                        <div class="timeline-dot"></div>
                        <div class="timeline-content">
                            <div class="timeline-time">${formatDate(h.timestamp)}</div>
                            <div><strong>${formatStatus(h.new_status)}</strong></div>
                            ${h.notes ? `<div>${h.notes}</div>` : ''}
                            <div class="text-muted">Updated by: ${h.updated_by}</div>
                        </div>
                    </div>
                `).join('') : '<p class="text-muted">No history available</p>'}
            </div>
        </div>
    `;
}

// ========== UPDATE ISSUE STATUS ==========
async function updateIssueStatus(issueId) {
    const newStatus = prompt('Enter new status:\n- pending\n- in_progress\n- resolved\n- rejected');
    
    if (!newStatus || !['pending', 'in_progress', 'resolved', 'rejected'].includes(newStatus)) {
        if (newStatus) {
            showAlert('error', 'Invalid status. Use: pending, in_progress, resolved, or rejected');
        }
        return;
    }
    
    const notes = prompt('Enter admin notes (optional):');
    
    try {
        const response = await fetch(`${API_BASE}/issues/${issueId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                status: newStatus,
                admin_notes: notes || null
            })
        });
        
        if (response.ok) {
            showAlert('success', '✅ Issue updated successfully');
            loadAdminIssues();
            loadAnalytics();
        } else {
            showAlert('error', '❌ Failed to update issue');
        }
    } catch (error) {
        console.error('Error updating issue:', error);
        showAlert('error', 'Update failed');
    }
}

// ========== UTILITY FUNCTIONS ==========
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatStatus(status) {
    return status.replace('_', ' ').toUpperCase();
}

function showAlert(type, message) {
    // Remove existing alerts
    document.querySelectorAll('.alert').forEach(alert => alert.remove());
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <strong>${type === 'success' ? '✅' : '❌'}</strong> ${message}
    `;
    
    const container = document.querySelector('.main-content .container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.style.opacity = '0';
            alertDiv.style.transition = 'opacity 0.3s';
            setTimeout(() => alertDiv.remove(), 300);
        }, 5000);
    }
}

// Make functions available globally
window.showIssueDetail = showIssueDetail;
window.updateIssueStatus = updateIssueStatus;
window.searchIssues = searchIssues;

console.log('✅ Civic Reporter App Loaded Successfully!');