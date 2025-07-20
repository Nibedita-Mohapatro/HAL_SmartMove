import React, { useState, useEffect } from 'react';
import VehicleForm from './VehicleForm';
import VehicleList from './VehicleList';

const VehicleManagement = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState(null);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    type: 'all',
    searchTerm: ''
  });

  useEffect(() => {
    fetchVehicles();
  }, []);

  const fetchVehicles = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/vehicles/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setVehicles(data.vehicles || []);
      } else {
        setError('Failed to fetch vehicles');
      }
    } catch (error) {
      console.error('Error fetching vehicles:', error);
      setError('Network error while fetching vehicles');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateVehicle = async (vehicleData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/vehicles/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(vehicleData),
      });

      if (response.ok) {
        const result = await response.json();
        setVehicles([...vehicles, result.vehicle]);
        setShowCreateForm(false);
        setError('');
        return { success: true, message: 'Vehicle created successfully' };
      } else {
        const errorData = await response.json();
        let errorMessage = 'Failed to create vehicle';

        if (Array.isArray(errorData.detail)) {
          // Handle validation errors
          errorMessage = errorData.detail.map(err => {
            if (typeof err === 'object' && err.msg) {
              return err.msg;
            } else if (typeof err === 'string') {
              return err;
            } else {
              return 'Validation error';
            }
          }).join(', ');
        } else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }

        return { success: false, message: errorMessage };
      }
    } catch (error) {
      console.error('Error creating vehicle:', error);
      return { success: false, message: 'Network error while creating vehicle' };
    }
  };

  const handleUpdateVehicle = async (vehicleId, vehicleData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/vehicles/${vehicleId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(vehicleData),
      });

      if (response.ok) {
        const result = await response.json();
        setVehicles(vehicles.map(v => v.id === vehicleId ? result.vehicle : v));
        setEditingVehicle(null);
        setError('');
        return { success: true, message: 'Vehicle updated successfully' };
      } else {
        const errorData = await response.json();
        let errorMessage = 'Failed to update vehicle';

        if (Array.isArray(errorData.detail)) {
          // Handle validation errors
          errorMessage = errorData.detail.map(err => {
            if (typeof err === 'object' && err.msg) {
              return err.msg;
            } else if (typeof err === 'string') {
              return err;
            } else {
              return 'Validation error';
            }
          }).join(', ');
        } else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }

        return { success: false, message: errorMessage };
      }
    } catch (error) {
      console.error('Error updating vehicle:', error);
      return { success: false, message: 'Network error while updating vehicle' };
    }
  };

  const handleDeleteVehicle = async (vehicleId) => {
    if (!window.confirm('Are you sure you want to delete this vehicle?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/vehicles/${vehicleId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setVehicles(vehicles.filter(v => v.id !== vehicleId));
        setError('');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to delete vehicle');
      }
    } catch (error) {
      console.error('Error deleting vehicle:', error);
      setError('Network error while deleting vehicle');
    }
  };

  const handleToggleStatus = async (vehicleId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/vehicles/${vehicleId}/toggle-status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        setVehicles(vehicles.map(v =>
          v.id === vehicleId
            ? { ...v, is_active: result.is_active }
            : v
        ));
        setError('');
        // Show success message
        alert(result.message || 'Vehicle status updated successfully');
      } else {
        const errorData = await response.json();
        let errorMessage = 'Failed to update vehicle status';

        if (Array.isArray(errorData.detail)) {
          // Handle validation errors properly
          errorMessage = errorData.detail.map(err => {
            if (typeof err === 'object' && err.msg) {
              return err.msg;
            } else if (typeof err === 'string') {
              return err;
            } else {
              return 'Validation error';
            }
          }).join(', ');
        } else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }

        setError(errorMessage);
      }
    } catch (error) {
      console.error('Error updating vehicle status:', error);
      setError('Network error while updating vehicle status');
    }
  };

  const filteredVehicles = vehicles.filter(vehicle => {
    const matchesStatus = filters.status === 'all' || vehicle.is_active === (filters.status === 'active');
    const matchesType = filters.type === 'all' || vehicle.vehicle_type === filters.type;
    const matchesSearch = !filters.searchTerm ||
      (vehicle.vehicle_number && vehicle.vehicle_number.toLowerCase().includes(filters.searchTerm.toLowerCase())) ||
      (vehicle.model && vehicle.model.toLowerCase().includes(filters.searchTerm.toLowerCase())) ||
      (vehicle.current_location && vehicle.current_location.toLowerCase().includes(filters.searchTerm.toLowerCase()));

    return matchesStatus && matchesType && matchesSearch;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading vehicles...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Vehicle Management</h2>
          <p className="text-gray-600">Manage fleet vehicles and their availability</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-hal-blue hover:bg-hal-navy text-white px-4 py-2 rounded-md font-medium"
        >
          Add New Vehicle
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-red-800">{error}</div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-gray-900">{vehicles.length}</div>
          <div className="text-sm text-gray-600">Total Vehicles</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-green-600">
            {vehicles.filter(v => v.status === 'available').length}
          </div>
          <div className="text-sm text-gray-600">Available</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-blue-600">
            {vehicles.filter(v => v.status === 'in_use').length}
          </div>
          <div className="text-sm text-gray-600">In Use</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-red-600">
            {vehicles.filter(v => v.status === 'maintenance').length}
          </div>
          <div className="text-sm text-gray-600">Maintenance</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search registration, make, model..."
              value={filters.searchTerm}
              onChange={(e) => setFilters({...filters, searchTerm: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="available">Available</option>
              <option value="in_use">In Use</option>
              <option value="maintenance">Maintenance</option>
              <option value="out_of_service">Out of Service</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={filters.type}
              onChange={(e) => setFilters({...filters, type: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            >
              <option value="all">All Types</option>
              <option value="sedan">Sedan</option>
              <option value="suv">SUV</option>
              <option value="bus">Bus</option>
              <option value="van">Van</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => setFilters({status: 'all', type: 'all', searchTerm: ''})}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Create/Edit Vehicle Form Modal */}
      {(showCreateForm || editingVehicle) && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <VehicleForm
              vehicle={editingVehicle}
              onSubmit={editingVehicle ? 
                (data) => handleUpdateVehicle(editingVehicle.id, data) : 
                handleCreateVehicle
              }
              onCancel={() => {
                setShowCreateForm(false);
                setEditingVehicle(null);
              }}
            />
          </div>
        </div>
      )}

      {/* Vehicle List */}
      <VehicleList
        vehicles={filteredVehicles}
        onEdit={setEditingVehicle}
        onDelete={handleDeleteVehicle}
        onToggleStatus={handleToggleStatus}
      />
    </div>
  );
};

export default VehicleManagement;
