import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import GPSTracker from './GPSTracker';

const EmployeeDashboard = () => {
  const [user, setUser] = useState(null);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showGPSTracker, setShowGPSTracker] = useState(false);
  const [selectedTripId, setSelectedTripId] = useState(null);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    approved: 0,
    completed: 0
  });

  useEffect(() => {
    // Get user from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }

    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No token found');
        setLoading(false);
        return;
      }

      console.log('Fetching requests with token:', token.substring(0, 20) + '...');

      const response = await fetch('http://localhost:8000/api/v1/requests/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      console.log('Response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('Received data:', data);
        setRequests(data.requests || []);

        // Calculate stats
        const requestList = data.requests || [];
        const stats = requestList.reduce((acc, req) => {
          acc.total++;
          if (acc[req.status] !== undefined) {
            acc[req.status]++;
          }
          return acc;
        }, { total: 0, pending: 0, approved: 0, completed: 0, rejected: 0, cancelled: 0 });

        setStats(stats);
      } else {
        console.error('Failed to fetch requests:', response.status, await response.text());
      }
    } catch (error) {
      console.error('Error fetching requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      completed: 'bg-blue-100 text-blue-800',
      cancelled: 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const openGPSTracker = (tripId) => {
    setSelectedTripId(tripId);
    setShowGPSTracker(true);
  };

  const closeGPSTracker = () => {
    setShowGPSTracker(false);
    setSelectedTripId(null);
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'text-green-600',
      medium: 'text-yellow-600',
      high: 'text-orange-600',
      urgent: 'text-red-600'
    };
    return colors[priority] || 'text-gray-600';
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-hal-blue"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-hal-navy">HAL Transport</h1>
              <span className="ml-4 text-sm text-gray-500">Employee Portal</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user?.first_name} {user?.last_name}
              </span>
              <button
                onClick={handleLogout}
                className="bg-hal-blue hover:bg-hal-navy text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold">{stats.total}</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Requests</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.total}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold">{stats.pending || 0}</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Pending</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.pending || 0}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold">{stats.approved || 0}</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Approved</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.approved || 0}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold">{stats.completed || 0}</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Completed</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.completed || 0}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="mb-6">
          <Link
            to="/employee/request"
            className="bg-hal-orange hover:bg-orange-600 text-white px-6 py-3 rounded-md font-medium inline-flex items-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            New Transport Request
          </Link>
        </div>

        {/* Recent Requests */}
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Requests</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">Your latest transport requests</p>
          </div>
          <ul className="divide-y divide-gray-200">
            {requests.length === 0 ? (
              <li className="px-4 py-4 text-center text-gray-500">
                No requests found. <Link to="/employee/request" className="text-hal-blue hover:underline">Create your first request</Link>
              </li>
            ) : (
              requests.slice(0, 10).map((request) => (
                <li key={request.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(request.status)}`}>
                            {request.status}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {request.origin} → {request.destination}
                          </div>
                          <div className="text-sm text-gray-500">
                            {request.request_date} at {request.request_time} • {request.passenger_count} passenger(s)
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm font-medium ${getPriorityColor(request.priority)}`}>
                          {request.priority}
                        </span>
                        {(request.status === 'approved' || request.status === 'in_progress') && (
                          <button
                            onClick={() => openGPSTracker(request.id)}
                            className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm font-medium"
                          >
                            🛰️ Track
                          </button>
                        )}
                        <Link
                          to={`/employee/request/${request.id}`}
                          className="text-hal-blue hover:text-hal-navy text-sm font-medium"
                        >
                          View Details
                        </Link>
                      </div>
                    </div>
                    {request.purpose && (
                      <div className="mt-2 text-sm text-gray-600">
                        Purpose: {request.purpose}
                      </div>
                    )}
                    {request.vehicle_assignment && (
                      <div className="mt-2 text-sm text-green-600">
                        Assigned: {request.vehicle_assignment.vehicle.vehicle_number} with {request.vehicle_assignment.driver.first_name} {request.vehicle_assignment.driver.last_name}
                      </div>
                    )}
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      </div>

      {/* GPS Tracker Modal */}
      {showGPSTracker && selectedTripId && (
        <GPSTracker
          tripId={selectedTripId}
          userRole={user?.role}
          onClose={closeGPSTracker}
        />
      )}
    </div>
  );
};

export default EmployeeDashboard;
