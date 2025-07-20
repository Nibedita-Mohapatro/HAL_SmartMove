import React, { useState, useEffect } from 'react';
import DriverForm from './DriverForm';
import DriverList from './DriverList';

const DriverManagement = () => {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingDriver, setEditingDriver] = useState(null);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    license_type: 'all',
    searchTerm: ''
  });

  useEffect(() => {
    fetchDrivers();
  }, []);

  const fetchDrivers = async () => {
    try {
      const token = localStorage.getItem('token');
      // Only fetch active drivers by default
      const response = await fetch('http://localhost:8000/api/v1/drivers/?is_active=true', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDrivers(data.drivers || []);
      } else {
        setError('Failed to fetch drivers');
      }
    } catch (error) {
      console.error('Error fetching drivers:', error);
      setError('Network error while fetching drivers');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDriver = async (driverData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/drivers/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(driverData),
      });

      if (response.ok) {
        const result = await response.json();
        setDrivers([...drivers, result.driver]);
        setShowCreateForm(false);
        setError('');
        return { success: true, message: 'Driver created successfully' };
      } else {
        const errorData = await response.json();
        return { success: false, message: errorData.detail || 'Failed to create driver' };
      }
    } catch (error) {
      console.error('Error creating driver:', error);
      return { success: false, message: 'Network error while creating driver' };
    }
  };

  const handleUpdateDriver = async (driverId, driverData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/drivers/${driverId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(driverData),
      });

      if (response.ok) {
        const result = await response.json();
        setDrivers(drivers.map(d => d.id === driverId ? result.driver : d));
        setEditingDriver(null);
        setError('');
        return { success: true, message: 'Driver updated successfully' };
      } else {
        const errorData = await response.json();
        return { success: false, message: errorData.detail || 'Failed to update driver' };
      }
    } catch (error) {
      console.error('Error updating driver:', error);
      return { success: false, message: 'Network error while updating driver' };
    }
  };

  const handleDeleteDriver = async (driverId) => {
    const driver = drivers.find(d => d.id === driverId);
    const driverName = driver ? `${driver.first_name} ${driver.last_name}` : 'this driver';

    if (!window.confirm(`Are you sure you want to delete ${driverName}? This action cannot be undone.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/drivers/${driverId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();

        // Remove driver from the list regardless of soft or hard delete
        setDrivers(drivers.filter(d => d.id !== driverId));
        setError('');

        // Show success message with appropriate feedback
        const deleteType = result.type === 'soft_delete' ?
          'Driver deactivated successfully (historical data preserved)' :
          'Driver deleted successfully';

        alert(deleteType);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to delete driver');
      }
    } catch (error) {
      console.error('Error deleting driver:', error);
      setError('Network error while deleting driver');
    }
  };

  const handleToggleStatus = async (driverId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/drivers/${driverId}/toggle-status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        setDrivers(drivers.map(d =>
          d.id === driverId
            ? { ...d, is_active: result.is_active }
            : d
        ));
        setError('');
        // Show success message
        alert(result.message || 'Driver status updated successfully');
      } else {
        const errorData = await response.json();
        if (Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map(err => err.msg || err.message || 'Validation error').join(', ');
          setError(errorMessages);
        } else {
          setError(errorData.detail || 'Failed to update driver status');
        }
      }
    } catch (error) {
      console.error('Error updating driver status:', error);
      setError('Network error while updating driver status');
    }
  };

  const filteredDrivers = drivers.filter(driver => {
    const matchesStatus = filters.status === 'all' || driver.status === filters.status;
    const matchesLicenseType = filters.license_type === 'all' || driver.license_type === filters.license_type;
    const matchesSearch = !filters.searchTerm || 
      driver.first_name.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
      driver.last_name.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
      driver.employee_id.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
      driver.license_number.toLowerCase().includes(filters.searchTerm.toLowerCase());

    return matchesStatus && matchesLicenseType && matchesSearch;
  });

  const isLicenseExpiring = (expiryDate) => {
    if (!expiryDate) return false;
    const today = new Date();
    const expiry = new Date(expiryDate);
    const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry <= 30;
  };

  const expiringLicenses = drivers.filter(driver => isLicenseExpiring(driver.license_expiry));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading drivers...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Driver Management</h2>
          <p className="text-gray-600">Manage drivers and their licenses</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-hal-blue hover:bg-hal-navy text-white px-4 py-2 rounded-md font-medium"
        >
          Add New Driver
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-red-800">{error}</div>
        </div>
      )}

      {/* License Expiry Alert */}
      {expiringLicenses.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-yellow-400">⚠️</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                License Expiry Alert
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                {expiringLicenses.length} driver license(s) expiring within 30 days:
                <ul className="list-disc list-inside mt-1">
                  {expiringLicenses.map(driver => (
                    <li key={driver.id}>
                      {driver.first_name} {driver.last_name} - Expires {new Date(driver.license_expiry).toLocaleDateString()}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-gray-900">{drivers.length}</div>
          <div className="text-sm text-gray-600">Total Drivers</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-green-600">
            {drivers.filter(d => d.status === 'active').length}
          </div>
          <div className="text-sm text-gray-600">Active</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-yellow-600">
            {drivers.filter(d => d.status === 'on_leave').length}
          </div>
          <div className="text-sm text-gray-600">On Leave</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-red-600">
            {expiringLicenses.length}
          </div>
          <div className="text-sm text-gray-600">License Expiring</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search name, employee ID, license..."
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
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="on_leave">On Leave</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">License Type</label>
            <select
              value={filters.license_type}
              onChange={(e) => setFilters({...filters, license_type: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            >
              <option value="all">All Types</option>
              <option value="Light Vehicle">Light Vehicle</option>
              <option value="Heavy Vehicle">Heavy Vehicle</option>
              <option value="Commercial">Commercial</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => setFilters({status: 'all', license_type: 'all', searchTerm: ''})}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Create/Edit Driver Form Modal */}
      {(showCreateForm || editingDriver) && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <DriverForm
              driver={editingDriver}
              onSubmit={editingDriver ? 
                (data) => handleUpdateDriver(editingDriver.id, data) : 
                handleCreateDriver
              }
              onCancel={() => {
                setShowCreateForm(false);
                setEditingDriver(null);
              }}
            />
          </div>
        </div>
      )}

      {/* Driver List */}
      <DriverList
        drivers={filteredDrivers}
        onEdit={setEditingDriver}
        onDelete={handleDeleteDriver}
        onToggleStatus={handleToggleStatus}
      />
    </div>
  );
};

export default DriverManagement;
