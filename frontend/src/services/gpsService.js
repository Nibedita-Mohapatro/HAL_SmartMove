/**
 * Real GPS Service for HAL Transport Management System
 * Handles device location permissions and real-time GPS tracking
 */

class GPSService {
  constructor() {
    this.watchId = null;
    this.isTracking = false;
    this.currentPosition = null;
    this.locationHistory = [];
    this.callbacks = new Set();
    this.permissionStatus = 'unknown'; // 'granted', 'denied', 'prompt', 'unknown'
  }

  /**
   * Request location permission from user
   */
  async requestLocationPermission() {
    try {
      // Check if geolocation is supported
      if (!navigator.geolocation) {
        throw new Error('Geolocation is not supported by this browser');
      }

      // Check current permission status
      if (navigator.permissions) {
        const permission = await navigator.permissions.query({ name: 'geolocation' });
        this.permissionStatus = permission.state;
        
        // Listen for permission changes
        permission.onchange = () => {
          this.permissionStatus = permission.state;
          if (permission.state === 'denied') {
            this.stopTracking();
          }
        };
      }

      // Request location with high accuracy
      return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            this.permissionStatus = 'granted';
            this.currentPosition = {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
              accuracy: position.coords.accuracy,
              timestamp: new Date().toISOString(),
              speed: position.coords.speed || 0,
              heading: position.coords.heading || 0
            };
            resolve(this.currentPosition);
          },
          (error) => {
            this.permissionStatus = 'denied';
            reject(this.handleLocationError(error));
          },
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
          }
        );
      });
    } catch (error) {
      console.error('Error requesting location permission:', error);
      throw error;
    }
  }

  /**
   * Start real-time GPS tracking
   */
  async startTracking(tripId, updateCallback) {
    try {
      if (this.isTracking) {
        console.warn('GPS tracking is already active');
        return;
      }

      // Request permission first
      await this.requestLocationPermission();

      this.isTracking = true;
      this.tripId = tripId;
      
      if (updateCallback) {
        this.callbacks.add(updateCallback);
      }

      // Start watching position with high accuracy
      this.watchId = navigator.geolocation.watchPosition(
        (position) => {
          const locationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date().toISOString(),
            speed: position.coords.speed || 0,
            heading: position.coords.heading || 0,
            altitude: position.coords.altitude,
            altitudeAccuracy: position.coords.altitudeAccuracy
          };

          this.currentPosition = locationData;
          this.locationHistory.push(locationData);

          // Keep only last 100 positions to prevent memory issues
          if (this.locationHistory.length > 100) {
            this.locationHistory = this.locationHistory.slice(-100);
          }

          // Notify all callbacks
          this.callbacks.forEach(callback => {
            try {
              callback(locationData);
            } catch (error) {
              console.error('Error in GPS callback:', error);
            }
          });

          // Send to backend
          this.sendLocationToBackend(tripId, locationData);
        },
        (error) => {
          console.error('GPS tracking error:', this.handleLocationError(error));
          this.notifyError(this.handleLocationError(error));
        },
        {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 1000 // Accept 1-second old positions
        }
      );

      console.log('GPS tracking started for trip:', tripId);
      return true;
    } catch (error) {
      console.error('Failed to start GPS tracking:', error);
      this.isTracking = false;
      throw error;
    }
  }

  /**
   * Stop GPS tracking
   */
  stopTracking() {
    if (this.watchId !== null) {
      navigator.geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }
    
    this.isTracking = false;
    this.callbacks.clear();
    console.log('GPS tracking stopped');
  }

  /**
   * Send location update to backend
   */
  async sendLocationToBackend(tripId, locationData) {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      await fetch(`http://localhost:8000/api/v1/gps/update-location/${tripId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          latitude: locationData.latitude,
          longitude: locationData.longitude,
          speed: locationData.speed,
          heading: locationData.heading,
          accuracy: locationData.accuracy,
          timestamp: locationData.timestamp
        })
      });
    } catch (error) {
      console.error('Failed to send location to backend:', error);
    }
  }

  /**
   * Get current location once
   */
  async getCurrentLocation() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation not supported'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const locationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date().toISOString(),
            speed: position.coords.speed || 0,
            heading: position.coords.heading || 0
          };
          resolve(locationData);
        },
        (error) => reject(this.handleLocationError(error)),
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000
        }
      );
    });
  }

  /**
   * Handle geolocation errors
   */
  handleLocationError(error) {
    switch (error.code) {
      case error.PERMISSION_DENIED:
        return new Error('Location access denied by user. Please enable location permissions in your browser settings.');
      case error.POSITION_UNAVAILABLE:
        return new Error('Location information is unavailable. Please check your GPS/network connection.');
      case error.TIMEOUT:
        return new Error('Location request timed out. Please try again.');
      default:
        return new Error('An unknown error occurred while retrieving location.');
    }
  }

  /**
   * Notify callbacks about errors
   */
  notifyError(error) {
    this.callbacks.forEach(callback => {
      try {
        if (callback.onError) {
          callback.onError(error);
        }
      } catch (err) {
        console.error('Error in GPS error callback:', err);
      }
    });
  }

  /**
   * Calculate distance between two points (Haversine formula)
   */
  calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in kilometers
    const dLat = this.toRadians(lat2 - lat1);
    const dLon = this.toRadians(lon2 - lon1);
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }

  /**
   * Convert degrees to radians
   */
  toRadians(degrees) {
    return degrees * (Math.PI / 180);
  }

  /**
   * Calculate bearing between two points
   */
  calculateBearing(lat1, lon1, lat2, lon2) {
    const dLon = this.toRadians(lon2 - lon1);
    const lat1Rad = this.toRadians(lat1);
    const lat2Rad = this.toRadians(lat2);
    
    const y = Math.sin(dLon) * Math.cos(lat2Rad);
    const x = Math.cos(lat1Rad) * Math.sin(lat2Rad) - 
              Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLon);
    
    const bearing = Math.atan2(y, x);
    return (bearing * 180 / Math.PI + 360) % 360;
  }

  /**
   * Get tracking status
   */
  getStatus() {
    return {
      isTracking: this.isTracking,
      permissionStatus: this.permissionStatus,
      currentPosition: this.currentPosition,
      locationHistory: this.locationHistory,
      tripId: this.tripId
    };
  }

  /**
   * Add callback for location updates
   */
  addLocationCallback(callback) {
    this.callbacks.add(callback);
  }

  /**
   * Remove callback
   */
  removeLocationCallback(callback) {
    this.callbacks.delete(callback);
  }
}

// Create singleton instance
const gpsService = new GPSService();

export default gpsService;
