import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Professional car icon with direction and animation
const createCarIcon = (direction = 0, isMoving = false) => {
  return L.divIcon({
    className: 'car-marker',
    html: `
      <div style="
        width: 50px;
        height: 50px;
        position: relative;
        transform: rotate(${direction}deg);
        transition: transform 0.5s ease;
      ">
        <div style="
          width: 40px;
          height: 40px;
          background: linear-gradient(135deg, #1E40AF, #1E3A8A);
          border-radius: 8px;
          border: 3px solid white;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 12px rgba(0,0,0,0.4);
          position: relative;
          ${isMoving ? 'animation: carPulse 2s infinite;' : ''}
        ">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
            <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.22.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
          </svg>
          ${isMoving ? '<div style="position: absolute; top: -3px; right: -3px; width: 14px; height: 14px; background: #00FF88; border: 2px solid white; border-radius: 50%; animation: pulse 1.5s infinite;"></div>' : ''}
        </div>
        <div style="
          position: absolute;
          top: -8px;
          left: 50%;
          transform: translateX(-50%);
          width: 0;
          height: 0;
          border-left: 6px solid transparent;
          border-right: 6px solid transparent;
          border-bottom: 12px solid #1E40AF;
        "></div>
      </div>
    `,
    iconSize: [50, 50],
    iconAnchor: [25, 25]
  });
};

// Professional Uber-like custom icons
const createProfessionalIcon = (type, isActive = false) => {
  const configs = {
    vehicle: {
      color: isActive ? '#00D4AA' : '#1E40AF',
      size: 40,
      html: `
        <div style="
          background: linear-gradient(135deg, ${isActive ? '#00D4AA' : '#1E40AF'}, ${isActive ? '#00B894' : '#1E3A8A'});
          width: 40px;
          height: 40px;
          border-radius: 50%;
          border: 3px solid white;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
          position: relative;
        ">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
            <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.22.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
          </svg>
          ${isActive ? '<div style="position: absolute; top: -2px; right: -2px; width: 12px; height: 12px; background: #00FF88; border: 2px solid white; border-radius: 50%;"></div>' : ''}
        </div>
      `
    },
    origin: {
      color: '#10B981',
      size: 35,
      html: `
        <div style="
          background: linear-gradient(135deg, #10B981, #059669);
          width: 35px;
          height: 35px;
          border-radius: 50%;
          border: 3px solid white;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
          font-weight: bold;
          color: white;
          font-size: 14px;
        ">A</div>
        <div style="
          position: absolute;
          top: 35px;
          left: 50%;
          transform: translateX(-50%);
          width: 0;
          height: 0;
          border-left: 8px solid transparent;
          border-right: 8px solid transparent;
          border-top: 12px solid #10B981;
        "></div>
      `
    },
    destination: {
      color: '#EF4444',
      size: 35,
      html: `
        <div style="
          background: linear-gradient(135deg, #EF4444, #DC2626);
          width: 35px;
          height: 35px;
          border-radius: 50%;
          border: 3px solid white;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
          font-weight: bold;
          color: white;
          font-size: 14px;
        ">B</div>
        <div style="
          position: absolute;
          top: 35px;
          left: 50%;
          transform: translateX(-50%);
          width: 0;
          height: 0;
          border-left: 8px solid transparent;
          border-right: 8px solid transparent;
          border-top: 12px solid #EF4444;
        "></div>
      `
    },
    driver: {
      color: '#8B5CF6',
      size: 32,
      html: `
        <div style="
          background: linear-gradient(135deg, #8B5CF6, #7C3AED);
          width: 32px;
          height: 32px;
          border-radius: 50%;
          border: 2px solid white;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 3px 8px rgba(139, 92, 246, 0.4);
        ">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
        </div>
      `
    },
    currentLocation: {
      color: '#3B82F6',
      size: 20,
      html: `
        <div style="
          background: #3B82F6;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 4px solid white;
          box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3);
          animation: pulse 2s infinite;
        "></div>
      `
    }
  };

  const config = configs[type];
  return L.divIcon({
    className: 'professional-marker',
    html: config.html,
    iconSize: [config.size, config.size],
    iconAnchor: [config.size / 2, config.size / 2]
  });
};

// Professional icons for different elements
const icons = {
  vehicle: createProfessionalIcon('vehicle', true),
  vehicleInactive: createProfessionalIcon('vehicle', false),
  origin: createProfessionalIcon('origin'),
  destination: createProfessionalIcon('destination'),
  driver: createProfessionalIcon('driver'),
  currentLocation: createProfessionalIcon('currentLocation')
};

