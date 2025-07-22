import React, { useState, useEffect } from 'react';

const ResourceAvailabilityCounters = ({ onResourceUpdate }) => {
  const [resourceData, setResourceData] = useState({
    available_drivers: 0,
    available_vehicles: 0,
    pending_requests: 0,
    driver_status: 'good',
    vehicle_status: 'good',
    pending_status: 'good',
    driver_availability_percentage: 0,
    vehicle_availability_percentage: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchResourceAvailability = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No access token found');
        return;
      }

      const response = await fetch('http://localhost:8000/api/v1/admin/resource-availability', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setResourceData(data);
        setError(null);
        
        // Notify parent component of resource update
        if (onResourceUpdate) {
          onResourceUpdate(data);
        }
      } else {
        setError('Failed to fetch resource availability');
      }
    } catch (error) {
      console.error('Error fetching resource availability:', error);
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResourceAvailability();
    
    // Set up polling for real-time updates every 30 seconds
    const interval = setInterval(fetchResourceAvailability, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'good':
        return 'bg-green-500';
      case 'warning':
        return 'bg-orange-500';
      case 'critical':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getTextColor = (status) => {
    switch (status) {
      case 'good':
        return 'text-green-700';
      case 'warning':
        return 'text-orange-700';
      case 'critical':
        return 'text-red-700';
      default:
        return 'text-gray-700';
    }
  };

  const getBorderColor = (status) => {
    switch (status) {
      case 'good':
        return 'border-green-200';
      case 'warning':
        return 'border-orange-200';
      case 'critical':
        return 'border-red-200';
      default:
        return 'border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-lg shadow p-4 animate-pulse">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gray-300 rounded-full"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
                <div className="h-6 bg-gray-300 rounded w-1/2"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div className="flex items-center">
          <span className="text-red-600 text-sm">⚠️ {error}</span>
          <button
            onClick={fetchResourceAvailability}
            className="ml-auto text-red-600 hover:text-red-800 text-sm underline"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      {/* Available Drivers Counter */}
      <div className={`bg-white rounded-lg shadow border-l-4 ${getBorderColor(resourceData.driver_status)} p-4 hover:shadow-md transition-shadow`}>
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 ${getStatusColor(resourceData.driver_status)} rounded-full flex items-center justify-center`}>
            <span className="text-white text-lg">👨‍✈️</span>
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-500">Available Drivers</h3>
              <span className={`text-xs font-medium ${getTextColor(resourceData.driver_status)}`}>
                {resourceData.driver_availability_percentage}%
              </span>
            </div>
            <div className="flex items-baseline space-x-2">
              <p className={`text-2xl font-bold ${getTextColor(resourceData.driver_status)}`}>
                {resourceData.available_drivers}
              </p>
              <span className="text-sm text-gray-500">
                / {resourceData.total_drivers}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Available Vehicles Counter */}
      <div className={`bg-white rounded-lg shadow border-l-4 ${getBorderColor(resourceData.vehicle_status)} p-4 hover:shadow-md transition-shadow`}>
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 ${getStatusColor(resourceData.vehicle_status)} rounded-full flex items-center justify-center`}>
            <span className="text-white text-lg">🚗</span>
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-500">Available Vehicles</h3>
              <span className={`text-xs font-medium ${getTextColor(resourceData.vehicle_status)}`}>
                {resourceData.vehicle_availability_percentage}%
              </span>
            </div>
            <div className="flex items-baseline space-x-2">
              <p className={`text-2xl font-bold ${getTextColor(resourceData.vehicle_status)}`}>
                {resourceData.available_vehicles}
              </p>
              <span className="text-sm text-gray-500">
                / {resourceData.total_vehicles}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Pending Requests Counter */}
      <div className={`bg-white rounded-lg shadow border-l-4 ${getBorderColor(resourceData.pending_status)} p-4 hover:shadow-md transition-shadow`}>
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 ${getStatusColor(resourceData.pending_status)} rounded-full flex items-center justify-center`}>
            <span className="text-white text-lg">📋</span>
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-500">Pending Requests</h3>
              <span className={`text-xs font-medium ${getTextColor(resourceData.pending_status)}`}>
                {resourceData.pending_requests > 10 ? 'High' : resourceData.pending_requests > 5 ? 'Medium' : 'Low'}
              </span>
            </div>
            <div className="flex items-baseline space-x-2">
              <p className={`text-2xl font-bold ${getTextColor(resourceData.pending_status)}`}>
                {resourceData.pending_requests}
              </p>
              <span className="text-sm text-gray-500">
                awaiting
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResourceAvailabilityCounters;
