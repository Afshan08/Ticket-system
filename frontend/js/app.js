/**
 * Main Application Logic
 * Handles Sidebar, Navigation, and Lookup Modals
 */

document.addEventListener('DOMContentLoaded', () => {
    injectSidebar();
    initializeLookupSystem();
});

/* --- Sidebar Logic --- */
function injectSidebar() {
    // Path Detection
    // Normalize path to use forward slashes for Windows compatibility and case-insensitive
    const path = window.location.pathname.replace(/\\/g, '/').toLowerCase();
    const isFormsDir = path.includes('/forms/') || path.includes('/forms');
    const isReportsDir = path.includes('/reports/') || path.includes('/reports');

    let dashboardLink = 'index.html';
    let formPrefix = 'forms/';
    let reportPrefix = 'reports/';

    if (isFormsDir || isReportsDir) {
        dashboardLink = '../index.html';
        formPrefix = isFormsDir ? '' : '../forms/';
        reportPrefix = isReportsDir ? '' : '../reports/';
    }

    const sidebarHTML = `
        <!-- Mobile Backdrop -->
        <div id="sidebar-backdrop" class="fixed inset-0 bg-gray-900 bg-opacity-50 z-40 hidden md:hidden transition-opacity"></div>

        <div id="sidebar" class="bg-white h-screen border-r border-gray-200 flex flex-col transition-transform duration-300 w-64 fixed left-0 top-0 z-50 transform -translate-x-full md:translate-x-0">
            <div class="p-4 flex items-center justify-between border-b border-gray-100">
                <h1 id="app-title" class="font-bold text-xl text-indigo-600 truncate">Printy</h1>
                <!-- Desktop Toggle (Hidden on Mobile) -->
                <button id="toggle-btn" class="p-2 rounded hover:bg-gray-100 text-gray-500 hidden md:block">
                     <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                </button>
                <!-- Mobile Close Button -->
                 <button id="mobile-close-btn" class="p-2 rounded hover:bg-gray-100 text-gray-500 md:hidden">
                     <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            
            <nav class="flex-1 overflow-y-auto py-4 custom-scrollbar">
                <div class="px-4 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider sidebar-label">Main</div>
                <a href="${dashboardLink}" class="flex items-center px-4 py-3 text-gray-600 hover:bg-indigo-50 hover:text-indigo-600 transition-colors">
                    <svg class="h-5 w-5 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
                    <span class="sidebar-text">Dashboard</span>
                </a>



                <div class="px-4 mt-6 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider sidebar-label">Master Data</div>
                ${createNavLink('Area', formPrefix + 'area.html', 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z')}
                ${createNavLink('Customer', formPrefix + 'customer.html', 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z')}
                ${createNavLink('Category', formPrefix + 'item_category.html', 'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z')}
                ${createNavLink('Item', formPrefix + 'item.html', 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4')}
                ${createNavLink('Machine', formPrefix + 'machine.html', 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z')}
                ${createNavLink('Operator', formPrefix + 'operator.html', 'M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z')}

                <div class="px-4 mt-6 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider sidebar-label">Transactions</div>
                ${createNavLink('Job Order', formPrefix + 'job.html', 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2')}
                ${createNavLink('Printing Transaction', formPrefix + 'transaction.html', 'M12 4v16m8-8H4')}
                ${createNavLink('Rewind Transaction', formPrefix + 'rewinding.html', 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15')}
                ${createNavLink('Lamination Transaction', formPrefix + 'laminating.html', 'M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2')}
                ${createNavLink('Slit Transaction', formPrefix + 'sliting.html', 'M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243 4.243 3 3 0 004.243-4.243zm0-5.758a3 3 0 10-4.243-4.243 3 3 0 004.243 4.243z')}

                <div class="px-4 mt-6 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider sidebar-label">Reports</div>
                ${createNavLink('Production Details', reportPrefix + 'production_dashboard.html', 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z')}
                ${createNavLink('Pending Orders', reportPrefix + 'pending_orders.html', 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z')}
                ${createNavLink('Job Progress', reportPrefix + 'job_progress.html', 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2')}
                ${createNavLink('Print Output', reportPrefix + 'print_output.html', 'M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z')}

            </nav>
        </div>
    `;

    document.body.insertAdjacentHTML('afterbegin', sidebarHTML);

    const mainContentArea = document.getElementById('main-content');
    if (!mainContentArea) {
        console.error("Main Content area not found! App.js expects #main-content.");
        return;
    }

    // Toggle Logic
    const toggleBtn = document.getElementById('toggle-btn');
    const mobileCloseBtn = document.getElementById('mobile-close-btn');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    const appTitle = document.getElementById('app-title');
    const labels = document.querySelectorAll('.sidebar-label');
    const texts = document.querySelectorAll('.sidebar-text');

    // Desktop Toggle
    toggleBtn.addEventListener('click', () => {
        if (sidebar.classList.contains('md:w-64')) {
            // It's expanded, so collapse it
            collapseSidebar();
            localStorage.setItem('sidebarCollapsed', 'true');
        } else if (sidebar.classList.contains('w-64') && !sidebar.classList.contains('w-20')) {
            // Fallback if md: class check fails or custom logic
            collapseSidebar();
            localStorage.setItem('sidebarCollapsed', 'true');
        } else {
            expandSidebar();
            localStorage.setItem('sidebarCollapsed', 'false');
        }
    });

    // Mobile Toggle
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.remove('-translate-x-full');
            backdrop.classList.remove('hidden');
        });
    }

    if (mobileCloseBtn) {
        mobileCloseBtn.addEventListener('click', closeMobileMenu);
    }

    if (backdrop) {
        backdrop.addEventListener('click', closeMobileMenu);
    }

    function closeMobileMenu() {
        sidebar.classList.add('-translate-x-full');
        backdrop.classList.add('hidden');
    }

    function collapseSidebar() {
        // We only modify desktop state (w-64 -> w-20)
        // We need to remove w-64 and add w-20
        // And reset main content margin
        sidebar.classList.remove('w-64');
        sidebar.classList.remove('md:w-64'); // Important to override tailwind md:
        sidebar.classList.add('w-20');

        mainContentArea.classList.remove('md:ml-64');
        mainContentArea.classList.add('md:ml-20');

        appTitle.classList.add('hidden');
        labels.forEach(l => l.classList.add('hidden'));
        texts.forEach(t => t.classList.add('hidden'));
    }

    function expandSidebar() {
        sidebar.classList.remove('w-20');
        sidebar.classList.add('w-64');
        sidebar.classList.add('md:w-64');

        mainContentArea.classList.remove('md:ml-20');
        mainContentArea.classList.add('md:ml-64');

        appTitle.classList.remove('hidden');
        labels.forEach(l => l.classList.remove('hidden'));
        texts.forEach(t => t.classList.remove('hidden'));
    }

    // Restore state (Desktop only)
    if (window.innerWidth >= 768) {
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed) collapseSidebar();
    }
}

