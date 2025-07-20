import React, { useState, useEffect } from 'react';

const VehicleForm = ({ vehicle, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    vehicle_number: '',
    vehicle_type: 'bus',
    model: '',
    year_of_manufacture: '',
    capacity: '',
    fuel_type: 'diesel',
    insurance_expiry: '',
    fitness_certificate_expiry: '',
    current_location: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (vehicle) {
      setFormData({
        vehicle_number: vehicle.vehicle_number || '',
        vehicle_type: vehicle.vehicle_type || 'bus',
        model: vehicle.model || '',
        year_of_manufacture: vehicle.year_of_manufacture || '',
        capacity: vehicle.capacity || '',
        fuel_type: vehicle.fuel_type || 'diesel',
        insurance_expiry: vehicle.insurance_expiry || '',
        fitness_certificate_expiry: vehicle.fitness_certificate_expiry || '',
        current_location: vehicle.current_location || ''
      });
    }
  }, [vehicle]);

  const vehicleTypes = [
    { value: 'bus', label: 'Bus' },
    { value: 'car', label: 'Car' },
    { value: 'van', label: 'Van' },
    { value: 'shuttle', label: 'Shuttle' }
  ];

  const fuelTypes = [
    { value: 'petrol', label: 'Petrol' },
    { value: 'diesel', label: 'Diesel' },
    { value: 'electric', label: 'Electric' },
    { value: 'hybrid', label: 'Hybrid' }
  ];

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

    // Basic validation
    if (!formData.vehicle_number || !formData.vehicle_type || !formData.capacity) {
      setError('Please fill in all required fields');
      setLoading(false);
      return;
    }

    // Year validation
    if (formData.year_of_manufacture) {
      const currentYear = new Date().getFullYear();
      const year = parseInt(formData.year_of_manufacture);
      if (year < 1990 || year > currentYear + 1) {
        setError('Please enter a valid year');
        setLoading(false);
        return;
      }
    }

    // Capacity validation
    if (formData.capacity && (parseInt(formData.capacity) < 1 || parseInt(formData.capacity) > 100)) {
      setError('Please enter a valid capacity (1-100)');
      setLoading(false);
      return;
    }

    try {
      const result = await onSubmit(formData);
      if (result.success) {
        // Form will be closed by parent component
      } else {
        // Handle different types of error messages
        if (typeof result.message === 'string') {
          setError(result.message);
        } else if (Array.isArray(result.message)) {
          setError(result.message.join(', '));
        } else {
          setError('Failed to save vehicle');
        }
      }
    } catch (error) {
      console.error('Vehicle form error:', error);
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-medium text-gray-900">
          {vehicle ? 'Edit Vehicle' : 'Add New Vehicle'}
        </h3>
        <button
          onClick={onCancel}
          className="text-gray-400 hover:text-gray-600"
        >
          <span className="text-2xl">&times;</span>
        </button>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-3">
          <div className="text-red-800 text-sm">{error}</div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Vehicle Number */}
          <div>
            <label htmlFor="vehicle_number" className="block text-sm font-medium text-gray-700 mb-1">
              Vehicle Number *
            </label>
            <input
              type="text"
              name="vehicle_number"
              id="vehicle_number"
              required
              value={formData.vehicle_number}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
              placeholder="e.g., KA01AB1234"
            />
          </div>

          {/* Vehicle Type */}
          <div>
            <label htmlFor="vehicle_type" className="block text-sm font-medium text-gray-700 mb-1">
              Vehicle Type *
            </label>
            <select
              name="vehicle_type"
              id="vehicle_type"
              required
              value={formData.vehicle_type}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            >
              {vehicleTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Model */}
          <div>
            <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-1">
              Model
            </label>
            <input
              type="text"
              name="model"
              id="model"
              value={formData.model}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
              placeholder="e.g., Innova"
            />
          </div>

          {/* Year of Manufacture */}
          <div>
            <label htmlFor="year_of_manufacture" className="block text-sm font-medium text-gray-700 mb-1">
              Year of Manufacture
            </label>
            <input
              type="number"
              name="year_of_manufacture"
              id="year_of_manufacture"
              min="1990"
              max={new Date().getFullYear() + 1}
              value={formData.year_of_manufacture}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            />
          </div>

          {/* Capacity */}
          <div>
            <label htmlFor="capacity" className="block text-sm font-medium text-gray-700 mb-1">
              Seating Capacity *
            </label>
            <input
              type="number"
              name="capacity"
              id="capacity"
              required
              min="1"
              max="100"
              value={formData.capacity}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
              placeholder="e.g., 7"
            />
          </div>

          {/* Fuel Type */}
          <div>
            <label htmlFor="fuel_type" className="block text-sm font-medium text-gray-700 mb-1">
              Fuel Type
            </label>
            <select
              name="fuel_type"
              id="fuel_type"
              value={formData.fuel_type}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            >
              {fuelTypes.map(fuel => (
                <option key={fuel.value} value={fuel.value}>{fuel.label}</option>
              ))}
            </select>
          </div>

          {/* Current Location */}
          <div>
            <label htmlFor="current_location" className="block text-sm font-medium text-gray-700 mb-1">
              Current Location
            </label>
            <input
              type="text"
              name="current_location"
              id="current_location"
              value={formData.current_location}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
              placeholder="e.g., HAL Bangalore Office"
            />
          </div>
        </div>

        {/* Insurance and Fitness Certificate Dates */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="insurance_expiry" className="block text-sm font-medium text-gray-700 mb-1">
              Insurance Expiry
            </label>
            <input
              type="date"
              name="insurance_expiry"
              id="insurance_expiry"
              value={formData.insurance_expiry}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="fitness_certificate_expiry" className="block text-sm font-medium text-gray-700 mb-1">
              Fitness Certificate Expiry
            </label>
            <input
              type="date"
              name="fitness_certificate_expiry"
              id="fitness_certificate_expiry"
              value={formData.fitness_certificate_expiry}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            />
          </div>
        </div>

        {/* Form Actions */}
        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-hal-blue text-white rounded-md hover:bg-hal-navy focus:outline-none focus:ring-2 focus:ring-hal-blue disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (vehicle ? 'Updating...' : 'Creating...') : (vehicle ? 'Update Vehicle' : 'Create Vehicle')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default VehicleForm;
