// State variables
let currentRelPath = ""; // Path relative to home directory
let allItems = []; // All items in the current directory
let selectedItem = null; // Currently selected item object

// DOM Elements
const filesList = document.getElementById('files-list');
const btnBack = document.getElementById('btn-back');
const addressSegments = document.getElementById('address-segments');
const searchInput = document.getElementById('search-input');
const previewPane = document.getElementById('preview-pane');
const btnClosePreview = document.getElementById('btn-close-preview');

// Sidebar places buttons
const places = {
    home: { btn: document.getElementById('btn-home'), path: "" },
    desktop: { btn: document.getElementById('btn-desktop'), path: "Desktop" },
    documents: { btn: document.getElementById('btn-documents'), path: "Documents" },
    downloads: { btn: document.getElementById('btn-downloads'), path: "Downloads" }
};

// Format Bytes to human readable
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Check if file is likely viewable text
function isTextFile(filename) {
    const textExtensions = [
        'txt', 'md', 'py', 'js', 'json', 'html', 'css', 'xml', 'yml', 'yaml', 
        'ini', 'conf', 'sh', 'bash', 'cfg', 'csv', 'log', 'lua', 'toml'
    ];
    const ext = filename.split('.').pop().toLowerCase();
    return textExtensions.includes(ext) || !filename.includes('.'); // Guess plain files
}

// Generate file type icons
function getFileIcon(item) {
    if (item.is_dir) return '📁';
    
    const ext = item.name.split('.').pop().toLowerCase();
    switch (ext) {
        case 'pdf': return '📕';
        case 'zip': case 'tar': case 'gz': case 'rar': case '7z': return '📦';
        case 'png': case 'jpg': case 'jpeg': case 'gif': case 'svg': case 'webp': return '🖼️';
        case 'mp3': case 'wav': case 'ogg': case 'flac': return '🎵';
        case 'mp4': case 'mkv': case 'avi': case 'mov': return '🎥';
        case 'doc': case 'docx': case 'odt': return '📘';
        case 'xls': case 'xlsx': case 'ods': return '📗';
        case 'ppt': case 'pptx': return '📙';
        case 'txt': case 'md': return '📝';
        case 'py': case 'js': case 'html': case 'css': case 'json': case 'sh': case 'lua': return '💻';
        default: return '📄';
    }
}

// Render breadcrumbs/address segments
function renderBreadcrumbs(relPath) {
    addressSegments.innerHTML = '';
    
    // Always start with Home
    const homeSpan = document.createElement('span');
    homeSpan.textContent = 'Home';
    homeSpan.addEventListener('click', () => navigateToPath(""));
    addressSegments.appendChild(homeSpan);
    
    if (!relPath) return;
    
    const parts = relPath.split('/').filter(p => p);
    let accumPath = "";
    
    parts.forEach(part => {
        const separator = document.createElement('span');
        separator.textContent = ' / ';
        separator.className = 'separator';
        addressSegments.appendChild(separator);
        
        accumPath += (accumPath ? '/' : '') + part;
        const currentPathCopy = accumPath; // Closure snapshot
        
        const segment = document.createElement('span');
        segment.textContent = part;
        segment.addEventListener('click', () => navigateToPath(currentPathCopy));
        addressSegments.appendChild(segment);
    });
}

