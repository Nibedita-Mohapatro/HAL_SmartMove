import React, { useState, useEffect, useRef } from 'react';
import gpsService from '../services/gpsService';

const LiveGPSMap = ({ tripId, userRole, onClose }) => {
  const [trackingData, setTrackingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [gpsPermission, setGpsPermission] = useState('unknown');
  const [isLiveTracking, setIsLiveTracking] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    if (!tripId) return;

    initializeMap();
    fetchTrackingData();
    
    // Set up real-time updates
    const interval = setInterval(fetchTrackingData, 3000);
    
    return () => {
      clearInterval(interval);
      if (isLiveTracking) {
        gpsService.stopTracking();
      }
      cleanup();
    };
  }, [tripId]);

  const initializeMap = () => {
    // Initialize with a basic map (using OpenStreetMap/Leaflet as example)
    // In production, you'd use Google Maps, Mapbox, or similar
    if (mapRef.current && !mapInstanceRef.current) {
      // This is a placeholder for map initialization
      // You would integrate with your preferred mapping service here
      mapRef.current.innerHTML = `
        <div class="w-full h-full bg-gray-200 flex items-center justify-center">
          <div class="text-center">
            <div class="text-4xl mb-2">🗺️</div>
            <p class="text-gray-600">Interactive Map</p>
            <p class="text-sm text-gray-500">GPS tracking visualization</p>
          </div>
        </div>
      `;
    }
  };

  const fetchTrackingData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/gps/trip/${tripId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setTrackingData(data.tracking);
          updateMapWithTrackingData(data.tracking);
        } else {
          setError(data.message || 'Tracking not available');
        }
      } else {
        setError('Failed to fetch tracking data');
      }
    } catch (err) {
      setError('Error fetching tracking data');
    } finally {
      setLoading(false);
    }
  };

  const updateMapWithTrackingData = (tracking) => {
    // Update map with tracking data
    // This would integrate with your mapping service
    console.log('Updating map with tracking data:', tracking);
  };

  const requestGPSPermission = async () => {
    try {
      setLoading(true);
      const position = await gpsService.requestLocationPermission();
      setGpsPermission('granted');
      setCurrentLocation(position);
      setError('');
    } catch (err) {
      setGpsPermission('denied');
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const startLiveTracking = async () => {
    try {
      setLoading(true);
      
      await gpsService.startTracking(tripId, (locationData) => {
        setCurrentLocation(locationData);
        // Update map with new location
        updateMapWithLocation(locationData);
      });
      
      setIsLiveTracking(true);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const stopLiveTracking = () => {
    gpsService.stopTracking();
    setIsLiveTracking(false);
  };

  const updateMapWithLocation = (location) => {
    // Update map with current location
    console.log('Updating map with current location:', location);
    // This would update markers, path, etc. on the actual map
  };

  const cleanup = () => {
    // Clean up map resources
    markersRef.current = [];
    if (mapInstanceRef.current) {
      // Clean up map instance
      mapInstanceRef.current = null;
    }
  };

  const formatTime = (isoString) => {
    if (!isoString) return 'N/A';
    return new Date(isoString).toLocaleTimeString();
  };

  const formatCoordinate = (coord) => {
    return coord ? coord.toFixed(6) : 'N/A';
  };

  if (loading && !trackingData) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-4/5 lg:w-3/4 shadow-lg rounded-md bg-white">
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hal-blue mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading GPS map...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-5 mx-auto p-5 border w-11/12 md:w-11/12 lg:w-5/6 shadow-lg rounded-md bg-white max-h-screen overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            🛰️ Live GPS Tracking - Trip #{tripId}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* GPS Permission and Controls */}
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-blue-900">Real GPS Tracking</h4>
              <p className="text-sm text-blue-700">
                {gpsPermission === 'granted' ? 
                  '✅ Location permission granted' : 
                  '📍 Enable location access for real-time tracking'
                }
              </p>
            </div>
            <div className="flex space-x-2">
              {gpsPermission !== 'granted' && (
                <button
                  onClick={requestGPSPermission}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium disabled:bg-gray-400"
                >
                  {loading ? 'Requesting...' : 'Enable GPS'}
                </button>
              )}
              {gpsPermission === 'granted' && !isLiveTracking && userRole === 'transport' && (
                <button
                  onClick={startLiveTracking}
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm font-medium disabled:bg-gray-400"
                >
                  {loading ? 'Starting...' : 'Start Live Tracking'}
                </button>
              )}
              {isLiveTracking && (
                <button
                  onClick={stopLiveTracking}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm font-medium"
                >
                  Stop Tracking
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Live Location Status */}
        {currentLocation && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-green-900 flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-2"></div>
                  Live Location Active
                </h4>
                <p className="text-sm text-green-700">
                  {formatCoordinate(currentLocation.latitude)}, {formatCoordinate(currentLocation.longitude)}
                </p>
                <p className="text-xs text-green-600">
                  Accuracy: {currentLocation.accuracy?.toFixed(0)}m | Speed: {currentLocation.speed?.toFixed(1)} km/h
                </p>
              </div>
              <div className="text-right text-sm text-green-600">
                <p>Last Update:</p>
                <p>{formatTime(currentLocation.timestamp)}</p>
              </div>
            </div>
          </div>
        )}

        {/* Map Container */}
        <div className="mb-4">
          <div 
            ref={mapRef}
            className="w-full h-96 border border-gray-300 rounded-lg overflow-hidden"
            style={{ minHeight: '400px' }}
          >
            {/* Map will be rendered here */}
          </div>
        </div>

        {/* Trip Information */}
        {trackingData && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Current Status */}
            <div className="bg-white border rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">📊 Trip Status</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Status:</span>
                  <span className={`font-medium ${
                    trackingData.status === 'in_progress' ? 'text-blue-600' :
                    trackingData.status === 'completed' ? 'text-green-600' :
                    'text-gray-600'
                  }`}>
                    {trackingData.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Distance:</span>
                  <span>{trackingData.distance_covered?.toFixed(2)} / {trackingData.total_distance?.toFixed(2)} km</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">ETA:</span>
                  <span>{formatTime(trackingData.estimated_arrival)}</span>
                </div>
              </div>
            </div>

            {/* Vehicle Info */}
            <div className="bg-white border rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">🚗 Vehicle</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Vehicle ID:</span>
                  <span>#{trackingData.vehicle_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Driver ID:</span>
                  <span>#{trackingData.driver_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Speed:</span>
                  <span>{trackingData.current_location?.speed?.toFixed(1)} km/h</span>
                </div>
              </div>
            </div>

            {/* GPS Info */}
            <div className="bg-white border rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">🛰️ GPS Data</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Source:</span>
                  <span className={isLiveTracking ? 'text-green-600 font-medium' : 'text-gray-600'}>
                    {isLiveTracking ? 'Live Device GPS' : 'Simulated'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Points:</span>
                  <span>{trackingData.path_history?.length || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Last Update:</span>
                  <span>{formatTime(trackingData.current_location?.timestamp)}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-2">📱 How to use Live GPS:</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• <strong>Drivers:</strong> Click "Enable GPS" to allow location access</li>
            <li>• <strong>Drivers:</strong> Click "Start Live Tracking" to share real-time location</li>
            <li>• <strong>Admin:</strong> View all vehicle locations in real-time</li>
            <li>• <strong>Employees:</strong> Track your assigned trip progress</li>
            <li>• Location updates every 3-5 seconds when live tracking is active</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default LiveGPSMap;
