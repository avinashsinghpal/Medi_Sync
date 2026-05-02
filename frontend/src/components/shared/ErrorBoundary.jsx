import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', textAlign: 'center', backgroundColor: '#fef2f2', borderRadius: '0.5rem', margin: '2rem', border: '1px solid #ef4444' }}>
          <h2 style={{ color: '#ef4444', marginBottom: '1rem' }}>Something went wrong.</h2>
          <p style={{ color: '#7f1d1d' }}>{this.state.error?.message || 'An unexpected error occurred.'}</p>
          <button 
            onClick={() => window.location.reload()}
            style={{ marginTop: '1rem', padding: '0.5rem 1rem', backgroundColor: '#ef4444', color: 'white', borderRadius: '0.375rem', cursor: 'pointer' }}
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