// Component to update map view
const MapUpdater = ({ center, zoom }) => {
  const map = useMap();
  
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || 13);
    }
  }, [center, zoom, map]);
  
  return null;
};

const OpenStreetMapTracker = ({
  tripId,
  userRole,
  onClose,
  initialCenter = [12.9716, 77.5946], // Bangalore coordinates
  initialZoom = 13
}) => {
  const [mapData, setMapData] = useState({
    vehicleLocation: null,
    previousLocation: null,
    route: [],
    traveledPath: [],
    origin: null,
    destination: null,
    driverInfo: null,
    tripInfo: null,
    direction: 0,
    isMoving: false,
    estimatedArrival: null,
    distanceRemaining: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isTracking, setIsTracking] = useState(false);
  const [autoZoom, setAutoZoom] = useState(true);
  const intervalRef = useRef(null);
  const mapRef = useRef(null);
  const vehicleMarkerRef = useRef(null);

  // Calculate direction between two points
  const calculateDirection = (from, to) => {
    const lat1 = from[0] * Math.PI / 180;
    const lat2 = to[0] * Math.PI / 180;
    const deltaLng = (to[1] - from[1]) * Math.PI / 180;

    const y = Math.sin(deltaLng) * Math.cos(lat2);
    const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(deltaLng);

    const bearing = Math.atan2(y, x) * 180 / Math.PI;
    return (bearing + 360) % 360; // Normalize to 0-360
  };

  // Calculate distance between two points (Haversine formula)
  const calculateDistance = (from, to) => {
    const R = 6371; // Earth's radius in km
    const lat1 = from[0] * Math.PI / 180;
    const lat2 = to[0] * Math.PI / 180;
    const deltaLat = (to[0] - from[0]) * Math.PI / 180;
    const deltaLng = (to[1] - from[1]) * Math.PI / 180;

    const a = Math.sin(deltaLat/2) * Math.sin(deltaLat/2) +
              Math.cos(lat1) * Math.cos(lat2) *
              Math.sin(deltaLng/2) * Math.sin(deltaLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c; // Distance in km
  };

  // Auto-zoom to fit route and vehicle
  const autoZoomToTrip = (map, vehicleLocation, origin, destination) => {
    if (!autoZoom || !map) return;

    const bounds = L.latLngBounds();

    if (vehicleLocation) bounds.extend(vehicleLocation);
    if (origin) bounds.extend(origin);
    if (destination) bounds.extend(destination);

    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  };

  // Fetch trip data with enhanced tracking
  const fetchTripData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/gps/trip/${tripId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();

        // Parse location data
        const newVehicleLocation = data.current_location ? [
          data.current_location.latitude,
          data.current_location.longitude
        ] : null;

        const origin = data.origin_coordinates ? [
          data.origin_coordinates.latitude,
          data.origin_coordinates.longitude
        ] : [12.9716, 77.5946]; // Default to Bangalore

        const destination = data.destination_coordinates ? [
          data.destination_coordinates.latitude,
          data.destination_coordinates.longitude
        ] : [12.9716, 77.6946]; // Default destination

        const route = data.route_path || [];

        // Calculate direction and movement
        let direction = 0;
        let isMoving = false;
        let traveledPath = mapData.traveledPath || [];

        if (newVehicleLocation && mapData.vehicleLocation) {
          const distance = calculateDistance(mapData.vehicleLocation, newVehicleLocation);
          isMoving = distance > 0.01; // Moving if more than 10 meters

          if (isMoving) {
            direction = calculateDirection(mapData.vehicleLocation, newVehicleLocation);
            traveledPath = [...traveledPath, newVehicleLocation];

            // Keep only last 50 points to avoid memory issues
            if (traveledPath.length > 50) {
              traveledPath = traveledPath.slice(-50);
            }
          }
        }

        // Calculate distance to destination
        let distanceRemaining = null;
        let estimatedArrival = null;

        if (newVehicleLocation && destination) {
          distanceRemaining = calculateDistance(newVehicleLocation, destination);
          // Estimate arrival time (assuming 30 km/h average speed)
          const estimatedMinutes = Math.round((distanceRemaining / 30) * 60);
          estimatedArrival = new Date(Date.now() + estimatedMinutes * 60000);
        }

        setMapData(prevData => ({
          ...prevData,
          vehicleLocation: newVehicleLocation,
          previousLocation: prevData.vehicleLocation,
          route,
          traveledPath,
          origin,
          destination,
          driverInfo: data.driver_info,
          tripInfo: data.trip_info,
          direction,
          isMoving,
          distanceRemaining,
          estimatedArrival
        }));

        // Auto-zoom to show the trip
        if (mapRef.current && newVehicleLocation) {
          autoZoomToTrip(mapRef.current, newVehicleLocation, origin, destination);
        }

        setError('');
      } else {
        setError('Failed to fetch trip data');
      }
    } catch (error) {
      console.error('Error fetching trip data:', error);
      setError('Network error while fetching trip data');
    } finally {
      setLoading(false);
    }
  };

  // Start real-time tracking
  const startTracking = () => {
    setIsTracking(true);
    intervalRef.current = setInterval(fetchTripData, 5000); // Update every 5 seconds
  };

  // Stop tracking
  const stopTracking = () => {
    setIsTracking(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  useEffect(() => {
    fetchTripData();
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [tripId]);

  // Calculate map center based on available data
  const getMapCenter = () => {
    if (mapData.vehicleLocation) {
      return mapData.vehicleLocation;
    }
    if (mapData.origin) {
      return mapData.origin;
    }
    return initialCenter;
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span>Loading map data...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg w-11/12 h-5/6 max-w-6xl">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b">
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              🗺️ Live GPS Tracking - Trip #{tripId}
            </h2>
            {mapData.tripInfo && (
              <p className="text-sm text-gray-600">
                {mapData.tripInfo.origin} → {mapData.tripInfo.destination}
              </p>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={isTracking ? stopTracking : startTracking}
              className={`px-4 py-2 rounded text-sm font-medium ${
                isTracking 
                  ? 'bg-red-600 hover:bg-red-700 text-white' 
                  : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
            >
              {isTracking ? '⏸️ Stop Tracking' : '▶️ Start Tracking'}
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-50 border-l-4 border-red-400">
            <div className="text-red-700">
              <span className="font-medium">Error:</span> {error}
            </div>
          </div>
        )}

        {/* Map Container */}
        <div className="h-full p-4">
          <div className="h-full rounded-lg overflow-hidden border">
            <MapContainer
              center={getMapCenter()}
              zoom={initialZoom}
              style={{ height: '100%', width: '100%' }}
              className="z-10"
              ref={mapRef}
            >
              <MapUpdater center={autoZoom ? null : getMapCenter()} zoom={autoZoom ? null : initialZoom} />

              {/* OpenStreetMap Tile Layer */}
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              {/* Origin Marker */}
              {mapData.origin && (
                <Marker position={mapData.origin} icon={icons.origin}>
                  <Popup>
                    <div className="text-center">
                      <strong>🏁 Starting Point</strong>
                      <br />
                      {mapData.tripInfo?.origin || 'Origin'}
                      <br />
                      <small className="text-gray-500">Trip begins here</small>
                    </div>
                  </Popup>
                </Marker>
              )}

              {/* Destination Marker */}
              {mapData.destination && (
                <Marker position={mapData.destination} icon={icons.destination}>
                  <Popup>
                    <div className="text-center">
                      <strong>🎯 Destination</strong>
                      <br />
                      {mapData.tripInfo?.destination || 'End Point'}
                      {mapData.distanceRemaining && (
                        <>
                          <br />
                          <small className="text-blue-600">
                            {mapData.distanceRemaining.toFixed(1)} km remaining
                          </small>
                        </>
                      )}
                      {mapData.estimatedArrival && (
                        <>
                          <br />
                          <small className="text-green-600">
                            ETA: {mapData.estimatedArrival.toLocaleTimeString()}
                          </small>
                        </>
                      )}
                    </div>
                  </Popup>
                </Marker>
              )}

              {/* Vehicle Location with Professional Car Icon */}
              {mapData.vehicleLocation && (
                <Marker
                  position={mapData.vehicleLocation}
                  icon={createCarIcon(mapData.direction, mapData.isMoving)}
                  ref={vehicleMarkerRef}
                >
                  <Popup>
                    <div className="text-center">
                      <strong>🚗 Live Vehicle Location</strong>
                      {mapData.driverInfo && (
                        <>
                          <br />
                          <span className="font-medium">Driver:</span> {mapData.driverInfo.name}
                          <br />
                          <span className="font-medium">Vehicle:</span> {mapData.driverInfo.vehicle}
                        </>
                      )}
                      <br />
                      <div className="mt-2 p-2 bg-gray-50 rounded">
                        <div className="text-xs text-gray-600">
                          Status: <span className={`font-medium ${mapData.isMoving ? 'text-green-600' : 'text-orange-600'}`}>
                            {mapData.isMoving ? '🟢 Moving' : '🟡 Stopped'}
                          </span>
                        </div>
                        {mapData.distanceRemaining && (
                          <div className="text-xs text-blue-600">
                            Distance to destination: {mapData.distanceRemaining.toFixed(1)} km
                          </div>
                        )}
                        <div className="text-xs text-gray-500 mt-1">
                          Last updated: {new Date().toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              )}

              {/* Planned Route Path */}
              {mapData.route.length > 0 && (
                <Polyline
                  positions={mapData.route}
                  color="#3B82F6"
                  weight={4}
                  opacity={0.5}
                  dashArray="10, 10"
                />
              )}

              {/* Traveled Path (Real-time tracking) */}
              {mapData.traveledPath.length > 1 && (
                <Polyline
                  positions={mapData.traveledPath}
                  color="#10B981"
                  weight={6}
                  opacity={0.8}
                  className="animated-route"
                />
              )}

              {/* Direct line from vehicle to destination */}
              {mapData.vehicleLocation && mapData.destination && (
                <Polyline
                  positions={[mapData.vehicleLocation, mapData.destination]}
                  color="#EF4444"
                  weight={2}
                  opacity={0.4}
                  dashArray="5, 10"
                />
              )}
            </MapContainer>
          </div>
        </div>

        {/* Enhanced Status Bar */}
        <div className="p-4 border-t bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            {/* Tracking Status */}
            <div className="flex items-center space-x-4">
              <span className={`flex items-center ${isTracking ? 'text-green-600' : 'text-gray-500'}`}>
                <div className={`w-3 h-3 rounded-full mr-2 ${isTracking ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
                {isTracking ? 'Live Tracking Active' : 'Tracking Stopped'}
              </span>
              {mapData.vehicleLocation && (
                <span className={`flex items-center ${mapData.isMoving ? 'text-green-600' : 'text-orange-600'}`}>
                  <div className={`w-2 h-2 rounded-full mr-1 ${mapData.isMoving ? 'bg-green-500' : 'bg-orange-500'}`}></div>
                  {mapData.isMoving ? 'Moving' : 'Stopped'}
                </span>
              )}
            </div>

            {/* Trip Information */}
            <div className="flex items-center justify-center space-x-4">
              {mapData.distanceRemaining && (
                <span className="text-blue-600">
                  📍 {mapData.distanceRemaining.toFixed(1)} km remaining
                </span>
              )}
              {mapData.estimatedArrival && (
                <span className="text-green-600">
                  ⏰ ETA: {mapData.estimatedArrival.toLocaleTimeString()}
                </span>
              )}
            </div>

            {/* Controls */}
            <div className="flex items-center justify-end space-x-2">
              <button
                onClick={() => setAutoZoom(!autoZoom)}
                className={`px-3 py-1 rounded text-xs font-medium ${
                  autoZoom
                    ? 'bg-blue-100 text-blue-700 border border-blue-300'
                    : 'bg-gray-100 text-gray-600 border border-gray-300'
                }`}
                title="Toggle auto-zoom"
              >
                {autoZoom ? '🔍 Auto-Zoom ON' : '🔍 Auto-Zoom OFF'}
              </button>
              <span className="text-gray-500 text-xs">
                OpenStreetMap • Free & Secure
              </span>
            </div>
          </div>

          {/* Trip Progress Bar */}
          {mapData.origin && mapData.destination && mapData.vehicleLocation && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>Trip Progress</span>
                <span>
                  {mapData.distanceRemaining ?
                    `${((1 - mapData.distanceRemaining / calculateDistance(mapData.origin, mapData.destination)) * 100).toFixed(0)}% Complete` :
                    'Calculating...'
                  }
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full transition-all duration-500"
                  style={{
                    width: mapData.distanceRemaining ?
                      `${Math.max(5, (1 - mapData.distanceRemaining / calculateDistance(mapData.origin, mapData.destination)) * 100)}%` :
                      '0%'
                  }}
                ></div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OpenStreetMapTracker;
