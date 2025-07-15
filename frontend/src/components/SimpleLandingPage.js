import React from 'react';
import { Link } from 'react-router-dom';

const SimpleLandingPage = () => {
  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)' }}>
      {/* Navigation */}
      <nav style={{ background: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <div className="container">
          <div className="flex justify-between items-center" style={{ height: '64px' }}>
            <div className="flex items-center">
              <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1e3a8a' }}>HAL Transport</h1>
              <span style={{ marginLeft: '1rem', color: '#6b7280', fontSize: '0.875rem' }}>Management System</span>
            </div>
            <div>
              <Link
                to="/login"
                className="btn btn-primary"
                style={{ textDecoration: 'none' }}
              >
                Login
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div style={{ padding: '4rem 0', textAlign: 'center' }}>
        <div className="container">
          <h1 style={{ 
            fontSize: '3rem', 
            fontWeight: '800', 
            color: 'white',
            marginBottom: '1rem',
            lineHeight: '1.1'
          }}>
            Smart Vehicle Transport System
          </h1>
          <h2 style={{ 
            fontSize: '1.5rem', 
            color: '#ea580c',
            marginBottom: '2rem'
          }}>
            Hindustan Aeronautics Limited
          </h2>
          <p style={{ 
            fontSize: '1.125rem', 
            color: '#e5e7eb',
            maxWidth: '600px',
            margin: '0 auto 2rem auto',
            lineHeight: '1.6'
          }}>
            Streamline your transportation needs with HAL's intelligent vehicle management system. 
            Request vehicles, track status, and optimize routes with AI-powered insights.
          </p>
          <div style={{ marginTop: '2rem' }}>
            <Link
              to="/login"
              className="btn btn-orange"
              style={{ 
                textDecoration: 'none',
                padding: '1rem 2rem',
                fontSize: '1.125rem',
                display: 'inline-block',
                marginRight: '1rem'
              }}
            >
              Get Started
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
              style={{ 
                textDecoration: 'none',
                padding: '1rem 2rem',
                fontSize: '1.125rem',
                display: 'inline-block'
              }}
            >
              View API Docs
            </a>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div style={{ background: 'white', padding: '3rem 0' }}>
        <div className="container">
          <div className="text-center mb-4">
            <h2 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#111827', marginBottom: '1rem' }}>
              System Features
            </h2>
          </div>
          
          <div className="grid grid-cols-2 gap-4" style={{ marginTop: '2rem' }}>
            <div className="card">
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1e40af', marginBottom: '0.5rem' }}>
                🚗 Easy Request Management
              </h3>
              <p style={{ color: '#6b7280' }}>
                Submit transport requests with just a few clicks. Track status and get real-time updates.
              </p>
            </div>

            <div className="card">
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1e40af', marginBottom: '0.5rem' }}>
                🤖 AI-Powered Analytics
              </h3>
              <p style={{ color: '#6b7280' }}>
                Machine learning algorithms optimize routes, predict demand, and improve efficiency.
              </p>
            </div>

            <div className="card">
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1e40af', marginBottom: '0.5rem' }}>
                👨‍💼 Admin Dashboard
              </h3>
              <p style={{ color: '#6b7280' }}>
                Comprehensive admin panel for managing vehicles, drivers, and transport requests.
              </p>
            </div>

            <div className="card">
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1e40af', marginBottom: '0.5rem' }}>
                📊 Real-time Tracking
              </h3>
              <p style={{ color: '#6b7280' }}>
                Track vehicle locations, monitor trip progress, and get instant notifications.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Demo Credentials */}
      <div style={{ background: '#f3f4f6', padding: '2rem 0' }}>
        <div className="container">
          <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1e40af', marginBottom: '1rem', textAlign: 'center' }}>
              🔑 Demo Credentials
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <div>
                <strong style={{ color: '#ea580c' }}>Super Admin:</strong><br />
                HAL001 / admin123
              </div>
              <div>
                <strong style={{ color: '#ea580c' }}>Transport Admin:</strong><br />
                HAL002 / transport123
              </div>
              <div>
                <strong style={{ color: '#ea580c' }}>Employee:</strong><br />
                HAL003 / employee123
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer style={{ background: '#1e3a8a', color: 'white', padding: '2rem 0', textAlign: 'center' }}>
        <div className="container">
          <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
            HAL Transport Management System
          </h3>
          <p style={{ color: '#9ca3af' }}>
            Hindustan Aeronautics Limited - Powering India's Aerospace Dreams
          </p>
          <p style={{ marginTop: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
            © 2024 Hindustan Aeronautics Limited. All rights reserved.
          </p>
          <div style={{ marginTop: '1rem' }}>
            <a 
              href="http://localhost:8000" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: '#ea580c', textDecoration: 'none', marginRight: '1rem' }}
            >
              Backend API
            </a>
            <a 
              href="http://localhost:8000/docs" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: '#ea580c', textDecoration: 'none' }}
            >
              API Documentation
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default SimpleLandingPage;
