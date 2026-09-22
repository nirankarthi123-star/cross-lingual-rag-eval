const fileInput = document.getElementById('file-input');
const sourceUrl = document.getElementById('source-url');
const uploadBtn = document.getElementById('upload-btn');
const selectedFileText = document.getElementById('selected-file');
const uploadStatus = document.getElementById('upload-status');
const uploadForm = document.getElementById('upload-form');

const ingestBtn = document.getElementById('ingest-btn');
const ingestStatus = document.getElementById('ingest-status');

// Handle file selection
fileInput.addEventListener('change', (e) => {
    if (fileInput.files.length > 0) {
        selectedFileText.textContent = `Selected: ${fileInput.files[0].name}`;
        checkFormValidity();
    } else {
        selectedFileText.textContent = 'No file selected';
        uploadBtn.disabled = true;
    }
});

sourceUrl.addEventListener('input', checkFormValidity);

function checkFormValidity() {
    if (fileInput.files.length > 0 && sourceUrl.value.trim() !== '') {
        uploadBtn.disabled = false;
    } else {
        uploadBtn.disabled = true;
    }
}

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (fileInput.files.length === 0) return;

    uploadBtn.disabled = true;
    uploadStatus.textContent = 'Uploading...';
    uploadStatus.className = 'status-msg';

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('source_url', sourceUrl.value.trim());

    try {
        const res = await fetch('/api/documents/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        
        if (res.ok) {
            uploadStatus.textContent = `Success: ${data.message} (${data.filename})`;
            uploadStatus.className = 'status-msg success';
            fileInput.value = '';
            sourceUrl.value = '';
            selectedFileText.textContent = 'No file selected';
        } else {
            uploadStatus.textContent = `Error: ${data.detail || data.message}`;
            uploadStatus.className = 'status-msg error';
        }
    } catch (err) {
        uploadStatus.textContent = `Network Error: ${err.message}`;
        uploadStatus.className = 'status-msg error';
    }
    
    checkFormValidity();
});

ingestBtn.addEventListener('click', async () => {
    ingestBtn.disabled = true;
    ingestStatus.textContent = 'Ingesting documents and rebuilding FAISS index (this may take a few minutes)...';
    ingestStatus.className = 'status-msg';
    
    try {
        const res = await fetch('/api/documents/ingest', {
            method: 'POST'
        });
        const data = await res.json();
        
        if (res.ok) {
            ingestStatus.textContent = `Success: ${data.message}`;
            ingestStatus.className = 'status-msg success';
        } else {
            ingestStatus.textContent = `Error: ${data.detail || data.message}`;
            ingestStatus.className = 'status-msg error';
        }
    } catch (err) {
        ingestStatus.textContent = `Network Error: ${err.message}`;
        ingestStatus.className = 'status-msg error';
    }
    
    ingestBtn.disabled = false;
});