function createNavLink(name, url, iconPath) {
    const isCurrent = window.location.href.includes(url) && url !== '';
    // Simplified check; exact matching is hard with relative paths
    const activeClass = isCurrent ? 'bg-indigo-50 text-indigo-600 border-r-4 border-indigo-600' : 'text-gray-600 hover:bg-indigo-50 hover:text-indigo-600';
    return `
        <a href="${url}" class="flex items-center px-4 py-3 ${activeClass} transition-colors">
            <svg class="h-5 w-5 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${iconPath}" />
            </svg>
            <span class="sidebar-text truncate">${name}</span>
        </a>
    `;
}

/* --- Lookup Modal Logic --- */
function initializeLookupSystem() {
    // Create Modal HTML
    const modalHTML = `
        <div id="lookup-modal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full hidden z-[60]">
            <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-1/2 shadow-lg rounded-md bg-white">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-medium text-gray-900" id="modal-title">Select Item</h3>
                    <button class="text-gray-400 hover:text-gray-500" onclick="closeLookupModal()">
                        <span class="text-2xl">&times;</span>
                    </button>
                </div>
                <div class="mb-4">
                    <input type="text" id="lookup-search" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" placeholder="Search...">
                </div>
                <div id="lookup-results" class="max-h-60 overflow-y-auto border-t border-gray-200">
                    <!-- Results here -->
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Initial Bindings
    document.addEventListener('click', (e) => {
        if (e.target.closest('.lookup-btn')) {
            const btn = e.target.closest('.lookup-btn');
            const targetIdField = btn.dataset.targetId;
            const targetNameField = btn.dataset.targetName;
            const table = btn.dataset.table;
            openLookupModal(table, targetIdField, targetNameField);
        }
    });

    document.getElementById('lookup-search').addEventListener('input', filterResults);
}

let currentLookupTable = '';
let currentTargetIdField = '';
let currentTargetNameField = '';
let currentData = [];

function openLookupModal(table, idFieldId, nameFieldId) {
    currentLookupTable = table;
    currentTargetIdField = idFieldId;
    currentTargetNameField = nameFieldId;

    // Fetch data from mockDB
    currentData = getData(table);

    renderResults(currentData);

    document.getElementById('modal-title').innerText = `Select ${table.slice(0, -1)}`; // Remove 's' roughly
    document.getElementById('lookup-search').value = '';
    document.getElementById('lookup-modal').classList.remove('hidden');
}

function closeLookupModal() {
    document.getElementById('lookup-modal').classList.add('hidden');
}

function renderResults(data) {
    const container = document.getElementById('lookup-results');
    container.innerHTML = '';

    if (data.length === 0) {
        container.innerHTML = '<div class="p-3 text-gray-500 text-center">No results found</div>';
        return;
    }

    data.forEach(item => {
        const div = document.createElement('div');
        div.className = 'p-3 hover:bg-gray-100 cursor-pointer border-b border-gray-100 flex justify-between items-center';
        div.innerHTML = `
            <span class="font-medium">${item.name}</span>
            <span class="text-xs text-gray-400">#${item.id}</span>
        `;
        div.onclick = () => selectItem(item);
        container.appendChild(div);
    });
}

function selectItem(item) {
    if (currentTargetIdField) {
        document.getElementById(currentTargetIdField).value = item.id;
    }
    if (currentTargetNameField) {
        document.getElementById(currentTargetNameField).value = item.name;
    }
    closeLookupModal();
}

function filterResults(e) {
    const term = e.target.value.toLowerCase();
    const filtered = currentData.filter(item => item.name.toLowerCase().includes(term));
    renderResults(filtered);
}
