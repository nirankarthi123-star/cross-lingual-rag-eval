import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

export default function Layout() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--color-warm-cream)' }}>
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Workspace Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <Header />

        <main
          style={{
            flex: 1,
            padding: '20px 32px 36px 32px',
            maxWidth: '1080px',
            width: '100%',
            margin: '0 auto',
          }}
        >
          <Outlet />
        </main>
      </div>
    </div>
  );
}
