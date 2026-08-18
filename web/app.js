// State variables
let currentRelPath = ""; // Path relative to home or drive base
let currentPath = ""; // Active absolute path
let currentIsDrive = false; // Is the current path on a FreeWrite drive
let currentParentPath = null; // Calculated parent path for the "Up" button
let syncFolderName = ""; // Tracks currently active sync folder name
let copyEmptyFolders = false; // Tracks empty directory sync setting
let theme = "system"; // Tracks active theme setting
let syncFolderPrefix = ""; // Tracks sync folder prefix setting
let convertToDocx = false; // Tracks convert to DOCX sync setting
let docxDoublespace = false; // Tracks double space DOCX setting
let docxIndentFirstLine = false; // Tracks indent first line setting
let docxSpaceBefore = false; // Tracks space before paragraph setting
let docxSpaceAfter = false; // Tracks space after paragraph setting
let allItems = []; // All items in the current directory

function applyTheme(themeName) {
    const root = document.documentElement;
    if (themeName === 'light') {
        root.classList.add('light');
        root.classList.remove('dark');
    } else if (themeName === 'dark') {
        root.classList.add('dark');
        root.classList.remove('light');
    } else {
        root.classList.remove('light', 'dark');
    }
}
let selectedItem = null; // Currently selected item object
let driveButtons = []; // Dynamic drive elements in the sidebar

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
    sync: { btn: document.getElementById('btn-sync'), path: "" },
    documents: { btn: document.getElementById('btn-documents'), path: "Documents" }
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
// Render breadcrumbs/address segments
function renderBreadcrumbs(response) {
    addressSegments.innerHTML = '';

    // Start segment: either "Home" or the drive name
    const startSpan = document.createElement('span');
    if (response.is_drive) {
        startSpan.textContent = response.drive_name;
        startSpan.addEventListener('click', () => navigateToPath(response.drive_base));
    } else {
        startSpan.textContent = 'Home';
        startSpan.addEventListener('click', () => navigateToPath(""));
    }
    addressSegments.appendChild(startSpan);

    if (!response.rel_path) return;

    const parts = response.rel_path.split(/[/\\]/).filter(p => p);
    let accumPath = response.is_drive ? response.drive_base : "";
    const isWindows = response.current_path.includes('\\') || (response.drive_base && response.drive_base.includes('\\'));
    const separatorChar = isWindows ? '\\' : '/';

    parts.forEach(part => {
        const separator = document.createElement('span');
        separator.textContent = ' / ';
        separator.className = 'separator';
        addressSegments.appendChild(separator);

        if (accumPath) {
            accumPath += (accumPath.endsWith(separatorChar) ? '' : separatorChar) + part;
        } else {
            accumPath = part;
        }
        const currentPathCopy = accumPath; // Closure snapshot

        const segment = document.createElement('span');
        segment.textContent = part;
        segment.addEventListener('click', () => navigateToPath(currentPathCopy));
        addressSegments.appendChild(segment);
    });
}

// Load files in the directory
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
                    currentPath = response.current_path;
                    currentIsDrive = response.is_drive;
                    currentRelPath = response.rel_path;
                    currentParentPath = response.parent_path;
                    syncFolderName = response.sync_folder_name || "";
                    copyEmptyFolders = response.copy_empty_folders || false;
                    theme = response.theme || "system";
                    syncFolderPrefix = response.sync_folder_prefix || "";
                    convertToDocx = response.convert_to_docx || false;
                    docxDoublespace = response.docx_doublespace || false;
                    docxIndentFirstLine = response.docx_indent_first_line || false;
                    docxSpaceBefore = response.docx_space_before || false;
                    docxSpaceAfter = response.docx_space_after || false;
                    applyTheme(theme);

                    // Update Sync Folder shortcut path and visibility
                    if (syncFolderName) {
                        places.sync.path = syncFolderName;
                        places.sync.btn.classList.remove('hidden');
                    } else {
                        places.sync.btn.classList.add('hidden');
                    }

                    allItems = response.items;

                    renderBreadcrumbs(response);
                    renderFiles(allItems);
                    loadDrives(); // Dynamically refresh drives

                    // Enable/disable Up button based on whether we can go up
                    const btnBack = document.getElementById('btn-back');
                    if (currentParentPath !== null) {
                        btnBack.disabled = false;
                        btnBack.style.opacity = '1';
                        btnBack.style.cursor = 'pointer';
                    } else {
                        btnBack.disabled = true;
                        btnBack.style.opacity = '0.5';
                        btnBack.style.cursor = 'not-allowed';
                    }

                    updateSidebarHighlight(response);
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

