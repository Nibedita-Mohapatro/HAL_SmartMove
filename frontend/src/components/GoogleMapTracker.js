import React, { useState, useEffect, useRef } from 'react';
import gpsService from '../services/gpsService';

const GoogleMapTracker = ({ tripId, userRole, onClose }) => {
  const [trackingData, setTrackingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [gpsPermission, setGpsPermission] = useState('unknown');
  const [isLiveTracking, setIsLiveTracking] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef({});
  const pathRef = useRef(null);

  // Google Maps configuration
  const GOOGLE_MAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'; // Replace with your API key
  const BANGALORE_CENTER = { lat: 12.9716, lng: 77.5946 };

  useEffect(() => {
    if (!tripId) return;

    loadGoogleMaps();
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

  const loadGoogleMaps = () => {
    // Check if Google Maps is already loaded
    if (window.google && window.google.maps) {
      initializeMap();
      return;
    }

    // Load Google Maps API
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=geometry`;
    script.async = true;
    script.defer = true;
    script.onload = initializeMap;
    script.onerror = () => {
      console.error('Failed to load Google Maps');
      initializeFallbackMap();
    };
    document.head.appendChild(script);
  };

  const initializeMap = () => {
    if (!mapRef.current || mapInstanceRef.current) return;

    try {
      // Initialize Google Map
      mapInstanceRef.current = new window.google.maps.Map(mapRef.current, {
        zoom: 13,
        center: BANGALORE_CENTER,
        mapTypeId: window.google.maps.MapTypeId.ROADMAP,
        styles: [
          {
            featureType: 'poi',
            elementType: 'labels',
            stylers: [{ visibility: 'off' }]
          }
        ]
      });

      // Add traffic layer
      const trafficLayer = new window.google.maps.TrafficLayer();
      trafficLayer.setMap(mapInstanceRef.current);

    } catch (error) {
      console.error('Error initializing Google Maps:', error);
      initializeFallbackMap();
    }
  };

  const initializeFallbackMap = () => {
    if (mapRef.current && !mapInstanceRef.current) {
      mapRef.current.innerHTML = `
        <div class="w-full h-full bg-gradient-to-br from-blue-100 to-green-100 flex items-center justify-center relative overflow-hidden">
          <div class="absolute inset-0 opacity-10">
            <svg viewBox="0 0 100 100" class="w-full h-full">
              <defs>
                <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                  <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#000" stroke-width="0.5"/>
                </pattern>
              </defs>
              <rect width="100" height="100" fill="url(#grid)" />
            </svg>
          </div>
          <div class="text-center z-10">
            <div class="text-6xl mb-4">🗺️</div>
            <h3 class="text-xl font-bold text-gray-700 mb-2">Live GPS Map</h3>
            <p class="text-gray-600 mb-4">Real-time vehicle tracking</p>
            <div class="bg-white bg-opacity-80 rounded-lg p-4 max-w-sm">
              <p class="text-sm text-gray-700">
                📍 Interactive map with live GPS tracking<br/>
                🛰️ Real-time location updates<br/>
                🚗 Vehicle path visualization
              </p>
            </div>
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
    if (!mapInstanceRef.current || !window.google) return;

    try {
      // Clear existing markers and path
      Object.values(markersRef.current).forEach(marker => marker.setMap(null));
      if (pathRef.current) pathRef.current.setMap(null);

      // Add origin marker
      if (tracking.route && tracking.route.origin) {
        markersRef.current.origin = new window.google.maps.Marker({
          position: tracking.route.origin,
          map: mapInstanceRef.current,
          title: 'Origin',
          icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
              <svg width="30" height="30" viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg">
                <circle cx="15" cy="15" r="12" fill="#10B981" stroke="white" stroke-width="2"/>
                <text x="15" y="20" text-anchor="middle" fill="white" font-size="16">A</text>
              </svg>
            `),
            scaledSize: new window.google.maps.Size(30, 30)
          }
        });
      }

      // Add destination marker
      if (tracking.route && tracking.route.destination) {
        markersRef.current.destination = new window.google.maps.Marker({
          position: tracking.route.destination,
          map: mapInstanceRef.current,
          title: 'Destination',
          icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
              <svg width="30" height="30" viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg">
                <circle cx="15" cy="15" r="12" fill="#EF4444" stroke="white" stroke-width="2"/>
                <text x="15" y="20" text-anchor="middle" fill="white" font-size="16">B</text>
              </svg>
            `),
            scaledSize: new window.google.maps.Size(30, 30)
          }
        });
      }

      // Add current location marker
      if (tracking.current_location) {
        markersRef.current.current = new window.google.maps.Marker({
          position: {
            lat: tracking.current_location.latitude,
            lng: tracking.current_location.longitude
          },
          map: mapInstanceRef.current,
          title: 'Current Location',
          icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
              <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
                <circle cx="20" cy="20" r="15" fill="#3B82F6" stroke="white" stroke-width="3"/>
                <circle cx="20" cy="20" r="8" fill="white"/>
                <text x="20" y="25" text-anchor="middle" fill="#3B82F6" font-size="12">🚗</text>
              </svg>
            `),
            scaledSize: new window.google.maps.Size(40, 40)
          }
        });

        // Center map on current location
        mapInstanceRef.current.setCenter({
          lat: tracking.current_location.latitude,
          lng: tracking.current_location.longitude
        });
      }

      // Draw path if available
      if (tracking.path_history && tracking.path_history.length > 1) {
        const pathCoordinates = tracking.path_history.map(point => ({
          lat: point.latitude,
          lng: point.longitude
        }));

        pathRef.current = new window.google.maps.Polyline({
          path: pathCoordinates,
          geodesic: true,
          strokeColor: '#3B82F6',
          strokeOpacity: 0.8,
          strokeWeight: 4
        });

        pathRef.current.setMap(mapInstanceRef.current);
      }

      // Fit map to show all markers
      const bounds = new window.google.maps.LatLngBounds();
      Object.values(markersRef.current).forEach(marker => {
        bounds.extend(marker.getPosition());
      });
      if (!bounds.isEmpty()) {
        mapInstanceRef.current.fitBounds(bounds);
      }

    } catch (error) {
      console.error('Error updating map:', error);
    }
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
        updateCurrentLocationMarker(locationData);
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

  const updateCurrentLocationMarker = (location) => {
    if (!mapInstanceRef.current || !window.google) return;

    // Update current location marker
    if (markersRef.current.current) {
      markersRef.current.current.setPosition({
        lat: location.latitude,
        lng: location.longitude
      });
    }

    // Center map on new location
    mapInstanceRef.current.setCenter({
      lat: location.latitude,
      lng: location.longitude
    });
  };

  const cleanup = () => {
    Object.values(markersRef.current).forEach(marker => {
      if (marker && marker.setMap) marker.setMap(null);
    });
    markersRef.current = {};
    if (pathRef.current && pathRef.current.setMap) {
      pathRef.current.setMap(null);
    }
    pathRef.current = null;
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
      <div className="relative top-2 mx-auto p-3 border w-11/12 md:w-11/12 lg:w-11/12 shadow-lg rounded-md bg-white max-h-screen overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            🛰️ Live GPS Map - Trip #{tripId}
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

        {/* GPS Controls */}
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
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
                  className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm font-medium disabled:bg-gray-400"
                >
                  {loading ? 'Requesting...' : 'Enable GPS'}
                </button>
              )}
              {gpsPermission === 'granted' && !isLiveTracking && userRole === 'transport' && (
                <button
                  onClick={startLiveTracking}
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded text-sm font-medium disabled:bg-gray-400"
                >
                  {loading ? 'Starting...' : 'Start Live Tracking'}
                </button>
              )}
              {isLiveTracking && (
                <button
                  onClick={stopLiveTracking}
                  className="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded text-sm font-medium"
                >
                  Stop Tracking
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Live Location Status */}
        {currentLocation && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-green-900 flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-2"></div>
                  Live Location Active
                </h4>
                <p className="text-sm text-green-700">
                  {formatCoordinate(currentLocation.latitude)}, {formatCoordinate(currentLocation.longitude)}
                </p>
              </div>
              <div className="text-right text-sm text-green-600">
                <p>Speed: {currentLocation.speed?.toFixed(1)} km/h</p>
                <p>Accuracy: {currentLocation.accuracy?.toFixed(0)}m</p>
              </div>
            </div>
          </div>
        )}

        {/* Map Container */}
        <div className="mb-4">
          <div 
            ref={mapRef}
            className="w-full border border-gray-300 rounded-lg overflow-hidden"
            style={{ height: '500px' }}
          >
            {/* Google Map will be rendered here */}
          </div>
        </div>

        {/* Trip Status */}
        {trackingData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
            <div className="bg-white border rounded p-3">
              <p className="text-gray-500">Status</p>
              <p className="font-medium">{trackingData.status?.replace('_', ' ').toUpperCase()}</p>
            </div>
            <div className="bg-white border rounded p-3">
              <p className="text-gray-500">Progress</p>
              <p className="font-medium">{((trackingData.distance_covered / trackingData.total_distance) * 100).toFixed(1)}%</p>
            </div>
            <div className="bg-white border rounded p-3">
              <p className="text-gray-500">Speed</p>
              <p className="font-medium">{trackingData.current_location?.speed?.toFixed(1)} km/h</p>
            </div>
            <div className="bg-white border rounded p-3">
              <p className="text-gray-500">ETA</p>
              <p className="font-medium">{formatTime(trackingData.estimated_arrival)}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GoogleMapTracker;
