import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import UserManagement from './UserManagement';
import RequestManagement from './RequestManagement';
import VehicleManagement from './VehicleManagement';
import DriverManagement from './DriverManagement';
import AnalyticsDashboard from './AnalyticsDashboard';
import GPSTracker from './GPSTracker';

const AdminDashboard = () => {
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState({
    total_requests: 0,
    pending_requests: 0,
    approved_requests: 0,
    total_vehicles: 0,
    available_vehicles: 0,
    total_drivers: 0,
    active_drivers: 0
  });
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [assignmentOptions, setAssignmentOptions] = useState(null);
  const [selectedVehicle, setSelectedVehicle] = useState('');
  const [selectedDriver, setSelectedDriver] = useState('');
  const [safetyOverride, setSafetyOverride] = useState(false);
  const [showGPSTracker, setShowGPSTracker] = useState(false);
  const [selectedTripId, setSelectedTripId] = useState(null);

  // Get current user role
  const getCurrentUserRole = () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      return user.role;
    }
    return null;
  };

  const userRole = getCurrentUserRole();

  useEffect(() => {
    // Get user from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }

    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No access token found');
        setLoading(false);
        return;
      }

      // Fetch admin dashboard stats
      const statsResponse = await fetch('http://localhost:8000/api/v1/admin/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        // Map the API response to our expected format
        setStats({
          total_requests: statsData.summary.total_requests_today,
          pending_requests: statsData.summary.pending_requests,
          approved_requests: statsData.summary.approved_requests,
          total_vehicles: statsData.summary.active_vehicles,
          available_vehicles: statsData.summary.active_vehicles,
          total_drivers: statsData.summary.available_drivers,
          active_drivers: statsData.summary.available_drivers
        });
      }

      // Fetch all requests for admin
      const requestsResponse = await fetch('http://localhost:8000/api/v1/admin/requests', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (requestsResponse.ok) {
        const requestsData = await requestsResponse.json();
        setRequests(requestsData.requests || []);
      }

    } catch (error) {
      console.error('Error fetching admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/';
  };

  const openApprovalModal = async (request) => {
    setSelectedRequest(request);
    setSelectedVehicle('');
    setSelectedDriver('');
    setSafetyOverride(false);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/admin/requests/${request.id}/assignment-options`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAssignmentOptions(data);
        setShowApprovalModal(true);
      } else {
        const errorData = await response.json();
        console.error('Failed to fetch assignment options:', errorData);
        alert(errorData.detail || 'Failed to load assignment options. Please try again.');
      }
    } catch (error) {
      console.error('Error fetching assignment options:', error);
    }
  };

  const approveRequestWithAssignment = async () => {
    if (!selectedVehicle || !selectedDriver) {
      alert('Please select both vehicle and driver');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/admin/requests/${selectedRequest.id}/approve-with-assignment`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          vehicle_id: parseInt(selectedVehicle),
          driver_id: parseInt(selectedDriver),
          estimated_departure: "08:00:00",
          estimated_arrival: "09:00:00",
          notes: "Approved via admin dashboard"
        })
      });

      if (response.ok) {
        const data = await response.json();
        alert(data.message || 'Request approved and assigned successfully');
        setShowApprovalModal(false);
        setSafetyOverride(false); // Reset override flag
        fetchAdminData(); // Refresh data
      } else {
        const errorData = await response.json();
        if (Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map(err => err.msg || err.message || 'Validation error').join(', ');
          alert(errorMessages);
        } else {
          alert(errorData.detail || 'Approval failed');
        }
        setSafetyOverride(false); // Reset override flag on failure
      }
    } catch (error) {
      console.error('Error approving request:', error);
    }
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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading admin dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-hal-navy">
                HAL Admin Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">
                Welcome, {user?.first_name} {user?.last_name}
              </span>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Tab Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'dashboard'
                  ? 'border-hal-blue text-hal-blue'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab('requests')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'requests'
                  ? 'border-hal-blue text-hal-blue'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Transport Requests
            </button>
            {(user?.role === 'admin' || user?.role === 'super_admin') && (
              <button
                onClick={() => setActiveTab('users')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'users'
                    ? 'border-hal-blue text-hal-blue'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                User Management
              </button>
            )}
            <button
              onClick={() => setActiveTab('vehicles')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'vehicles'
                  ? 'border-hal-blue text-hal-blue'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Vehicles
            </button>
            <button
              onClick={() => setActiveTab('drivers')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'drivers'
                  ? 'border-hal-blue text-hal-blue'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Drivers
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'analytics'
                  ? 'border-hal-blue text-hal-blue'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Analytics
            </button>
          </nav>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Tab Content */}
        {activeTab === 'dashboard' && (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-sm font-bold">📋</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Requests</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.total_requests}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-sm font-bold">⏳</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Pending Requests</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.pending_requests}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-sm font-bold">🚗</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Available Vehicles</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.available_vehicles}/{stats.total_vehicles}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-sm font-bold">👨‍💼</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Active Drivers</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.active_drivers}/{stats.total_drivers}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Requests */}
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Transport Requests</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Latest transport requests requiring admin attention
            </p>
          </div>
          <ul className="divide-y divide-gray-200">
            {requests.slice(0, 10).map((request) => (
              <li key={request.id}>
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          request.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          request.status === 'approved' ? 'bg-green-100 text-green-800' :
                          request.status === 'rejected' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {request.status}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {request.origin} → {request.destination}
                        </div>
                        <div className="text-sm text-gray-500">
                          {request.request_date} at {request.request_time} • {request.passenger_count} passengers
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {(request.status === 'approved' || request.status === 'in_progress') && (
                        <button
                          onClick={() => openGPSTracker(request.id)}
                          className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm"
                        >
                          🛰️ Track GPS
                        </button>
                      )}
                      <span className="text-sm text-gray-500">
                        Priority: {request.priority}
                      </span>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>


          </>
        )}

        {/* User Management Tab - Admin Only */}
        {activeTab === 'users' && (user?.role === 'admin' || user?.role === 'super_admin') && (
          <UserManagement />
        )}

        {/* Transport Requests Tab */}
        {activeTab === 'requests' && (
          <RequestManagement />
        )}

        {/* Vehicles Tab */}
        {activeTab === 'vehicles' && (
          <VehicleManagement />
        )}

        {/* Drivers Tab */}
        {activeTab === 'drivers' && (
          <DriverManagement />
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <AnalyticsDashboard />
        )}
      </div>

      {/* Approval Modal */}
      {showApprovalModal && selectedRequest && assignmentOptions && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Approve Request #{selectedRequest.id} - {selectedRequest.user_name}
              </h3>

              <div className="mb-4 p-3 bg-gray-50 rounded">
                <p><strong>Route:</strong> {selectedRequest.origin} → {selectedRequest.destination}</p>
                <p><strong>Date:</strong> {selectedRequest.request_date} at {selectedRequest.request_time}</p>
                <p><strong>Passengers:</strong> {selectedRequest.passenger_count}</p>
                <p><strong>Purpose:</strong> {selectedRequest.purpose}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                {/* Vehicle Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Vehicle
                  </label>
                  <select
                    value={selectedVehicle}
                    onChange={(e) => setSelectedVehicle(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Choose a vehicle...</option>
                    {assignmentOptions.available_vehicles?.map((vehicle) => (
                      <option key={vehicle.id} value={vehicle.id}>
                        {vehicle.make} {vehicle.model} ({vehicle.registration_number})
                        {vehicle.safety_validation && !vehicle.safety_validation.is_safe && ' ⚠️ SAFETY ISSUES'}
                      </option>
                    ))}
                  </select>

                  {selectedVehicle && assignmentOptions.available_vehicles?.find(v => v.id == selectedVehicle)?.safety_validation && (
                    <div className="mt-2 text-sm">
                      {assignmentOptions.available_vehicles?.find(v => v.id == selectedVehicle)?.safety_validation?.issues?.length > 0 && (
                        <div className="text-red-600">
                          <strong>Issues:</strong>
                          <ul className="list-disc list-inside">
                            {assignmentOptions.available_vehicles?.find(v => v.id == selectedVehicle)?.safety_validation?.issues?.map((issue, idx) => (
                              <li key={idx}>{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {assignmentOptions.available_vehicles?.find(v => v.id == selectedVehicle)?.safety_validation?.warnings?.length > 0 && (
                        <div className="text-yellow-600">
                          <strong>Warnings:</strong>
                          <ul className="list-disc list-inside">
                            {assignmentOptions.available_vehicles?.find(v => v.id == selectedVehicle)?.safety_validation?.warnings?.map((warning, idx) => (
                              <li key={idx}>{warning}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Driver Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Driver
                  </label>
                  <select
                    value={selectedDriver}
                    onChange={(e) => setSelectedDriver(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Choose a driver...</option>
                    {assignmentOptions.available_drivers?.map((driver) => (
                      <option key={driver.id} value={driver.id}>
                        {driver.first_name} {driver.last_name} (Rating: {driver.rating || 'N/A'})
                        {driver.safety_validation && !driver.safety_validation.is_safe && ' ⚠️ SAFETY ISSUES'}
                      </option>
                    ))}
                  </select>

                  {selectedDriver && assignmentOptions.available_drivers?.find(d => d.id == selectedDriver)?.safety_validation && (
                    <div className="mt-2 text-sm">
                      {assignmentOptions.available_drivers?.find(d => d.id == selectedDriver)?.safety_validation?.issues?.length > 0 && (
                        <div className="text-red-600">
                          <strong>Issues:</strong>
                          <ul className="list-disc list-inside">
                            {assignmentOptions.available_drivers?.find(d => d.id == selectedDriver)?.safety_validation?.issues?.map((issue, idx) => (
                              <li key={idx}>{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {assignmentOptions.available_drivers?.find(d => d.id == selectedDriver)?.safety_validation?.warnings?.length > 0 && (
                        <div className="text-yellow-600">
                          <strong>Warnings:</strong>
                          <ul className="list-disc list-inside">
                            {assignmentOptions.available_drivers?.find(d => d.id == selectedDriver)?.safety_validation?.warnings?.map((warning, idx) => (
                              <li key={idx}>{warning}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="safetyOverride"
                    checked={safetyOverride}
                    onChange={(e) => setSafetyOverride(e.target.checked)}
                    className="mr-2"
                  />
                  <label htmlFor="safetyOverride" className="text-sm text-gray-700">
                    Override safety warnings (Admin only)
                  </label>
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={() => setShowApprovalModal(false)}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={approveRequestWithAssignment}
                    disabled={!selectedVehicle || !selectedDriver}
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
                  >
                    Approve & Assign
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

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

export default AdminDashboard;
