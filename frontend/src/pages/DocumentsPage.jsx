import React, { useState, useEffect, useRef } from 'react';
import { getDocumentStats, uploadDocument, ingestDocuments } from '../services/api';

const ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.csv', '.json'];

export default function DocumentsPage() {
  // Corpus Stats State
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState('');

  // Upload Form State
  const [selectedFile, setSelectedFile] = useState(null);
  const [sourceUrl, setSourceUrl] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // { type: 'success' | 'error', message: string }
  const [uploadValidation, setUploadValidation] = useState('');

  // Ingestion State
  const [ingesting, setIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState(null); // { type: 'success' | 'error', message: string }

  const fileInputRef = useRef(null);
  const dropZoneRef = useRef(null);

  // Fetch Corpus Statistics
  const loadStats = async () => {
    setStatsLoading(true);
    setStatsError('');
    try {
      const data = await getDocumentStats();
      setStats(data);
    } catch (err) {
      setStatsError(err.message || 'Failed to load corpus statistics.');
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  // File Selection Validation
  const handleFileChange = (file) => {
    setUploadValidation('');
    setUploadStatus(null);
    if (!file) {
      setSelectedFile(null);
      return;
    }

    const ext = `.${file.name.split('.').pop().toLowerCase()}`;
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setUploadValidation(`Unsupported file format (${ext}). Allowed types: PDF, TXT, CSV, JSON.`);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    setSelectedFile(file);
  };

  // Drag & Drop Handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (dropZoneRef.current) {
      dropZoneRef.current.style.backgroundColor = 'var(--color-light-blue)';
      dropZoneRef.current.style.borderColor = 'var(--color-baby-blue)';
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (dropZoneRef.current) {
      dropZoneRef.current.style.backgroundColor = 'var(--color-warm-cream)';
      dropZoneRef.current.style.borderColor = 'var(--color-border)';
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (dropZoneRef.current) {
      dropZoneRef.current.style.backgroundColor = 'var(--color-warm-cream)';
      dropZoneRef.current.style.borderColor = 'var(--color-border)';
    }
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  // Handle Document Upload
  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setUploadValidation('Please select a valid document file to upload.');
      return;
    }

    setUploading(true);
    setUploadStatus(null);
    setUploadValidation('');

    try {
      const res = await uploadDocument(selectedFile, sourceUrl.trim());
      setUploadStatus({
        type: 'success',
        message: res.message || `Successfully uploaded file (${res.filename || selectedFile.name}).`,
      });

      // Clear input fields
      setSelectedFile(null);
      setSourceUrl('');
      if (fileInputRef.current) fileInputRef.current.value = '';

      // Refresh real stats
      loadStats();
    } catch (err) {
      setUploadStatus({
        type: 'error',
        message: err.message || 'Failed to upload document.',
      });
    } finally {
      setUploading(false);
    }
  };

  // Handle Document Ingestion / FAISS Rebuild
  const handleIngest = async () => {
    setIngesting(true);
    setIngestStatus(null);

    try {
      const res = await ingestDocuments();
      setIngestStatus({
        type: 'success',
        message: res.message || 'Corpus successfully ingested and FAISS index rebuilt.',
      });

      // Refresh real stats
      loadStats();
    } catch (err) {
      setIngestStatus({
        type: 'error',
        message: err.message || 'Ingestion failed.',
      });
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Real Corpus Statistics Bar */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-dark-text)' }}>
            Active Corpus Statistics
          </h2>
          <button
            onClick={loadStats}
            disabled={statsLoading}
            className="btn btn-secondary"
            style={{ fontSize: '0.78rem', padding: '4px 10px' }}
          >
            {statsLoading ? 'Refreshing…' : 'Refresh Stats'}
          </button>
        </div>

        {statsLoading ? (
          <div style={{ fontSize: '0.85rem', color: 'var(--color-muted-text)', padding: '12px 0' }}>
            Loading corpus statistics from backend…
          </div>
        ) : statsError ? (
          <div style={{ fontSize: '0.85rem', color: 'var(--color-danger)', padding: '10px 14px', backgroundColor: '#FDF0F0', borderRadius: '8px', border: '1px solid #F5C6C6' }}>
            {statsError}
          </div>
        ) : stats ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '12px' }}>
            <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '12px 14px', borderRadius: '10px', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Total Documents</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--color-dark-text)', marginTop: '2px' }}>
                {stats.num_documents}
              </div>
            </div>

            <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '12px 14px', borderRadius: '10px', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Vector Chunks</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--color-dark-text)', marginTop: '2px' }}>
                {stats.num_chunks}
              </div>
            </div>

            <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '12px 14px', borderRadius: '10px', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Avg Chunk Length</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--color-dark-text)', marginTop: '2px' }}>
                {stats.avg_chunk_length ? `${Math.round(stats.avg_chunk_length)} chars` : 'N/A'}
              </div>
            </div>

            <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '12px 14px', borderRadius: '10px', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Document Formats</div>
              <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--color-dark-text)', marginTop: '4px' }}>
                {stats.document_types && Object.keys(stats.document_types).length > 0
                  ? Object.entries(stats.document_types).map(([type, count]) => `${type}: ${count}`).join(', ')
                  : 'None'}
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Upload Document Section */}
      <div className="card">
        <h2 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-dark-text)', marginBottom: '6px' }}>
          Upload Document to Corpus
        </h2>
        <p style={{ fontSize: '0.82rem', color: 'var(--color-muted-text)', marginBottom: '16px' }}>
          Add raw source files to the evaluation corpus. Supported formats: PDF, TXT, CSV, JSON.
        </p>

        <form onSubmit={handleUploadSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Drop Zone / Drag Area */}
          <div
            ref={dropZoneRef}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            style={{
              border: '2px dashed var(--color-border)',
              borderRadius: 'var(--radius-card)',
              backgroundColor: 'var(--color-warm-cream)',
              padding: '28px 20px',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.csv,.json"
              style={{ display: 'none' }}
              onChange={(e) => {
                if (e.target.files && e.target.files.length > 0) {
                  handleFileChange(e.target.files[0]);
                }
              }}
            />

            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-dark-text)' }}>
              {selectedFile ? `Selected: ${selectedFile.name}` : 'Click to select a file, or drag and drop'}
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--color-muted-text)', marginTop: '4px' }}>
              Supported: PDF, TXT, CSV, JSON
            </div>
          </div>

          {/* Validation Error */}
          {uploadValidation && (
            <div style={{ fontSize: '0.82rem', color: 'var(--color-danger)', fontWeight: 500 }}>
              {uploadValidation}
            </div>
          )}

          {/* Source Provenance Field */}
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--color-dark-text)', marginBottom: '6px' }}>
              Source URL / Title (for provenance)
            </label>
            <input
              type="text"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              placeholder="e.g. https://example.com/telecom-faq.pdf or 'Customer FAQ v2'"
              disabled={uploading}
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: 'var(--radius-input)',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-warm-cream)',
                color: 'var(--color-dark-text)',
                fontSize: '0.875rem',
                outline: 'none',
              }}
            />
          </div>

          {/* Submit Action & Status Display */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--color-muted-text)' }}>
              {selectedFile ? `${selectedFile.name} (${(selectedFile.size / 1024).toFixed(1)} KB)` : 'No file selected'}
            </span>

            <button
              type="submit"
              disabled={!selectedFile || uploading}
              className="btn btn-primary"
              style={{ padding: '9px 20px' }}
            >
              {uploading ? 'Uploading…' : 'Upload Document'}
            </button>
          </div>

          {uploadStatus && (
            <div
              style={{
                fontSize: '0.85rem',
                padding: '10px 14px',
                borderRadius: '8px',
                backgroundColor: uploadStatus.type === 'success' ? '#EEF8F2' : '#FDF0F0',
                color: uploadStatus.type === 'success' ? 'var(--color-success)' : 'var(--color-danger)',
                border: `1px solid ${uploadStatus.type === 'success' ? '#C8E8D5' : '#F5C6C6'}`,
              }}
            >
              {uploadStatus.message}
            </div>
          )}
        </form>
      </div>

      {/* Ingest & Rebuild FAISS Index Section */}
      <div className="card">
        <h2 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-dark-text)', marginBottom: '6px' }}>
          Rebuild Vector Index
        </h2>
        <p style={{ fontSize: '0.82rem', color: 'var(--color-muted-text)', lineHeight: 1.5, marginBottom: '16px' }}>
          After uploading new source documents, trigger ingestion to parse files, generate chunk embeddings, and rebuild the FAISS index in memory.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div>
            <button
              type="button"
              onClick={handleIngest}
              disabled={ingesting}
              className="btn btn-secondary"
              style={{
                borderColor: 'var(--color-warning)',
                color: 'var(--color-warning)',
                fontWeight: 600,
              }}
            >
              {ingesting ? 'Ingesting & Rebuilding Index…' : 'Ingest & Rebuild Index'}
            </button>
          </div>

          {ingestStatus && (
            <div
              style={{
                fontSize: '0.85rem',
                padding: '10px 14px',
                borderRadius: '8px',
                backgroundColor: ingestStatus.type === 'success' ? '#EEF8F2' : '#FDF0F0',
                color: ingestStatus.type === 'success' ? 'var(--color-success)' : 'var(--color-danger)',
                border: `1px solid ${ingestStatus.type === 'success' ? '#C8E8D5' : '#F5C6C6'}`,
              }}
            >
              {ingestStatus.message}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