// Load files in the directory
function loadDirectory(subpath) {
    filesList.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Reading files...</p>
        </div>
    `;
    closePreview();
    
    // Interact with PyWebView Python API
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.list_directory(subpath)
            .then(response => {
                if (response.success) {
                    currentRelPath = response.rel_path;
                    allItems = response.items;
                    renderBreadcrumbs(currentRelPath);
                    renderFiles(allItems);
                    updateSidebarHighlight(currentRelPath);
                } else {
                    renderError(response.error || "Failed to load directory");
                }
            })
            .catch(err => {
                renderError(err.toString());
            });
    } else {
        renderError("Python API not ready. Are you running this in PyWebView?");
    }
}

function renderError(message) {
    filesList.innerHTML = `
        <div class="error-state">
            <span style="font-size: 48px;">⚠️</span>
            <p>Error listing directory:</p>
            <p style="color: var(--accent-rose); font-family: var(--font-mono); margin-top: 8px;">${message}</p>
        </div>
    `;
}

function renderFiles(items) {
    if (items.length === 0) {
        filesList.innerHTML = `
            <div class="empty-state">
                <span style="font-size: 48px;">📭</span>
                <p>This directory is empty</p>
            </div>
        `;
        return;
    }
    
    filesList.innerHTML = '';
    items.forEach((item, index) => {
        const row = document.createElement('div');
        row.className = 'file-item';
        row.dataset.index = index;
        
        const sizeText = item.is_dir ? '--' : formatBytes(item.size);
        
        row.innerHTML = `
            <div class="file-name-col">
                <span class="file-icon">${getFileIcon(item)}</span>
                <span class="file-name-text">${item.name}</span>
            </div>
            <div class="file-size-col">${sizeText}</div>
            <div class="file-modified-col">${item.modified}</div>
        `;
        
        // Single Click -> Selection and Details
        row.addEventListener('click', (e) => {
            selectItem(index, row);
        });
        
        // Double Click -> Navigate folder or Preview file
        row.addEventListener('dblclick', () => {
            if (item.is_dir) {
                navigateToPath(item.rel_path);
            } else {
                showPreview(item);
            }
        });
        
        filesList.appendChild(row);
    });
}

// Set up UI actions for selected items
function selectItem(index, rowElement) {
    // Clear selection
    document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected'));
    
    selectedItem = allItems[index];
    rowElement.classList.add('selected');
    
    showPreview(selectedItem);
}

function navigateToPath(relPath) {
    loadDirectory(relPath);
}

// Side pane preview actions
function showPreview(item) {
    selectedItem = item;
    
    document.getElementById('preview-file-icon').textContent = getFileIcon(item);
    document.getElementById('preview-filename').textContent = item.name;
    document.getElementById('preview-size').textContent = item.is_dir ? 'Directory' : formatBytes(item.size);
    document.getElementById('preview-modified').textContent = item.modified;
    document.getElementById('preview-path').textContent = item.rel_path ? `~/` + item.rel_path : `~`;
    
    const previewContentSection = document.getElementById('preview-content-section');
    const textContentEl = document.getElementById('preview-text-content');
    
    previewContentSection.classList.add('hidden');
    textContentEl.textContent = '';
    
    if (!item.is_dir && isTextFile(item.name) && item.size < 5000000) { // Limit to files < 5MB for safety
        textContentEl.textContent = 'Loading preview...';
        previewContentSection.classList.remove('hidden');
        
        if (window.pywebview && window.pywebview.api) {
            window.pywebview.api.read_file_preview(item.rel_path)
                .then(res => {
                    if (res.success) {
                        textContentEl.textContent = res.content;
                        if (res.truncated) {
                            textContentEl.textContent += '\n\n[Preview truncated due to size...]';
                        }
                    } else {
                        textContentEl.textContent = 'Error: ' + res.error;
                    }
                })
                .catch(err => {
                    textContentEl.textContent = 'Failed to load content: ' + err.toString();
                });
        }
    }
    
    previewPane.classList.remove('hidden');
}

function closePreview() {
    previewPane.classList.add('hidden');
    selectedItem = null;
    document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected'));
}

// Update highlighting on sidebar folders
function updateSidebarHighlight(relPath) {
    // Reset all
    Object.values(places).forEach(p => p.btn.classList.remove('active'));
    
    // Match current path to preset paths
    if (relPath === "") {
        places.home.btn.classList.add('active');
    } else if (relPath === "Desktop") {
        places.desktop.btn.classList.add('active');
    } else if (relPath === "Documents") {
        places.documents.btn.classList.add('active');
    } else if (relPath === "Downloads") {
        places.downloads.btn.classList.add('active');
    }
}

// Setup Event Listeners
function setupListeners() {
    // Close preview button
    btnClosePreview.addEventListener('click', closePreview);
    
    // Go Up button
    btnBack.addEventListener('click', () => {
        if (!currentRelPath) return; // Already at home
        
        const segments = currentRelPath.split('/').filter(s => s);
        segments.pop(); // Remove last segment
        const parentPath = segments.join('/');
        navigateToPath(parentPath);
    });
    
    // Search input (instant client side filtering)
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
            renderFiles(allItems);
            return;
        }
        
        const filtered = allItems.filter(item => 
            item.name.toLowerCase().includes(query)
        );
        renderFiles(filtered);
    });
    
    // Places sidebar listeners
    Object.values(places).forEach(place => {
        place.btn.addEventListener('click', () => {
            navigateToPath(place.path);
        });
    });
}

// Start application
window.addEventListener('pywebviewready', () => {
    setupListeners();
    loadDirectory(""); // Load home directory initially
});