function loadDrives() {
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.get_freewrite_drives()
            .then(response => {
                if (response.success) {
                    renderDrives(response.drives);
                }
            })
            .catch(err => {
                console.error("Failed to load drives:", err);
            });
    }
}

function renderDrives(drives) {
    const sectionDrives = document.getElementById('section-drives');
    const drivesList = document.getElementById('drives-list');
    if (!sectionDrives || !drivesList) return;

    drivesList.innerHTML = '';
    driveButtons = [];

    if (drives && drives.length > 0) {
        sectionDrives.classList.remove('hidden');
        drives.forEach(drive => {
            const btn = document.createElement('button');
            btn.className = 'nav-item';
            btn.innerHTML = `
                <span class="item-icon" style="display: flex; align-items: center; color: var(--text-secondary);">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
                </span>
                <span class="item-label">${drive.name}</span>
            `;
            btn.addEventListener('click', () => {
                navigateToPath(drive.path);
            });
            drivesList.appendChild(btn);
            driveButtons.push({ btn: btn, path: drive.path });
        });

        // Highlight active drive if currently viewing a drive
        if (currentIsDrive) {
            const normalizedCurrent = currentPath.replace(/\\/g, '/');
            const activeDrive = driveButtons.find(db => {
                const normalizedDb = db.path.replace(/\\/g, '/');
                return normalizedCurrent === normalizedDb || normalizedCurrent.startsWith(normalizedDb + '/');
            });
            if (activeDrive) {
                activeDrive.btn.classList.add('active');
            }
        }
    } else {
        sectionDrives.classList.add('hidden');
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

        // Right Click Context Menu (Directories only)
        if (item.is_dir) {
            row.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                showContextMenu(e, item);
            });
        }

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
function updateSidebarHighlight(response) {
    // Reset all
    Object.values(places).forEach(p => p.btn.classList.remove('active'));
    driveButtons.forEach(db => db.btn.classList.remove('active'));

    if (response.is_drive) {
        const normalizedCurrent = response.current_path.replace(/\\/g, '/');
        const activeDrive = driveButtons.find(db => {
            const normalizedDb = db.path.replace(/\\/g, '/');
            return normalizedCurrent === normalizedDb || normalizedCurrent.startsWith(normalizedDb + '/');
        });
        if (activeDrive) {
            activeDrive.btn.classList.add('active');
        }
    } else {
        const relPath = response.rel_path.replace(/\\/g, '/');
        if (syncFolderName && (relPath === syncFolderName.replace(/\\/g, '/') || relPath.startsWith(syncFolderName.replace(/\\/g, '/') + '/'))) {
            places.sync.btn.classList.add('active');
        } else if (relPath === "") {
            places.home.btn.classList.add('active');
        } else if (relPath === "Documents" || relPath.startsWith("Documents/")) {
            places.documents.btn.classList.add('active');
        }
    }
}

