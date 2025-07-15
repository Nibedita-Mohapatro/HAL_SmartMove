import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SimpleLogin = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    employee_id: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        // Store tokens in localStorage
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Redirect based on user role
        if (data.user.role === 'admin' || data.user.role === 'super_admin') {
          window.location.href = '/admin';
        } else {
          navigate('/employee');
        }
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please check if the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f9fafb' }}>
      <div style={{ maxWidth: '400px', width: '100%', padding: '2rem' }}>
        <div className="card">
          <div className="text-center mb-4">
            <div style={{ 
              width: '48px', 
              height: '48px', 
              background: '#1e40af', 
              borderRadius: '50%', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              margin: '0 auto 1rem auto'
            }}>
              <span style={{ color: 'white', fontSize: '1.5rem' }}>🔐</span>
            </div>
            <h2 style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
              Sign in to HAL Transport
            </h2>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
              Access your transport management dashboard
            </p>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="employee_id" className="form-label">
                Employee ID
              </label>
              <input
                type="text"
                name="employee_id"
                id="employee_id"
                required
                value={formData.employee_id}
                onChange={handleChange}
                className="form-input"
                placeholder="Employee ID"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <input
                type="password"
                name="password"
                id="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="form-input"
                placeholder="Password"
              />
            </div>

            {error && (
              <div style={{ 
                background: '#fef2f2', 
                border: '1px solid #fecaca', 
                borderRadius: '0.375rem', 
                padding: '0.75rem', 
                marginBottom: '1rem' 
              }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <span style={{ color: '#dc2626', marginRight: '0.5rem' }}>⚠️</span>
                  <span style={{ color: '#dc2626', fontSize: '0.875rem' }}>{error}</span>
                </div>
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary"
                style={{ 
                  width: '100%', 
                  padding: '0.75rem',
                  opacity: loading ? 0.5 : 1,
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>

            <div className="text-center mt-4">
              <button
                type="button"
                onClick={() => navigate('/')}
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  color: '#1e40af', 
                  textDecoration: 'underline',
                  cursor: 'pointer'
                }}
              >
                ← Back to Home
              </button>
            </div>
          </form>

          {/* Demo Credentials */}
          <div style={{ 
            marginTop: '1.5rem', 
            padding: '1rem', 
            background: '#eff6ff', 
            borderRadius: '0.375rem' 
          }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#1e40af', marginBottom: '0.5rem' }}>
              Demo Credentials:
            </h3>
            <div style={{ fontSize: '0.75rem', color: '#1e40af', lineHeight: '1.4' }}>
              <div><strong>Super Admin:</strong> HAL001 / admin123</div>
              <div><strong>Transport Admin:</strong> HAL002 / transport123</div>
              <div><strong>Employee:</strong> HAL003 / employee123</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleLogin;
