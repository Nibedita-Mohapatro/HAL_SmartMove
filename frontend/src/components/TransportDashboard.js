import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import GPSTracker from './GPSTracker';

const TransportDashboard = () => {
  const [user, setUser] = useState(null);
  const [assignedTrips, setAssignedTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showGPSTracker, setShowGPSTracker] = useState(false);
  const [selectedTripId, setSelectedTripId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (!token || !userData) {
      navigate('/login');
      return;
    }

    const parsedUser = JSON.parse(userData);
    if (parsedUser.role !== 'transport') {
      navigate('/login');
      return;
    }

    setUser(parsedUser);
    fetchAssignedTrips();
  }, [navigate]);

  const fetchAssignedTrips = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/transport/assigned-trips', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setAssignedTrips(data.assigned_trips || []);
      } else {
        setError('Failed to fetch assigned trips');
      }
    } catch (err) {
      setError('Error fetching assigned trips');
    } finally {
      setLoading(false);
    }
  };

  const startTrip = async (tripId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/transport/trips/${tripId}/start`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        fetchAssignedTrips(); // Refresh trips
      } else {
        setError('Failed to start trip');
      }
    } catch (err) {
      setError('Error starting trip');
    }
  };

  const completeTrip = async (tripId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/transport/trips/${tripId}/complete`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          notes: 'Trip completed successfully',
          final_odometer: Math.floor(Math.random() * 1000) + 5000
        })
      });

      if (response.ok) {
        fetchAssignedTrips(); // Refresh trips
      } else {
        setError('Failed to complete trip');
      }
    } catch (err) {
      setError('Error completing trip');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const openGPSTracker = (tripId) => {
    setSelectedTripId(tripId);
    setShowGPSTracker(true);
  };

  const closeGPSTracker = () => {
    setShowGPSTracker(false);
    setSelectedTripId(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-hal-blue mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading assigned trips...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <img className="h-8 w-8" src="/hal-logo.png" alt="HAL" />
              </div>
              <div className="ml-4">
                <h1 className="text-2xl font-bold text-gray-900">Transport Dashboard</h1>
                <p className="text-sm text-gray-500">Welcome, {user?.first_name} {user?.last_name}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Driver Info Card */}
        <div className="bg-white overflow-hidden shadow rounded-lg mb-6">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Driver Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-500">License Number</p>
                <p className="text-sm text-gray-900">{user?.license_number || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Rating</p>
                <p className="text-sm text-gray-900">{user?.rating || 'N/A'} ⭐</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Status</p>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  user?.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {user?.status || 'Unknown'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Assigned Trips */}
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Assigned Trips</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Your current and upcoming trip assignments
            </p>
          </div>
          
          {assignedTrips.length === 0 ? (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No assigned trips</h3>
              <p className="mt-1 text-sm text-gray-500">You don't have any trips assigned at the moment.</p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {assignedTrips.map((trip) => (
                <li key={trip.id} className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-hal-blue truncate">
                          Trip #{trip.id} - {trip.user_name}
                        </p>
                        <div className="ml-2 flex-shrink-0 flex">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            trip.status === 'approved' ? 'bg-yellow-100 text-yellow-800' :
                            trip.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {trip.status.replace('_', ' ')}
                          </span>
                        </div>
                      </div>
                      <div className="mt-2">
                        <div className="sm:flex">
                          <div className="sm:flex-1">
                            <p className="text-sm text-gray-900">
                              <strong>Route:</strong> {trip.origin} → {trip.destination}
                            </p>
                            <p className="text-sm text-gray-500">
                              <strong>Date:</strong> {trip.request_date} at {trip.request_time}
                            </p>
                            <p className="text-sm text-gray-500">
                              <strong>Passengers:</strong> {trip.passenger_count}
                            </p>
                          </div>
                          {trip.assigned_vehicle && (
                            <div className="mt-2 sm:mt-0 sm:ml-6">
                              <p className="text-sm text-gray-900">
                                <strong>Vehicle:</strong> {trip.assigned_vehicle.make} {trip.assigned_vehicle.model}
                              </p>
                              <p className="text-sm text-gray-500">
                                {trip.assigned_vehicle.registration_number}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="ml-4 flex-shrink-0 flex flex-wrap gap-2">
                      {trip.driver_can_start && (
                        <button
                          onClick={() => startTrip(trip.id)}
                          className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm font-medium"
                        >
                          Start Trip
                        </button>
                      )}
                      {trip.driver_can_complete && (
                        <button
                          onClick={() => completeTrip(trip.id)}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm font-medium"
                        >
                          Complete Trip
                        </button>
                      )}
                      {(trip.status === 'approved' || trip.status === 'in_progress') && (
                        <button
                          onClick={() => openGPSTracker(trip.id)}
                          className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm font-medium"
                        >
                          🛰️ GPS Track
                        </button>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>

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

export default TransportDashboard;
