import React, { useState, useEffect } from 'react';

const DriverForm = ({ driver, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    employee_id: '',
    first_name: '',
    last_name: '',
    phone: '',
    email: '',
    license_number: '',
    license_expiry: '',
    experience_years: 0,
    password: '',
    confirm_password: '',
    create_user_account: true
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (driver) {
      setFormData({
        employee_id: driver.employee_id || '',
        first_name: driver.first_name || '',
        last_name: driver.last_name || '',
        phone: driver.phone || '',
        email: driver.email || '',
        license_number: driver.license_number || '',
        license_expiry: driver.license_expiry || '',
        experience_years: driver.experience_years || 0,
        password: '',
        confirm_password: '',
        create_user_account: false
      });
    }
  }, [driver]);

  const experienceOptions = [
    { value: 0, label: 'No Experience' },
    { value: 1, label: '1 Year' },
    { value: 2, label: '2 Years' },
    { value: 3, label: '3 Years' },
    { value: 5, label: '5 Years' },
    { value: 10, label: '10+ Years' },
    { value: 15, label: '15+ Years' },
    { value: 20, label: '20+ Years' }
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const validateForm = () => {
    if (!formData.employee_id || !formData.first_name || !formData.last_name || 
        !formData.phone || !formData.license_number || !formData.license_expiry) {
      setError('Please fill in all required fields');
      return false;
    }

    if (formData.create_user_account && !driver) {
      if (!formData.email || !formData.password || !formData.confirm_password) {
        setError('Email and password are required when creating user account');
        return false;
      }
      
      if (formData.password !== formData.confirm_password) {
        setError('Passwords do not match');
        return false;
      }
      
      if (formData.password.length < 6) {
        setError('Password must be at least 6 characters long');
        return false;
      }
    }

    if (formData.email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        setError('Please enter a valid email address');
        return false;
      }
    }

    const phoneRegex = /^(\+91-)?[6-9]\d{9}$/;
    if (!phoneRegex.test(formData.phone)) {
      setError('Please enter a valid phone number');
      return false;
    }

    const today = new Date();
    const licenseExpiry = new Date(formData.license_expiry);

    if (licenseExpiry <= today) {
      setError('License expiry must be in the future');
      return false;
    }

    if (formData.experience_years < 0 || formData.experience_years > 50) {
      setError('Experience years must be between 0 and 50');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    try {
      const { confirm_password, ...submitData } = formData;
      const result = await onSubmit(submitData);
      if (result.success) {
        // Form will be closed by parent component
      } else {
        setError(result.message);
      }
    } catch (error) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-medium text-gray-900">
          {driver ? 'Edit Driver' : 'Add New Driver'}
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
          <div>
            <label htmlFor="employee_id" className="block text-sm font-medium text-gray-700 mb-1">
              Employee ID *
            </label>
            <input
              type="text"
              name="employee_id"
              id="employee_id"
              required
              disabled={!!driver}
              value={formData.employee_id}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent disabled:bg-gray-100"
              placeholder="e.g., DRV005"
            />
          </div>

          <div>
            <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">
              First Name *
            </label>
            <input
              type="text"
              name="first_name"
              id="first_name"
              required
              value={formData.first_name}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
              placeholder="e.g., Rajesh"
            />
          </div>

          <div>
            <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">
              Last Name *
            </label>
            <input
              type="text"
              name="last_name"
              id="last_name"
              required
              value={formData.last_name}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
              placeholder="e.g., Kumar"
            />
          </div>

          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
              Phone *
            </label>
            <input
              type="tel"
              name="phone"
              id="phone"
              required
              value={formData.phone}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
              placeholder="+91-9876543210"
            />
          </div>

          <div>
            <label htmlFor="license_number" className="block text-sm font-medium text-gray-700 mb-1">
              License Number *
            </label>
            <input
              type="text"
              name="license_number"
              id="license_number"
              required
              value={formData.license_number}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
              placeholder="e.g., KA0120230001"
            />
          </div>

          <div>
            <label htmlFor="license_expiry" className="block text-sm font-medium text-gray-700 mb-1">
              License Expiry *
            </label>
            <input
              type="date"
              name="license_expiry"
              id="license_expiry"
              required
              value={formData.license_expiry}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="experience_years" className="block text-sm font-medium text-gray-700 mb-1">
              Experience Years
            </label>
            <select
              name="experience_years"
              id="experience_years"
              value={formData.experience_years}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            >
              {experienceOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {!driver && (
          <div className="border-t pt-4 mt-6">
            <div className="flex items-center mb-4">
              <input
                type="checkbox"
                name="create_user_account"
                id="create_user_account"
                checked={formData.create_user_account}
                onChange={(e) => setFormData({...formData, create_user_account: e.target.checked})}
                className="h-4 w-4 text-hal-blue focus:ring-hal-blue border-gray-300 rounded"
              />
              <label htmlFor="create_user_account" className="ml-2 block text-sm text-gray-900">
                Create user account for driver login
              </label>
            </div>

            {formData.create_user_account && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    name="email"
                    id="email"
                    required={formData.create_user_account}
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
                    placeholder="driver@hal.co.in"
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                    Password *
                  </label>
                  <input
                    type="password"
                    name="password"
                    id="password"
                    required={formData.create_user_account}
                    value={formData.password}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
                    placeholder="Minimum 6 characters"
                  />
                </div>

                <div>
                  <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-1">
                    Confirm Password *
                  </label>
                  <input
                    type="password"
                    name="confirm_password"
                    id="confirm_password"
                    required={formData.create_user_account}
                    value={formData.confirm_password}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
                    placeholder="Re-enter password"
                  />
                </div>
              </div>
            )}
          </div>
        )}

        <div className="flex justify-end space-x-3 pt-6 border-t">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-hal-blue"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-hal-blue hover:bg-hal-blue-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-hal-blue disabled:opacity-50"
          >
            {loading ? 'Creating...' : (driver ? 'Update Driver' : 'Create Driver')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default DriverForm;
