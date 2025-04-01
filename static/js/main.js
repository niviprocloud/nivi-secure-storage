// NiVi Secure Cloud Storage - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // File upload preview functionality
    initFileUploadPreview();
    
    // Dashboard file search functionality
    initFileSearch();
    
    // Initialize tooltips
    initTooltips();
});

/**
 * Initialize file upload preview
 */
function initFileUploadPreview() {
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        const uploadArea = document.querySelector('.upload-area');
        const uploadInfo = document.getElementById('uploadInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        
        // Add drag and drop functionality
        if (uploadArea) {
            uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                uploadArea.classList.add('bg-light');
            });
            
            uploadArea.addEventListener('dragleave', function() {
                uploadArea.classList.remove('bg-light');
            });
            
            uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                uploadArea.classList.remove('bg-light');
                
                if (e.dataTransfer.files.length) {
                    fileInput.files = e.dataTransfer.files;
                    updateFilePreview(e.dataTransfer.files[0]);
                }
            });
            
            // Click on upload area to trigger file input
            uploadArea.addEventListener('click', function() {
                fileInput.click();
            });
        }
        
        // File selection change
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                updateFilePreview(this.files[0]);
            } else if (uploadInfo) {
                uploadInfo.classList.add('d-none');
            }
        });
        
        // Update file preview
        function updateFilePreview(file) {
            if (!uploadInfo || !fileName || !fileSize) return;
            
            uploadInfo.classList.remove('d-none');
            fileName.textContent = file.name;
            
            // Format file size
            if (file.size < 1024) {
                fileSize.textContent = file.size + ' bytes';
            } else if (file.size < 1024 * 1024) {
                fileSize.textContent = (file.size / 1024).toFixed(2) + ' KB';
            } else {
                fileSize.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
            }
        }
    }
}

/**
 * Initialize file search functionality on dashboard
 */
function initFileSearch() {
    const searchInput = document.getElementById('fileSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('tbody tr');
            
            tableRows.forEach(row => {
                const fileName = row.querySelector('td:first-child h6').textContent.toLowerCase();
                if (fileName.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Show loading spinner during file upload
 */
function showUploadSpinner() {
    const form = document.querySelector('form[enctype="multipart/form-data"]');
    const submitBtn = form ? form.querySelector('button[type="submit"]') : null;
    
    if (form && submitBtn) {
        form.addEventListener('submit', function() {
            const fileInput = this.querySelector('input[type="file"]');
            if (fileInput && fileInput.files.length > 0) {
                // Change button text and add spinner
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Encrypting & Uploading...';
                submitBtn.disabled = true;
            }
        });
    }
}