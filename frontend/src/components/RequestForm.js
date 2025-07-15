import React, { useState, useEffect, useRef } from 'react';
import locationService from '../services/locationService';
import { useNavigate } from 'react-router-dom';

const RequestForm = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    request_date: '',
    request_time: '',
    passenger_count: 1,
    purpose: '',
    priority: 'medium'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Location suggestion states
  const [originSuggestions, setOriginSuggestions] = useState([]);
  const [destinationSuggestions, setDestinationSuggestions] = useState([]);
  const [showOriginSuggestions, setShowOriginSuggestions] = useState(false);
  const [showDestinationSuggestions, setShowDestinationSuggestions] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [loadingLocation, setLoadingLocation] = useState(false);

  const originInputRef = useRef(null);
  const destinationInputRef = useRef(null);

  // Get current location on component mount
  useEffect(() => {
    getCurrentLocation();
  }, []);

  // Get current location
  const getCurrentLocation = async () => {
    setLoadingLocation(true);
    try {
      const location = await locationService.getCurrentLocation();
      setCurrentLocation(location);
    } catch (error) {
      console.error('Failed to get current location:', error);
    } finally {
      setLoadingLocation(false);
    }
  };

  // Handle location input changes with suggestions
  const handleLocationChange = async (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));

    if (value.length > 1) {
      try {
        const suggestions = await locationService.searchLocations(value);

        if (field === 'origin') {
          setOriginSuggestions(suggestions);
          setShowOriginSuggestions(true);
        } else {
          setDestinationSuggestions(suggestions);
          setShowDestinationSuggestions(true);
        }
      } catch (error) {
        console.error('Error fetching suggestions:', error);
      }
    } else {
      if (field === 'origin') {
        setShowOriginSuggestions(false);
      } else {
        setShowDestinationSuggestions(false);
      }
    }
  };

  // Select suggestion
  const selectSuggestion = (field, suggestion) => {
    setFormData(prev => ({ ...prev, [field]: suggestion.address }));

    if (field === 'origin') {
      setShowOriginSuggestions(false);
    } else {
      setShowDestinationSuggestions(false);
    }
  };

  // Use current location as origin
  const useCurrentLocationAsOrigin = () => {
    if (currentLocation) {
      setFormData(prev => ({ ...prev, origin: currentLocation.address }));
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (name === 'origin' || name === 'destination') {
      handleLocationChange(name, value);
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/requests/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        navigate('/employee', { 
          state: { message: 'Transport request submitted successfully!' }
        });
      } else {
        setError(data.detail || 'Failed to submit request');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Get today's date for min date validation
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-hal-navy">HAL Transport</h1>
              <span className="ml-4 text-sm text-gray-500">New Request</span>
            </div>
            <div className="flex items-center">
              <button
                onClick={() => navigate('/employee')}
                className="text-hal-blue hover:text-hal-navy font-medium"
              >
                ← Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-6">
              Submit Transport Request
            </h3>

            {error && (
              <div className="mb-6 rounded-md bg-red-50 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">{error}</h3>
                  </div>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="relative">
                  <label htmlFor="origin" className="block text-sm font-medium text-gray-700">
                    Origin *
                  </label>
                  <div className="mt-1 relative">
                    <input
                      ref={originInputRef}
                      type="text"
                      name="origin"
                      id="origin"
                      required
                      value={formData.origin}
                      onChange={handleChange}
                      onFocus={() => setShowOriginSuggestions(true)}
                      onBlur={() => setTimeout(() => setShowOriginSuggestions(false), 200)}
                      className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm pr-10"
                      placeholder="Search for pickup location..."
                    />

                    {/* Current Location Button */}
                    <button
                      type="button"
                      onClick={useCurrentLocationAsOrigin}
                      disabled={loadingLocation || !currentLocation}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-blue-600 hover:text-blue-800 disabled:text-gray-400"
                      title="Use current location"
                    >
                      {loadingLocation ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                      ) : (
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                      )}
                    </button>

                    {/* Origin Suggestions Dropdown */}
                    {showOriginSuggestions && originSuggestions.length > 0 && (
                      <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
                        {originSuggestions.map((suggestion, index) => (
                          <div
                            key={index}
                            onClick={() => selectSuggestion('origin', suggestion)}
                            className="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-blue-50"
                          >
                            <div className="flex items-center">
                              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium mr-2 ${
                                suggestion.type === 'office' ? 'bg-blue-100 text-blue-800' :
                                suggestion.type === 'airport' ? 'bg-purple-100 text-purple-800' :
                                suggestion.type === 'tech_hub' ? 'bg-green-100 text-green-800' :
                                suggestion.type === 'city' ? 'bg-indigo-100 text-indigo-800' :
                                suggestion.type === 'town' ? 'bg-yellow-100 text-yellow-800' :
                                suggestion.type === 'village' ? 'bg-emerald-100 text-emerald-800' :
                                suggestion.type === 'residential' ? 'bg-pink-100 text-pink-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {suggestion.type === 'office' ? '🏢' :
                                 suggestion.type === 'airport' ? '✈️' :
                                 suggestion.type === 'tech_hub' ? '💻' :
                                 suggestion.type === 'transport' ? '🚌' :
                                 suggestion.type === 'shopping' ? '🛍️' :
                                 suggestion.type === 'government' ? '🏛️' :
                                 suggestion.type === 'city' ? '🏙️' :
                                 suggestion.type === 'town' ? '🏘️' :
                                 suggestion.type === 'village' ? '🏡' :
                                 suggestion.type === 'residential' ? '🏠' :
                                 suggestion.type === 'commercial' ? '🏬' :
                                 suggestion.type === 'landmark' ? '🗿' :
                                 suggestion.type === 'business' ? '💼' :
                                 '📍'}
                              </span>
                              <div>
                                <div className="font-medium text-gray-900">{suggestion.name}</div>
                                <div className="text-gray-500 text-sm">{suggestion.address}</div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className="relative">
                  <label htmlFor="destination" className="block text-sm font-medium text-gray-700">
                    Destination *
                  </label>
                  <div className="mt-1 relative">
                    <input
                      ref={destinationInputRef}
                      type="text"
                      name="destination"
                      id="destination"
                      required
                      value={formData.destination}
                      onChange={handleChange}
                      onFocus={() => setShowDestinationSuggestions(true)}
                      onBlur={() => setTimeout(() => setShowDestinationSuggestions(false), 200)}
                      className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Search for destination..."
                    />

                    {/* Destination Suggestions Dropdown */}
                    {showDestinationSuggestions && destinationSuggestions.length > 0 && (
                      <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
                        {destinationSuggestions.map((suggestion, index) => (
                          <div
                            key={index}
                            onClick={() => selectSuggestion('destination', suggestion)}
                            className="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-blue-50"
                          >
                            <div className="flex items-center">
                              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium mr-2 ${
                                suggestion.type === 'office' ? 'bg-blue-100 text-blue-800' :
                                suggestion.type === 'airport' ? 'bg-purple-100 text-purple-800' :
                                suggestion.type === 'tech_hub' ? 'bg-green-100 text-green-800' :
                                suggestion.type === 'city' ? 'bg-indigo-100 text-indigo-800' :
                                suggestion.type === 'town' ? 'bg-yellow-100 text-yellow-800' :
                                suggestion.type === 'village' ? 'bg-emerald-100 text-emerald-800' :
                                suggestion.type === 'residential' ? 'bg-pink-100 text-pink-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {suggestion.type === 'office' ? '🏢' :
                                 suggestion.type === 'airport' ? '✈️' :
                                 suggestion.type === 'tech_hub' ? '💻' :
                                 suggestion.type === 'transport' ? '🚌' :
                                 suggestion.type === 'shopping' ? '🛍️' :
                                 suggestion.type === 'government' ? '🏛️' :
                                 suggestion.type === 'city' ? '🏙️' :
                                 suggestion.type === 'town' ? '🏘️' :
                                 suggestion.type === 'village' ? '🏡' :
                                 suggestion.type === 'residential' ? '🏠' :
                                 suggestion.type === 'commercial' ? '🏬' :
                                 suggestion.type === 'landmark' ? '🗿' :
                                 suggestion.type === 'business' ? '💼' :
                                 '📍'}
                              </span>
                              <div>
                                <div className="font-medium text-gray-900">{suggestion.name}</div>
                                <div className="text-gray-500 text-sm">{suggestion.address}</div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <label htmlFor="request_date" className="block text-sm font-medium text-gray-700">
                    Date *
                  </label>
                  <input
                    type="date"
                    name="request_date"
                    id="request_date"
                    required
                    min={today}
                    value={formData.request_date}
                    onChange={handleChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-hal-blue focus:border-hal-blue sm:text-sm"
                  />
                </div>

                <div>
                  <label htmlFor="request_time" className="block text-sm font-medium text-gray-700">
                    Time *
                  </label>
                  <select
                    name="request_time"
                    id="request_time"
                    required
                    value={formData.request_time}
                    onChange={handleChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-hal-blue focus:border-hal-blue sm:text-sm"
                  >
                    <option value="">Select time...</option>
                    <option value="06:00">06:00 AM</option>
                    <option value="06:30">06:30 AM</option>
                    <option value="07:00">07:00 AM</option>
                    <option value="07:30">07:30 AM</option>
                    <option value="08:00">08:00 AM</option>
                    <option value="08:30">08:30 AM</option>
                    <option value="09:00">09:00 AM</option>
                    <option value="09:30">09:30 AM</option>
                    <option value="10:00">10:00 AM</option>
                    <option value="10:30">10:30 AM</option>
                    <option value="11:00">11:00 AM</option>
                    <option value="11:30">11:30 AM</option>
                    <option value="12:00">12:00 PM</option>
                    <option value="12:30">12:30 PM</option>
                    <option value="13:00">01:00 PM</option>
                    <option value="13:30">01:30 PM</option>
                    <option value="14:00">02:00 PM</option>
                    <option value="14:30">02:30 PM</option>
                    <option value="15:00">03:00 PM</option>
                    <option value="15:30">03:30 PM</option>
                    <option value="16:00">04:00 PM</option>
                    <option value="16:30">04:30 PM</option>
                    <option value="17:00">05:00 PM</option>
                    <option value="17:30">05:30 PM</option>
                    <option value="18:00">06:00 PM</option>
                    <option value="18:30">06:30 PM</option>
                    <option value="19:00">07:00 PM</option>
                    <option value="19:30">07:30 PM</option>
                    <option value="20:00">08:00 PM</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="passenger_count" className="block text-sm font-medium text-gray-700">
                    Number of Passengers *
                  </label>
                  <input
                    type="number"
                    name="passenger_count"
                    id="passenger_count"
                    required
                    min="1"
                    max="50"
                    value={formData.passenger_count}
                    onChange={handleChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-hal-blue focus:border-hal-blue sm:text-sm"
                  />
                </div>

                <div>
                  <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
                    Priority
                  </label>
                  <select
                    name="priority"
                    id="priority"
                    value={formData.priority}
                    onChange={handleChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-hal-blue focus:border-hal-blue sm:text-sm"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>

              <div>
                <label htmlFor="purpose" className="block text-sm font-medium text-gray-700">
                  Purpose
                </label>
                <textarea
                  name="purpose"
                  id="purpose"
                  rows={3}
                  value={formData.purpose}
                  onChange={handleChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-hal-blue focus:border-hal-blue sm:text-sm"
                  placeholder="Brief description of the purpose of travel"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => navigate('/employee')}
                  className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-hal-blue"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-hal-blue hover:bg-hal-navy py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-hal-blue disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Submitting...
                    </>
                  ) : (
                    'Submit Request'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Help Section */}
        <div className="mt-6 bg-blue-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900 mb-2">Request Guidelines:</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Submit requests at least 24 hours in advance when possible</li>
            <li>• Provide accurate passenger count for proper vehicle assignment</li>
            <li>• Use "Urgent" priority only for emergency situations</li>
            <li>• Include detailed purpose for faster approval</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default RequestForm;
