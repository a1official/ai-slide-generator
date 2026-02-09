// Wav2Lip Video Processing - Main JavaScript

let sessionId = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    setupFileInputs();
    setupForm();
    loadOutputs();
});

// Setup custom file inputs
function setupFileInputs() {
    const videoInput = document.getElementById('videoFile');
    const audioInput = document.getElementById('audioFile');

    videoInput.addEventListener('change', function (e) {
        updateFileDisplay(e.target, 'video');
    });

    audioInput.addEventListener('change', function (e) {
        updateFileDisplay(e.target, 'audio');
    });
}

// Update file input display
function updateFileDisplay(input, type) {
    const display = input.parentElement.querySelector('.file-placeholder');
    if (input.files.length > 0) {
        const file = input.files[0];
        const size = formatFileSize(file.size);
        display.textContent = `${file.name} (${size})`;
        display.style.color = 'var(--text-primary)';
    } else {
        display.textContent = `Choose ${type} file...`;
        display.style.color = 'var(--text-muted)';
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Setup form submission
function setupForm() {
    const form = document.getElementById('uploadForm');
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        await processVideo();
    });
}

// Process video
async function processVideo() {
    const videoFile = document.getElementById('videoFile').files[0];
    const audioFile = document.getElementById('audioFile').files[0];
    const quality = document.querySelector('input[name="quality"]:checked').value;

    if (!videoFile || !audioFile) {
        showError('Please select both video and audio files');
        return;
    }

    // Show processing section
    showSection('processingSection');
    updateProgress(0, 'Uploading files...');
    activateStep(1);

    try {
        // Upload files
        const formData = new FormData();
        formData.append('video', videoFile);
        formData.append('audio', audioFile);

        updateProgress(10, 'Uploading files...');

        const uploadResponse = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            const error = await uploadResponse.json();
            throw new Error(error.error || 'Upload failed');
        }

        const uploadData = await uploadResponse.json();
        sessionId = uploadData.session_id;

        updateProgress(30, 'Files uploaded. Processing video...');
        activateStep(2);

        // Process video
        const processResponse = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                quality: quality
            })
        });

        if (!processResponse.ok) {
            const error = await processResponse.json();
            throw new Error(error.error || 'Processing failed');
        }

        updateProgress(60, 'Detecting faces...');
        activateStep(3);

        // Simulate progress for better UX
        await sleep(1000);
        updateProgress(80, 'Generating lip sync...');
        activateStep(4);

        await sleep(1000);
        updateProgress(100, 'Finalizing video...');

        const processData = await processResponse.json();

        // Show result
        showResult(processData.output_filename, processData.output_url);

        // Reload outputs list
        loadOutputs();

    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    }
}

// Update progress
function updateProgress(percent, text) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    progressFill.style.width = percent + '%';
    progressText.textContent = text;
}

// Activate processing step
function activateStep(stepNumber) {
    // Deactivate all steps
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });

    // Activate current step
    const currentStep = document.getElementById(`step${stepNumber}`);
    if (currentStep) {
        currentStep.classList.add('active');
    }
}

// Show result
function showResult(filename, downloadUrl) {
    showSection('resultSection');

    const videoSource = document.getElementById('videoSource');
    const resultVideo = document.getElementById('resultVideo');
    const downloadBtn = document.getElementById('downloadBtn');

    videoSource.src = downloadUrl.replace('/download/', '/view/');
    resultVideo.load();

    downloadBtn.href = downloadUrl;
    downloadBtn.download = filename;
}

// Show error
function showError(message) {
    showSection('errorSection');
    document.getElementById('errorMessage').textContent = message;
}

// Show section
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.upload-section, .processing-section, .result-section, .error-section').forEach(section => {
        section.classList.add('hidden');
    });

    // Show target section
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.remove('hidden');
    }
}

// Reset form
function resetForm() {
    document.getElementById('uploadForm').reset();

    // Reset file displays
    document.querySelectorAll('.file-placeholder').forEach(placeholder => {
        const type = placeholder.closest('.file-input-group').querySelector('input').name;
        placeholder.textContent = `Choose ${type} file...`;
        placeholder.style.color = 'var(--text-muted)';
    });

    // Reset progress
    updateProgress(0, '');
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });

    // Show upload section
    showSection('uploadSection');

    sessionId = null;
}

// Load outputs
async function loadOutputs() {
    const outputsList = document.getElementById('outputsList');

    try {
        const response = await fetch('/outputs');
        const data = await response.json();

        if (data.outputs && data.outputs.length > 0) {
            outputsList.innerHTML = '';

            data.outputs.forEach(output => {
                const item = createOutputItem(output);
                outputsList.appendChild(item);
            });
        } else {
            outputsList.innerHTML = '<p class="loading-text">No outputs yet</p>';
        }
    } catch (error) {
        console.error('Error loading outputs:', error);
        outputsList.innerHTML = '<p class="loading-text">Failed to load outputs</p>';
    }
}

// Create output item element
function createOutputItem(output) {
    const item = document.createElement('div');
    item.className = 'output-item';

    item.innerHTML = `
        <div class="output-info">
            <div class="output-name">${output.filename}</div>
            <div class="output-meta">
                ${output.created} • ${formatFileSize(output.size)}
            </div>
        </div>
        <div class="output-actions">
            <a href="${output.view_url}" class="output-btn" target="_blank">View</a>
            <a href="${output.download_url}" class="output-btn" download>Download</a>
        </div>
    `;

    return item;
}

// Sleep utility
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Handle browse button clicks
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('browse-btn')) {
        e.preventDefault();
        const input = e.target.closest('.file-input-wrapper').querySelector('input[type="file"]');
        input.click();
    }
});
