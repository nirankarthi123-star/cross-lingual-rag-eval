import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { chat } from '../services/api';

const sampleChips = [
  {
    label: 'How to activate international roaming?',
    query: 'How do I activate international roaming on my mobile postpaid connection?',
  },
  {
    label: 'Tamil-English: Activate roaming',
    query: 'Ennoda mobile postpaid connection-la international roaming eppadi activate panrathu?',
  },
  {
    label: 'Hindi-English: Activate roaming',
    query: 'Mere mobile postpaid connection par international roaming kaise activate karu?',
  },
  {
    label: 'Out-of-context question',
    query: 'What is the capital of Mars?',
  },
];

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');
  const [mitigationEnabled, setMitigationEnabled] = useState(true);
  const [loading, setLoading] = useState(false);
  const [validationError, setValidationError] = useState('');
  const [expandedSources, setExpandedSources] = useState({});

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Handle Textarea Auto-height
  const handleInputChange = (e) => {
    setQuery(e.target.value);
    if (validationError) setValidationError('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleChipClick = (chipQuery) => {
    setQuery(chipQuery);
    setValidationError('');
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const toggleSourceExpand = (msgId, sourceIdx) => {
    const key = `${msgId}-${sourceIdx}`;
    setExpandedSources((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleClearChat = () => {
    if (messages.length > 0) {
      setMessages([]);
      setExpandedSources({});
    }
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      setValidationError('Please enter a query string to evaluate.');
      return;
    }

    setValidationError('');
    setLoading(true);
    const msgId = Date.now();

    // Add transient user query entry
    const userMsg = {
      id: msgId,
      userQuery: trimmedQuery,
      mitigationEnabled,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      loading: true,
      responseData: null,
      error: null,
    };

    setMessages((prev) => [...prev, userMsg]);
    setQuery('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    try {
      const response = await chat(trimmedQuery, mitigationEnabled);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === msgId
            ? { ...msg, loading: false, responseData: response }
            : msg
        )
      );
    } catch (err) {
      const errorMessage = err.isNetworkError
        ? 'Backend server is unreachable. Please verify FastAPI is running on http://localhost:8000.'
        : err.message || 'An unexpected error occurred while communicating with the backend.';

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === msgId
            ? { ...msg, loading: false, error: errorMessage }
            : msg
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Upper Control Bar & Disclaimer */}
      <div
        className="card"
        style={{
          display: 'flex',
          alignItems: 'center',
          justify: 'space-between',
          flexWrap: 'wrap',
          gap: '16px',
          padding: '16px 24px',
        }}
      >
        {/* Mitigation Toggle Control */}
        <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', userSelect: 'none' }}>
          <input
            type="checkbox"
            checked={mitigationEnabled}
            onChange={(e) => setMitigationEnabled(e.target.checked)}
            style={{
              width: '16px',
              height: '16px',
              accentColor: 'var(--color-baby-blue)',
              cursor: 'pointer',
            }}
          />
          <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-dark-text)' }}>
            Code-Mix Normalization / Mitigation
          </span>
          <span className="badge badge-soft" style={{ marginLeft: '4px' }}>
            {mitigationEnabled ? 'Mitigation ON' : 'Mitigation OFF'}
          </span>
        </label>

        {/* Clear Chat Button */}
        {messages.length > 0 && (
          <button onClick={handleClearChat} className="btn btn-secondary" style={{ fontSize: '0.8rem', padding: '6px 12px' }}>
            Clear Chat
          </button>
        )}
      </div>

      {/* Main Conversation Stream */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', minHeight: '360px' }}>
        {messages.length === 0 ? (
          /* Empty Workspace State — No fake data */
          <div
            className="panel"
            style={{
              textAlign: 'center',
              padding: '48px 24px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                backgroundColor: 'var(--color-light-blue)',
                border: '1px solid var(--color-baby-blue)',
                display: 'flex',
                alignItems: 'center',
                justify: 'center',
                marginBottom: '16px',
                color: 'var(--color-dark-text)',
              }}
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--color-dark-text)', marginBottom: '8px' }}>
              Evaluation Chat Workspace
            </h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-muted-text)', maxWidth: '480px', lineHeight: 1.6, marginBottom: '24px' }}>
              Ask a question to test the Cross-Lingual RAG pipeline. Answers are retrieved from the FAISS vector index, generated by the LLM, and evaluated by the LLM Judge in real time.
            </p>

            {/* Prompt Chips */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center', maxWidth: '680px' }}>
              {sampleChips.map((chip, i) => (
                <button
                  key={i}
                  onClick={() => handleChipClick(chip.query)}
                  style={{
                    backgroundColor: 'var(--color-cream)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-pill)',
                    padding: '8px 14px',
                    fontSize: '0.8rem',
                    color: 'var(--color-dark-text)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--color-light-blue)';
                    e.currentTarget.style.borderColor = 'var(--color-baby-blue)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--color-cream)';
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                  }}
                >
                  {chip.label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Active Message Stream */
          messages.map((msg) => (
            <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {/* User Query Entry */}
              <div
                style={{
                  alignSelf: 'flex-end',
                  maxWidth: '85%',
                  backgroundColor: 'var(--color-light-blue)',
                  border: '1px solid var(--color-baby-blue)',
                  borderRadius: '16px 16px 4px 16px',
                  padding: '14px 18px',
                }}
              >
                <div style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--color-muted-text)', marginBottom: '4px' }}>
                  User Query &middot; {msg.timestamp} &middot; {msg.mitigationEnabled ? 'Mitigation Enabled' : 'Mitigation Disabled'}
                </div>
                <div style={{ fontSize: '0.92rem', color: 'var(--color-dark-text)', fontWeight: 500, whiteSpace: 'pre-wrap' }}>
                  {msg.userQuery}
                </div>
              </div>

              {/* Bot Response Entry */}
              <div
                style={{
                  alignSelf: 'flex-start',
                  width: '100%',
                  backgroundColor: 'var(--color-cream)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '16px',
                  padding: '24px',
                  boxShadow: 'var(--shadow-subtle)',
                }}
              >
                {msg.loading ? (
                  /* Loading State */
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--color-muted-text)', fontSize: '0.875rem' }}>
                    <div
                      style={{
                        width: '14px',
                        height: '14px',
                        borderRadius: '50%',
                        border: '2px solid var(--color-baby-blue)',
                        borderTopColor: 'transparent',
                        animation: 'spin 1s linear infinite',
                      }}
                    />
                    <span>Retrieving context, generating answer, and scoring faithfulness…</span>
                  </div>
                ) : msg.error ? (
                  /* Error Alert */
                  <div style={{ color: 'var(--color-danger)', fontSize: '0.875rem', lineHeight: 1.5 }}>
                    <div style={{ fontWeight: 600, marginBottom: '4px' }}>Request Error</div>
                    <div>{msg.error}</div>
                  </div>
                ) : msg.responseData ? (
                  /* Real Response Content */
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {/* Generated Answer */}
                    <div>
                      <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-muted-text)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px' }}>
                        Generated Answer
                      </div>
                      <div style={{ fontSize: '0.92rem', color: 'var(--color-dark-text)', lineHeight: 1.6 }}>
                        <ReactMarkdown>{msg.responseData.answer || ''}</ReactMarkdown>
                      </div>
                    </div>

                    {/* Normalized Query Display (if mitigation actively normalized) */}
                    {msg.responseData.normalized_query && msg.responseData.mitigation_applied && (
                      <div style={{ backgroundColor: 'var(--color-warm-cream)', border: '1px solid var(--color-border)', borderRadius: '10px', padding: '12px 14px' }}>
                        <div style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--color-muted-text)', marginBottom: '4px' }}>
                          Normalized Query (Used for FAISS Vector Retrieval)
                        </div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--color-dark-text)', fontFamily: 'var(--font-sans)' }}>
                          {msg.responseData.normalized_query}
                        </div>
                      </div>
                    )}

                    {/* Research Evaluation Metrics Panel */}
                    <div
                      style={{
                        backgroundColor: 'var(--color-warm-cream)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '12px',
                        padding: '16px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '12px',
                      }}
                    >
                      <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-dark-text)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        LLM-as-a-Judge Evaluation Metrics
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px' }}>
                        {/* Faithfulness Score */}
                        <div style={{ backgroundColor: 'var(--color-cream)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Faithfulness Score</div>
                          <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-dark-text)', marginTop: '2px' }}>
                            {msg.responseData.faithfulness_score !== null && msg.responseData.faithfulness_score !== undefined
                              ? Number(msg.responseData.faithfulness_score).toFixed(3)
                              : 'N/A'}
                          </div>
                        </div>

                        {/* Hallucination Flag */}
                        <div style={{ backgroundColor: 'var(--color-cream)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Hallucination Status</div>
                          <div style={{ marginTop: '4px' }}>
                            {msg.responseData.hallucination_flag === true ? (
                              <span className="badge" style={{ backgroundColor: '#FDF0F0', color: 'var(--color-danger)', border: '1px solid #F5C6C6' }}>
                                FAIL (Flagged)
                              </span>
                            ) : msg.responseData.hallucination_flag === false ? (
                              <span className="badge badge-success">
                                PASS (Faithful)
                              </span>
                            ) : (
                              <span style={{ fontSize: '0.85rem', color: 'var(--color-muted-text)' }}>N/A</span>
                            )}
                          </div>
                        </div>

                        {/* Code-Mix Status */}
                        <div style={{ backgroundColor: 'var(--color-cream)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Code-Mix Detection</div>
                          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-dark-text)', marginTop: '4px' }}>
                            {msg.responseData.code_mix_detected
                              ? `Yes (${(msg.responseData.detected_languages || []).join(', ')})`
                              : 'No'}
                          </div>
                        </div>

                        {/* Mitigation Applied */}
                        <div style={{ backgroundColor: 'var(--color-cream)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Mitigation Status</div>
                          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-dark-text)', marginTop: '4px' }}>
                            {msg.responseData.mitigation_applied
                              ? 'Applied'
                              : msg.responseData.mitigation_enabled
                              ? 'Enabled (Raw Query Used)'
                              : 'Disabled'}
                          </div>
                        </div>

                        {/* Pipeline Latency */}
                        <div style={{ backgroundColor: 'var(--color-cream)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Latency</div>
                          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-dark-text)', marginTop: '4px' }}>
                            {msg.responseData.latency ? `${msg.responseData.latency}s` : 'N/A'}
                          </div>
                        </div>
                      </div>

                      {/* Judge Explanation */}
                      {msg.responseData.faithfulness_explanation && (
                        <div style={{ backgroundColor: 'var(--color-cream)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '12px' }}>
                          <div style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--color-muted-text)', marginBottom: '4px' }}>
                            Judge Explanation
                          </div>
                          <div style={{ fontSize: '0.82rem', color: 'var(--color-dark-text)', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
                            {msg.responseData.faithfulness_explanation}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Retrieved Sources Accordion */}
                    {msg.responseData.retrieved_documents && msg.responseData.retrieved_documents.length > 0 && (
                      <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '16px' }}>
                        <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--color-dark-text)', marginBottom: '10px' }}>
                          Retrieved Sources ({msg.responseData.retrieved_documents.length} Chunks)
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          {msg.responseData.retrieved_documents.map((doc, idx) => {
                            const isExpanded = expandedSources[`${msg.id}-${idx}`] ?? false;
                            return (
                              <div
                                key={idx}
                                style={{
                                  border: '1px solid var(--color-border)',
                                  borderRadius: '8px',
                                  overflow: 'hidden',
                                  backgroundColor: 'var(--color-cream)',
                                }}
                              >
                                <button
                                  type="button"
                                  onClick={() => toggleSourceExpand(msg.id, idx)}
                                  style={{
                                    width: '100%',
                                    padding: '10px 14px',
                                    backgroundColor: 'var(--color-warm-cream)',
                                    border: 'none',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justify: 'space-between',
                                    fontSize: '0.82rem',
                                    fontWeight: 500,
                                    color: 'var(--color-dark-text)',
                                    textAlign: 'left',
                                  }}
                                >
                                  <span style={{ fontWeight: 600 }}>Source {idx + 1}: Doc {doc.document_id || 'N/A'}</span>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                    <span style={{ color: 'var(--color-primary)', fontWeight: 600, fontSize: '0.78rem' }}>
                                      Score: {(doc.score || 0).toFixed(3)}
                                    </span>
                                    <span style={{ fontSize: '0.75rem', color: 'var(--color-muted-text)' }}>
                                      {isExpanded ? '▲ Hide' : '▼ View'}
                                    </span>
                                  </div>
                                </button>

                                {isExpanded && (
                                  <div style={{ padding: '12px 14px', borderTop: '1px solid var(--color-border)', fontSize: '0.82rem' }}>
                                    <div style={{ fontSize: '0.72rem', color: 'var(--color-muted-text)', marginBottom: '6px' }}>
                                      Chunk ID: {doc.chunk_id}
                                    </div>
                                    <div style={{ color: 'var(--color-dark-text)', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
                                      {doc.text}
                                    </div>
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Model Provenance Footer */}
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-muted-text)', borderTop: '1px solid var(--color-border)', paddingTop: '10px', display: 'flex', gap: '16px' }}>
                      <span>Generator: <strong>{msg.responseData.generator_model || 'Unknown'}</strong></span>
                      <span>Judge: <strong>{msg.responseData.judge_model || 'Unknown'}</strong></span>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Query Input Area */}
      <form onSubmit={handleSubmit} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {validationError && (
          <div style={{ fontSize: '0.8rem', color: 'var(--color-danger)', fontWeight: 500 }}>
            {validationError}
          </div>
        )}

        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
          <textarea
            ref={textareaRef}
            rows={1}
            value={query}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Type your question... (e.g. English, Tamil-English, or Hindi-English). Press Enter to send."
            disabled={loading}
            style={{
              flex: 1,
              padding: '12px 14px',
              borderRadius: 'var(--radius-input)',
              border: '1px solid var(--color-border)',
              backgroundColor: 'var(--color-warm-cream)',
              color: 'var(--color-dark-text)',
              fontSize: '0.9rem',
              resize: 'none',
              outline: 'none',
              lineHeight: 1.5,
            }}
          />

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{
              padding: '12px 20px',
              minWidth: '100px',
              height: '46px',
            }}
          >
            {loading ? 'Evaluating…' : 'Send'}
          </button>
        </div>
      </form>

      {/* Inline Animation keyframes for loading spinner */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