// Setup Event Listeners
function setupListeners() {
    // Close preview button
    btnClosePreview.addEventListener('click', closePreview);

    // Go Up button
    btnBack.addEventListener('click', () => {
        if (currentParentPath !== null) {
            navigateToPath(currentParentPath);
        }
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

    // Preferences modal listeners
    setupPreferencesListeners();

    // Setup Context Menu Action
    const menuSetSync = document.getElementById('menu-set-sync');
    if (menuSetSync) {
        menuSetSync.addEventListener('click', () => {
            if (menuSetSync.classList.contains('disabled') || !contextMenuItem) return;

            const isCurrentSync = (contextMenuItem.rel_path.replace(/\\/g, '/').toLowerCase() === syncFolderName.replace(/\\/g, '/').toLowerCase());
            // If already sync folder, toggle it off (set empty). Otherwise set it as sync folder.
            const targetValue = isCurrentSync ? "" : contextMenuItem.rel_path;

            if (window.pywebview && window.pywebview.api && window.pywebview.api.save_preferences) {
                window.pywebview.api.save_preferences(targetValue, copyEmptyFolders, theme, syncFolderPrefix, convertToDocx, false, docxDoublespace, docxIndentFirstLine, docxSpaceBefore, docxSpaceAfter)
                    .then(res => {
                        if (res.success) {
                            closeContextMenu();
                            loadDirectory(currentRelPath); // Refresh view to show updated highlighting / status
                        } else {
                            alert("Error updating sync folder: " + res.error);
                        }
                    });
            }
        });
    }

    // Dismiss context menu on click elsewhere
    document.addEventListener('click', () => closeContextMenu());
    document.addEventListener('contextmenu', (e) => {
        if (!e.target.closest('.file-item')) {
            closeContextMenu();
        }
    });

    // Setup Sync Trigger Action
    const btnTriggerSync = document.getElementById('btn-trigger-sync');
    const modalSyncStatus = document.getElementById('modal-sync-status');
    const btnCloseSyncModal = document.getElementById('btn-close-sync-modal');
    const btnDoneSync = document.getElementById('btn-done-sync');



    const btnCheckDrives = document.getElementById('btn-check-drives');
    if (btnCheckDrives) {
        btnCheckDrives.addEventListener('click', () => {
            loadDrives();
        });

    }


    if (btnTriggerSync && modalSyncStatus) {
        btnTriggerSync.addEventListener('click', () => {
            const syncModalTitle = document.getElementById('sync-modal-title');
            const syncStateLoading = document.getElementById('sync-state-loading');
            const syncStateResults = document.getElementById('sync-state-results');

            // Initial loading state setup
            syncModalTitle.textContent = "Synchronizing";
            syncStateLoading.style.display = 'flex';
            syncStateResults.classList.add('hidden');
            btnDoneSync.classList.add('hidden');
            btnCloseSyncModal.disabled = true;
            btnCloseSyncModal.style.opacity = '0.3';

            modalSyncStatus.classList.remove('hidden');

            if (window.pywebview && window.pywebview.api && window.pywebview.api.trigger_sync) {
                window.pywebview.api.trigger_sync()
                    .then(res => {
                        btnCloseSyncModal.disabled = false;
                        btnCloseSyncModal.style.opacity = '1';
                        syncStateLoading.style.display = 'none';
                        syncStateResults.classList.remove('hidden');
                        btnDoneSync.classList.remove('hidden');

                        const summaryEl = document.getElementById('sync-results-summary');
                        const listEl = document.getElementById('sync-results-list');
                        listEl.innerHTML = '';

                        if (res.success) {
                            syncModalTitle.textContent = "Sync Complete";

                            const copiedCount = res.synced.filter(f => f.status === "copied").length;
                            const identicalCount = res.synced.filter(f => f.status === "identical").length;
                            const failedCount = res.failed.length;

                            summaryEl.innerHTML = `
                                <span style="color: #4ade80;">Success!</span> Scanned drives: ${res.drives_scanned.join(', ')}.<br>
                                <span style="font-size: 13px; color: var(--text-secondary); font-weight: normal;">
                                    Copied: ${copiedCount} | Identical (Skipped): ${identicalCount} | Failed: ${failedCount}
                                </span>
                            `;

                            // Render list of files
                            res.synced.forEach(f => {
                                const item = document.createElement('div');
                                item.style.fontSize = '12px';
                                item.style.display = 'flex';
                                item.style.justifyContent = 'space-between';
                                if (f.status === "copied") {
                                    item.innerHTML = `<span style="color: #38bdf8;">✓ ${f.file}</span> <span style="color: var(--text-muted);">Copied</span>`;
                                } else {
                                    item.innerHTML = `<span style="color: var(--text-secondary);">✓ ${f.file}</span> <span style="color: var(--text-muted);">Identical</span>`;
                                }
                                listEl.appendChild(item);
                            });

                            res.failed.forEach(f => {
                                const item = document.createElement('div');
                                item.style.fontSize = '12px';
                                item.style.color = '#ef4444';
                                item.innerHTML = `<span>✗ ${f.file}</span> <span>Error: ${f.error}</span>`;
                                listEl.appendChild(item);
                            });

                            // Automatically reload directory listing in browser workspace to show synced items
                            loadDirectory(currentRelPath);
                        } else {
                            syncModalTitle.textContent = "Sync Failed";
                            summaryEl.innerHTML = `<span style="color: #ef4444;">Error:</span> ${res.error || "Unknown synchronization failure."}`;
                        }
                    })
                    .catch(err => {
                        btnCloseSyncModal.disabled = false;
                        btnCloseSyncModal.style.opacity = '1';
                        syncStateLoading.style.display = 'none';
                        syncStateResults.classList.remove('hidden');
                        btnDoneSync.classList.remove('hidden');

                        document.getElementById('sync-modal-title').textContent = "Sync Error";
                        document.getElementById('sync-results-summary').innerHTML = `<span style="color: #ef4444;">Unhandled Error:</span> ${err.toString()}`;
                    });
            } else {
                // Fail-safe if API is missing
                setTimeout(() => {
                    btnCloseSyncModal.disabled = false;
                    btnCloseSyncModal.style.opacity = '1';
                    syncStateLoading.style.display = 'none';
                    syncStateResults.classList.remove('hidden');
                    btnDoneSync.classList.remove('hidden');
                    document.getElementById('sync-modal-title').textContent = "API Error";
                    document.getElementById('sync-results-summary').textContent = "Python trigger_sync endpoint not loaded.";
                }, 1000);
            }
        });

        const closeSyncModal = () => modalSyncStatus.classList.add('hidden');
        btnCloseSyncModal.addEventListener('click', closeSyncModal);
        btnDoneSync.addEventListener('click', closeSyncModal);
    }
}

let contextMenuItem = null; // Tracks folder being acted upon

function showContextMenu(e, item) {
    const menu = document.getElementById('folder-context-menu');
    const menuSetSync = document.getElementById('menu-set-sync');
    const checkbox = document.getElementById('menu-sync-checkbox');
    if (!menu) return;

    contextMenuItem = item;

    // Position menu near cursor
    menu.style.left = `${e.clientX}px`;
    menu.style.top = `${e.clientY}px`;

    // Check if this folder is the active sync folder
    const isCurrentSync = (item.rel_path.replace(/\\/g, '/').toLowerCase() === syncFolderName.replace(/\\/g, '/').toLowerCase());
    checkbox.textContent = isCurrentSync ? '☑' : '☐';

    // Disable sync mapping option if we are inside an external drive
    if (currentIsDrive) {
        menuSetSync.classList.add('disabled');
        menuSetSync.style.opacity = '0.5';
        menuSetSync.style.cursor = 'not-allowed';
    } else {
        menuSetSync.classList.remove('disabled');
        menuSetSync.style.opacity = '1';
        menuSetSync.style.cursor = 'pointer';
    }

    menu.classList.remove('hidden');
}

function closeContextMenu() {
    const menu = document.getElementById('folder-context-menu');
    if (menu) {
        menu.classList.add('hidden');
    }
    contextMenuItem = null;
}

// Global listener to open external http/https links in system default browser
document.addEventListener('click', (e) => {
    const anchor = e.target.closest && e.target.closest('a');
    if (anchor && anchor.href && (anchor.href.startsWith('http://') || anchor.href.startsWith('https://'))) {
        e.preventDefault();
        if (window.pywebview && window.pywebview.api && window.pywebview.api.open_external) {
            window.pywebview.api.open_external(anchor.href);
        }
    }
});

// Setup preferences modal listeners
function setupPreferencesListeners() {
    const modalPreferences = document.getElementById('modal-preferences');
    const btnPreferences = document.getElementById('btn-preferences');
    const btnClosePreferences = document.getElementById('btn-close-preferences');
    const btnCancelPreferences = document.getElementById('btn-cancel-preferences');
    const btnSavePreferences = document.getElementById('btn-save-preferences');
    const inputSyncFolder = document.getElementById('input-sync-folder');
    const inputCopyEmpty = document.getElementById('input-copy-empty');
    const themeSelector = document.getElementById('theme-selector');
    const themeOpts = themeSelector ? themeSelector.querySelectorAll('.theme-opt') : [];
    const inputFolderPrefix = document.getElementById('input-folder-prefix');
    const inputConvertDocx = document.getElementById('input-convert-docx');
    const inputDocxDoublespace = document.getElementById('input-docx-doublespace');
    const inputDocxIndentFirstLine = document.getElementById('input-docx-indent-first-line');
    const inputDocxSpaceBefore = document.getElementById('input-docx-space-before');
    const inputDocxSpaceAfter = document.getElementById('input-docx-space-after');
    const inputStripDatePrefix = document.getElementById('input-strip-date-prefix');
    const inputAllowedLabels = document.getElementById('input-allowed-labels');

    const tabBtnGeneral = document.getElementById('tab-btn-general');
    const tabBtnWord = document.getElementById('tab-btn-word');
    const tabPanelGeneral = document.getElementById('tab-panel-general');
    const tabPanelWord = document.getElementById('tab-panel-word');

    if (tabBtnGeneral && tabBtnWord && tabPanelGeneral && tabPanelWord) {
        tabBtnGeneral.addEventListener('click', () => {
            tabBtnGeneral.classList.add('active');
            tabBtnWord.classList.remove('active');
            tabPanelGeneral.classList.remove('hidden');
            tabPanelWord.classList.add('hidden');
        });
        tabBtnWord.addEventListener('click', () => {
            tabBtnWord.classList.add('active');
            tabBtnGeneral.classList.remove('active');
            tabPanelWord.classList.remove('hidden');
            tabPanelGeneral.classList.add('hidden');
        });
    }

    if (!modalPreferences || !btnPreferences) return;

    // Toggle active segment buttons on click
    themeOpts.forEach(opt => {
        opt.addEventListener('click', () => {
            themeOpts.forEach(o => o.classList.remove('active'));
            opt.classList.add('active');
        });
    });

    btnPreferences.addEventListener('click', () => {
        if (window.pywebview && window.pywebview.api && window.pywebview.api.get_preferences) {
            window.pywebview.api.get_preferences()
                .then(res => {
                    if (res.success) {
                        inputSyncFolder.value = res.sync_folder_name || "";
                        inputCopyEmpty.checked = res.copy_empty_folders || false;
                        // Set version display if element exists
                        const versionEl = document.getElementById('version-display');
                        if (versionEl) {
                            versionEl.textContent = res.version || '';
                        }
                        if (inputConvertDocx) {
                            inputConvertDocx.checked = res.convert_to_docx || false;
                        }
                        if (inputDocxDoublespace) {
                            inputDocxDoublespace.checked = res.docx_doublespace || false;
                        }
                        if (inputDocxIndentFirstLine) {
                            inputDocxIndentFirstLine.checked = res.docx_indent_first_line || false;
                        }
                        if (inputDocxSpaceBefore) {
                            inputDocxSpaceBefore.checked = res.docx_space_before || false;
                        }
                        if (inputDocxSpaceAfter) {
                            inputDocxSpaceAfter.checked = res.docx_space_after || false;
                        }
                        if (inputAllowedLabels) {
                            const labels = res.allowed_labels;
                            if (Array.isArray(labels)) {
                                inputAllowedLabels.value = labels.join(', ');
                            } else if (typeof labels === 'string') {
                                inputAllowedLabels.value = labels;
                            } else {
                                inputAllowedLabels.value = 'freewrite, traveler, alpha';
                            }
                        }

                        const activeTheme = res.theme || "system";
                        themeOpts.forEach(opt => {
                            if (opt.dataset.value === activeTheme) {
                                opt.classList.add('active');
                            } else {
                                opt.classList.remove('active');
                            }
                        });

                        inputFolderPrefix.value = res.sync_folder_prefix || "";
                        inputStripDatePrefix.checked = res.strip_date_prefix || false;
                    }
                    modalPreferences.classList.remove('hidden');
                });
        } else {
            modalPreferences.classList.remove('hidden');
        }
    });

    const closeModal = () => modalPreferences.classList.add('hidden');
    btnClosePreferences.addEventListener('click', closeModal);
    btnCancelPreferences.addEventListener('click', closeModal);

    btnSavePreferences.addEventListener('click', () => {
        const value = inputSyncFolder.value.trim();
        const copyEmpty = inputCopyEmpty.checked;
        const activeOpt = themeSelector ? themeSelector.querySelector('.theme-opt.active') : null;
        const themeVal = activeOpt ? activeOpt.dataset.value : "system";
        const folderPrefix = inputFolderPrefix.value;
        const convertToDocxVal = inputConvertDocx ? inputConvertDocx.checked : false;
        const docxDoublespaceVal = inputDocxDoublespace ? inputDocxDoublespace.checked : false;
        const docxIndentFirstLineVal = inputDocxIndentFirstLine ? inputDocxIndentFirstLine.checked : false;
        const docxSpaceBeforeVal = inputDocxSpaceBefore ? inputDocxSpaceBefore.checked : false;
        const docxSpaceAfterVal = inputDocxSpaceAfter ? inputDocxSpaceAfter.checked : false;
        const allowedLabelsVal = inputAllowedLabels ? inputAllowedLabels.value : "";

        if (window.pywebview && window.pywebview.api && window.pywebview.api.save_preferences) {
            window.pywebview.api.save_preferences(
                value,
                copyEmpty,
                themeVal,
                folderPrefix,
                convertToDocxVal,
                inputStripDatePrefix ? inputStripDatePrefix.checked : false,
                docxDoublespaceVal,
                docxIndentFirstLineVal,
                docxSpaceBeforeVal,
                docxSpaceAfterVal,
                allowedLabelsVal
            )
                .then(res => {
                    if (res.success) {
                        theme = themeVal;
                        convertToDocx = convertToDocxVal;
                        docxDoublespace = docxDoublespaceVal;
                        docxIndentFirstLine = docxIndentFirstLineVal;
                        docxSpaceBefore = docxSpaceBeforeVal;
                        docxSpaceAfter = docxSpaceAfterVal;
                        applyTheme(theme);
                        closeModal();
                        navigateToPath(value); // Open/display the sync folder in the main window
                    } else {
                        alert("Error saving preferences: " + (res.error || "Unknown error"));
                    }
                })
                .catch(err => {
                    alert("Failed to save: " + err.toString());
                });
        }
    });
}

// Start application
window.addEventListener('pywebviewready', () => {
    setupListeners();
    loadDrives(); // Initially load drives

    // Fetch and load startup directory path
    if (window.pywebview && window.pywebview.api && window.pywebview.api.get_startup_path) {
        window.pywebview.api.get_startup_path()
            .then(path => {
                loadDirectory(path || "");
            })
            .catch(() => {
                loadDirectory("");
            });
    } else {
        loadDirectory("");
    }
});
