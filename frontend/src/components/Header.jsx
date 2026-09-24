import React from 'react';
import { useLocation } from 'react-router-dom';

const routeInfo = {
  '/': {
    title: 'RAG Chat',
    description: 'Test multilingual and code-mixed queries against the retrieval pipeline.',
  },
  '/documents': {
    title: 'Documents',
    description: 'Manage the evaluation corpus and FAISS vector index.',
  },
  '/dashboard': {
    title: 'Evaluation Dashboard',
    description: 'Analyze retrieval, faithfulness, hallucination, and experiment results.',
  },
};

export default function Header() {
  const location = useLocation();
  const currentInfo = routeInfo[location.pathname] || {
    title: 'RAG Evaluation',
    description: 'Multilingual & Code-Mixed RAG Research Workspace',
  };

  return (
    <header
      style={{
        height: 'var(--header-height)',
        backgroundColor: 'transparent',
        display: 'flex',
        alignItems: 'center',
        justify: 'space-between',
        padding: '0 32px',
        flexShrink: 0,
      }}
    >
      <div>
        <h1 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--color-dark-text)', letterSpacing: '-0.01em', lineHeight: 1.25 }}>
          {currentInfo.title}
        </h1>
        <p style={{ fontSize: '0.82rem', color: 'var(--color-muted-text)', marginTop: '2px', fontWeight: 400 }}>
          {currentInfo.description}
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center' }}>
        <span className="badge badge-soft">
          Local Workspace
        </span>
      </div>
    </header>
  );
}
