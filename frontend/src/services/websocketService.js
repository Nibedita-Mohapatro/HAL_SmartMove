/**
 * WebSocket Service for Real-time Updates
 * Provides live updates for GPS tracking, notifications, and chat
 */

class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000;
    this.listeners = new Map();
    this.isConnected = false;
    this.userId = null;
    this.userRole = null;
  }

  /**
   * Connect to WebSocket server
   */
  connect(userId, userRole) {
    this.userId = userId;
    this.userRole = userRole;
    
    const token = localStorage.getItem('token');
    const wsUrl = `ws://localhost:8000/ws/${userId}?token=${token}`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers();
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.scheduleReconnect();
    }
  }

  /**
   * Setup WebSocket event handlers
   */
  setupEventHandlers() {
    this.ws.onopen = () => {
      console.log('✅ WebSocket connected');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.emit('connected', { userId: this.userId });
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.isConnected = false;
      this.emit('disconnected', { code: event.code, reason: event.reason });
      
      if (event.code !== 1000) { // Not a normal closure
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.emit('error', error);
    };
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(data) {
    const { type, payload } = data;
    
    switch (type) {
      case 'gps_update':
        this.emit('gpsUpdate', payload);
        break;
      case 'trip_status_change':
        this.emit('tripStatusChange', payload);
        break;
      case 'new_request':
        this.emit('newRequest', payload);
        break;
      case 'request_approved':
        this.emit('requestApproved', payload);
        break;
      case 'driver_assigned':
        this.emit('driverAssigned', payload);
        break;
      case 'chat_message':
        this.emit('chatMessage', payload);
        break;
      case 'notification':
        this.emit('notification', payload);
        break;
      case 'system_alert':
        this.emit('systemAlert', payload);
        break;
      default:
        console.log('Unknown message type:', type, payload);
    }
  }

  /**
   * Send message through WebSocket
   */
  send(type, payload) {
    if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({ type, payload });
      this.ws.send(message);
      return true;
    } else {
      console.warn('WebSocket not connected, message not sent:', type, payload);
      return false;
    }
  }

  /**
   * Send GPS location update
   */
  sendGPSUpdate(tripId, location) {
    return this.send('gps_update', {
      tripId,
      location,
      timestamp: new Date().toISOString(),
      userId: this.userId
    });
  }

  /**
   * Send chat message
   */
  sendChatMessage(tripId, message, recipientId) {
    return this.send('chat_message', {
      tripId,
      message,
      recipientId,
      senderId: this.userId,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Join trip room for real-time updates
   */
  joinTripRoom(tripId) {
    return this.send('join_trip', { tripId });
  }

  /**
   * Leave trip room
   */
  leaveTripRoom(tripId) {
    return this.send('leave_trip', { tripId });
  }

  /**
   * Subscribe to events
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
  }

  /**
   * Unsubscribe from events
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }

  /**
   * Emit event to listeners
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in ${event} listener:`, error);
        }
      });
    }
  }

  /**
   * Schedule reconnection attempt
   */
  scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      
      setTimeout(() => {
        if (!this.isConnected) {
          this.connect(this.userId, this.userRole);
        }
      }, this.reconnectInterval * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
    }
  }

  /**
   * Disconnect WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'User disconnected');
      this.ws = null;
    }
    this.isConnected = false;
    this.listeners.clear();
  }

  /**
   * Get connection status
   */
  getStatus() {
    return {
      isConnected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      userId: this.userId,
      userRole: this.userRole
    };
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;
