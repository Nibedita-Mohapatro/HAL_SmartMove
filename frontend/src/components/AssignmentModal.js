import React, { useState, useEffect } from 'react';

const AssignmentModal = ({ request, onClose, onAssign, onRefresh }) => {
  const [vehicles, setVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [assigning, setAssigning] = useState(false);
  const [assignmentData, setAssignmentData] = useState({
    vehicle_id: '',
    driver_id: '',
    notes: ''
  });
  const [suggestions, setSuggestions] = useState({
    vehicles: [],
    drivers: []
  });
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAvailableResources();
  }, []);

  const fetchAvailableResources = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch available vehicles
      const vehiclesResponse = await fetch('http://localhost:8000/api/v1/vehicles/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      // Fetch available drivers
      const driversResponse = await fetch('http://localhost:8000/api/v1/drivers/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (vehiclesResponse.ok && driversResponse.ok) {
        const vehiclesData = await vehiclesResponse.json();
        const driversData = await driversResponse.json();
        
        const availableVehicles = vehiclesData.vehicles.filter(v => v.status === 'available');
        const availableDrivers = driversData.drivers.filter(d => d.status === 'active');
        
        setVehicles(availableVehicles);
        setDrivers(availableDrivers);
        
        // Generate suggestions
        generateSuggestions(availableVehicles, availableDrivers);
      } else {
        setError('Failed to fetch available resources');
      }
    } catch (error) {
      console.error('Error fetching resources:', error);
      setError('Network error while fetching resources');
    } finally {
      setLoading(false);
    }
  };

  const generateSuggestions = (availableVehicles, availableDrivers) => {
    // Vehicle suggestions based on passenger count and type
    const vehicleSuggestions = availableVehicles
      .filter(vehicle => {
        const capacity = vehicle.capacity || 4;
        return capacity >= request.passenger_count;
      })
      .sort((a, b) => {
        // Prefer vehicles with capacity closest to passenger count
        const aDiff = Math.abs((a.capacity || 4) - request.passenger_count);
        const bDiff = Math.abs((b.capacity || 4) - request.passenger_count);
        return aDiff - bDiff;
      })
      .slice(0, 3);

    // Driver suggestions based on rating and experience
    const driverSuggestions = availableDrivers
      .sort((a, b) => {
        // Sort by rating first, then by total trips
        if (b.rating !== a.rating) {
          return (b.rating || 0) - (a.rating || 0);
        }
        return (b.total_trips || 0) - (a.total_trips || 0);
      })
      .slice(0, 3);

    setSuggestions({
      vehicles: vehicleSuggestions,
      drivers: driverSuggestions
    });

    // Auto-select best suggestions
    if (vehicleSuggestions.length > 0) {
      setAssignmentData(prev => ({ ...prev, vehicle_id: vehicleSuggestions[0].id }));
    }
    if (driverSuggestions.length > 0) {
      setAssignmentData(prev => ({ ...prev, driver_id: driverSuggestions[0].id }));
    }
  };

  const handleAssign = async () => {
    if (!assignmentData.vehicle_id || !assignmentData.driver_id) {
      setError('Please select both vehicle and driver');
      return;
    }

    setAssigning(true);
    setError('');

    try {
      const result = await onAssign(request.id, assignmentData);
      if (result.success) {
        onRefresh();
        onClose();
      } else {
        setError(result.message);
      }
    } catch (error) {
      setError('Error assigning resources');
    } finally {
      setAssigning(false);
    }
  };

  const getVehicleInfo = (vehicleId) => {
    const vehicle = vehicles.find(v => v.id === parseInt(vehicleId));
    return vehicle ? `${vehicle.registration_number} (${vehicle.make} ${vehicle.model})` : '';
  };

  const getDriverInfo = (driverId) => {
    const driver = drivers.find(d => d.id === parseInt(driverId));
    return driver ? `${driver.first_name} ${driver.last_name} (${driver.employee_id})` : '';
  };

  const getSuggestionReason = (vehicle, driver) => {
    const reasons = [];
    
    if (vehicle) {
      if (vehicle.capacity >= request.passenger_count) {
        reasons.push(`Suitable capacity (${vehicle.capacity} seats)`);
      }
      if (vehicle.fuel_type === 'diesel' && request.passenger_count > 4) {
        reasons.push('Fuel efficient for group travel');
      }
    }
    
    if (driver) {
      if (driver.rating >= 4.5) {
        reasons.push(`High rating (${driver.rating}★)`);
      }
      if (driver.total_trips > 200) {
        reasons.push('Experienced driver');
      }
    }
    
    return reasons.join(', ');
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
          <div className="flex items-center justify-center h-32">
            <div className="text-lg">Loading available resources...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-medium text-gray-900">Assign Vehicle & Driver</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            &times;
          </button>
        </div>

        {/* Request Info */}
        <div className="bg-gray-50 p-4 rounded-md mb-6">
          <h4 className="font-medium text-gray-900 mb-2">Request Details</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Route:</span> {request.origin} → {request.destination}
            </div>
            <div>
              <span className="text-gray-600">Passengers:</span> {request.passenger_count}
            </div>
            <div>
              <span className="text-gray-600">Date:</span> {request.request_date}
            </div>
            <div>
              <span className="text-gray-600">Time:</span> {request.request_time}
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-3">
            <div className="text-red-800 text-sm">{error}</div>
          </div>
        )}

        {/* AI Suggestions */}
        {suggestions.vehicles.length > 0 && suggestions.drivers.length > 0 && (
          <div className="bg-blue-50 p-4 rounded-md mb-6">
            <h4 className="font-medium text-blue-900 mb-2">🤖 AI Recommendations</h4>
            <div className="text-sm text-blue-800">
              <div className="mb-2">
                <strong>Best Match:</strong> {getVehicleInfo(suggestions.vehicles[0].id)} + {getDriverInfo(suggestions.drivers[0].id)}
              </div>
              <div className="text-blue-600">
                {getSuggestionReason(suggestions.vehicles[0], suggestions.drivers[0])}
              </div>
            </div>
          </div>
        )}

        {/* Assignment Form */}
        <div className="space-y-4">
          {/* Vehicle Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Vehicle *
            </label>
            <select
              value={assignmentData.vehicle_id}
              onChange={(e) => setAssignmentData({...assignmentData, vehicle_id: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            >
              <option value="">Choose a vehicle...</option>
              {vehicles.map(vehicle => (
                <option key={vehicle.id} value={vehicle.id}>
                  {vehicle.registration_number} - {vehicle.make} {vehicle.model} ({vehicle.capacity} seats, {vehicle.fuel_type})
                </option>
              ))}
            </select>
            {vehicles.length === 0 && (
              <p className="text-sm text-red-600 mt-1">No available vehicles found</p>
            )}
          </div>

          {/* Driver Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Driver *
            </label>
            <select
              value={assignmentData.driver_id}
              onChange={(e) => setAssignmentData({...assignmentData, driver_id: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            >
              <option value="">Choose a driver...</option>
              {drivers.map(driver => (
                <option key={driver.id} value={driver.id}>
                  {driver.first_name} {driver.last_name} ({driver.employee_id}) - Rating: {driver.rating}★, Trips: {driver.total_trips}
                </option>
              ))}
            </select>
            {drivers.length === 0 && (
              <p className="text-sm text-red-600 mt-1">No available drivers found</p>
            )}
          </div>

          {/* Assignment Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Assignment Notes
            </label>
            <textarea
              value={assignmentData.notes}
              onChange={(e) => setAssignmentData({...assignmentData, notes: e.target.value})}
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
              placeholder="Optional notes about this assignment..."
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-6 mt-6 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Cancel
          </button>
          <button
            onClick={handleAssign}
            disabled={assigning || !assignmentData.vehicle_id || !assignmentData.driver_id}
            className="px-4 py-2 bg-hal-blue text-white rounded-md hover:bg-hal-navy focus:outline-none focus:ring-2 focus:ring-hal-blue disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {assigning ? 'Assigning...' : 'Assign Resources'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AssignmentModal;
