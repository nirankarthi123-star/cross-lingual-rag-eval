import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { getHealth } from '../services/api';

const ChatIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
  </svg>
);

const DocsIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
  </svg>
);

const DashboardIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10"></line>
    <line x1="12" y1="20" x2="12" y2="4"></line>
    <line x1="6" y1="20" x2="6" y2="14"></line>
  </svg>
);

export default function Sidebar() {
  const [backendStatus, setBackendStatus] = useState('checking'); // 'checking' | 'online' | 'offline'

  useEffect(() => {
    let isMounted = true;

    async function checkBackendHealth() {
      try {
        const res = await getHealth();
        if (isMounted) {
          if (res && res.status === 'ok') {
            setBackendStatus('online');
          } else {
            setBackendStatus('offline');
          }
        }
      } catch (err) {
        if (isMounted) {
          setBackendStatus('offline');
        }
      }
    }

    checkBackendHealth();

    // Periodic check every 15 seconds
    const interval = setInterval(checkBackendHealth, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const navItems = [
    { path: '/', label: 'RAG Chat', icon: <ChatIcon /> },
    { path: '/documents', label: 'Documents', icon: <DocsIcon /> },
    { path: '/dashboard', label: 'Evaluation Dashboard', icon: <DashboardIcon /> },
  ];

  const getStatusColor = () => {
    if (backendStatus === 'online') return 'var(--color-success)';
    if (backendStatus === 'offline') return 'var(--color-danger)';
    return 'var(--color-warning)';
  };

  const getStatusText = () => {
    if (backendStatus === 'online') return 'Backend Online';
    if (backendStatus === 'offline') return 'Backend Offline';
    return 'Checking…';
  };

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        backgroundColor: 'var(--color-warm-cream)',
        borderRight: '1px solid var(--color-border)',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'sticky',
        top: 0,
        flexShrink: 0,
        userSelect: 'none',
      }}
    >
      {/* Brand Identity — Aligned Grid */}
      <div
        style={{
          padding: '24px 20px 16px 20px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              backgroundColor: 'var(--color-baby-blue)',
              display: 'flex',
              alignItems: 'center',
              justify: 'center',
              color: 'var(--color-dark-text)',
              fontWeight: 600,
              fontSize: '0.85rem',
            }}
          >
            CR
          </div>
          <div>
            <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--color-dark-text)', lineHeight: 1.25 }}>
              Cross-Lingual RAG
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-muted-text)', marginTop: '2px', fontWeight: 400 }}>
              Research Workspace
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Menu — Consistent 20px Left Grid */}
      <nav style={{ padding: '16px 12px', flex: 1 }}>
        <div style={{ fontSize: '0.68rem', fontWeight: 600, color: 'var(--color-muted-text)', letterSpacing: '0.04em', padding: '0 8px 10px 8px' }}>
          Navigation
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '10px 12px',
                borderRadius: 'var(--radius-card)',
                fontSize: '0.875rem',
                fontWeight: isActive ? 600 : 500,
                color: isActive ? 'var(--color-dark-text)' : 'var(--color-muted-text)',
                backgroundColor: isActive ? 'var(--color-light-blue)' : 'transparent',
                border: isActive ? '1px solid var(--color-baby-blue)' : '1px solid transparent',
                transition: 'all 0.15s ease',
              })}
            >
              <span style={{ display: 'flex', alignItems: 'center', opacity: 0.85 }}>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Backend Status Footer — Dynamic Connection Indicator */}
      <div
        style={{
          padding: '16px 20px',
          borderTop: '1px solid var(--color-border)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: getStatusColor(),
              display: 'inline-block',
              transition: 'background-color 0.3s ease',
            }}
          />
          <span style={{ color: 'var(--color-dark-text)', fontWeight: 500, fontSize: '0.78rem' }}>
            {getStatusText()}
          </span>
        </div>
      </div>
    </aside>
  );
}
