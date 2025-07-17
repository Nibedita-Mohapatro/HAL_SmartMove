"""
GPS Tracking Service for HAL Transport Management System
Provides real-time location tracking for vehicles and trips
"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class GPSTracker:
    def __init__(self):
        self.active_trips = {}  # trip_id -> tracking_data
        self.vehicle_locations = {}  # vehicle_id -> location_data
        self.tracking_enabled = True
        
    def start_trip_tracking(self, trip_id: int, vehicle_id: int, driver_id: int, route: dict):
        """Start GPS tracking for a trip"""
        tracking_data = {
            "trip_id": trip_id,
            "vehicle_id": vehicle_id,
            "driver_id": driver_id,
            "route": route,
            "start_time": datetime.now().isoformat(),
            "status": "in_progress",
            "current_location": {
                "latitude": route["origin"]["lat"],
                "longitude": route["origin"]["lng"],
                "timestamp": datetime.now().isoformat(),
                "speed": 0,
                "heading": 0
            },
            "path_history": [],
            "estimated_arrival": self._calculate_eta(route),
            "distance_covered": 0,
            "total_distance": route.get("distance_km", 10)
        }
        
        self.active_trips[trip_id] = tracking_data
        logger.info(f"Started GPS tracking for trip {trip_id}")
        return tracking_data
    
    def update_location(self, trip_id: int, latitude: float, longitude: float, speed: float = 0, heading: float = 0):
        """Update current location for a trip"""
        if trip_id not in self.active_trips:
            return None
            
        tracking_data = self.active_trips[trip_id]
        
        # Add current location to history
        tracking_data["path_history"].append(tracking_data["current_location"].copy())
        
        # Update current location
        tracking_data["current_location"] = {
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.now().isoformat(),
            "speed": speed,
            "heading": heading
        }
        
        # Update distance covered (simplified calculation)
        if tracking_data["path_history"]:
            last_location = tracking_data["path_history"][-1]
            distance_increment = self._calculate_distance(
                last_location["latitude"], last_location["longitude"],
                latitude, longitude
            )
            tracking_data["distance_covered"] += distance_increment
        
        # Update ETA based on current progress
        progress = tracking_data["distance_covered"] / tracking_data["total_distance"]
        if progress > 0:
            elapsed_time = (datetime.now() - datetime.fromisoformat(tracking_data["start_time"])).total_seconds()
            estimated_total_time = elapsed_time / progress
            remaining_time = estimated_total_time - elapsed_time
            tracking_data["estimated_arrival"] = (datetime.now() + timedelta(seconds=remaining_time)).isoformat()
        
        logger.debug(f"Updated location for trip {trip_id}: {latitude}, {longitude}")
        return tracking_data
    
    def simulate_trip_progress(self, trip_id: int):
        """Simulate GPS movement for testing purposes"""
        if trip_id not in self.active_trips:
            return None
            
        tracking_data = self.active_trips[trip_id]
        route = tracking_data["route"]
        
        # Simulate movement from origin to destination
        origin_lat = route["origin"]["lat"]
        origin_lng = route["origin"]["lng"]
        dest_lat = route["destination"]["lat"]
        dest_lng = route["destination"]["lng"]
        
        # Calculate progress (0 to 1)
        elapsed_time = (datetime.now() - datetime.fromisoformat(tracking_data["start_time"])).total_seconds()
        total_trip_time = 30 * 60  # 30 minutes for demo
        progress = min(elapsed_time / total_trip_time, 1.0)
        
        # Interpolate position
        current_lat = origin_lat + (dest_lat - origin_lat) * progress
        current_lng = origin_lng + (dest_lng - origin_lng) * progress
        
        # Add some random variation for realism
        current_lat += random.uniform(-0.001, 0.001)
        current_lng += random.uniform(-0.001, 0.001)
        
        # Simulate speed (30-60 km/h)
        speed = random.uniform(30, 60)
        heading = self._calculate_bearing(origin_lat, origin_lng, dest_lat, dest_lng)
        
        return self.update_location(trip_id, current_lat, current_lng, speed, heading)
    
    def complete_trip(self, trip_id: int):
        """Complete GPS tracking for a trip"""
        if trip_id in self.active_trips:
            tracking_data = self.active_trips[trip_id]
            tracking_data["status"] = "completed"
            tracking_data["end_time"] = datetime.now().isoformat()
            
            # Move to completed trips (could be stored in database)
            completed_data = self.active_trips.pop(trip_id)
            logger.info(f"Completed GPS tracking for trip {trip_id}")
            return completed_data
        return None
    
    def get_trip_tracking(self, trip_id: int) -> Optional[dict]:
        """Get current tracking data for a trip"""
        return self.active_trips.get(trip_id)
    
    def get_all_active_trips(self) -> Dict[int, dict]:
        """Get tracking data for all active trips"""
        return self.active_trips.copy()
    
    def get_vehicle_location(self, vehicle_id: int) -> Optional[dict]:
        """Get current location of a vehicle"""
        # Find vehicle in active trips
        for trip_data in self.active_trips.values():
            if trip_data["vehicle_id"] == vehicle_id:
                return {
                    "vehicle_id": vehicle_id,
                    "location": trip_data["current_location"],
                    "trip_id": trip_data["trip_id"],
                    "status": trip_data["status"]
                }
        
        # Return last known location if not in active trip
        return self.vehicle_locations.get(vehicle_id)
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points (simplified)"""
        # Simplified distance calculation for demo
        return ((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2) ** 0.5 * 111  # Rough km conversion
    
    def _calculate_bearing(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate bearing between two points"""
        import math
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lng_diff_rad = math.radians(lng2 - lng1)
        
        y = math.sin(lng_diff_rad) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lng_diff_rad)
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = math.degrees(bearing_rad)
        
        return (bearing_deg + 360) % 360
    
    def _calculate_eta(self, route: dict) -> str:
        """Calculate estimated time of arrival"""
        # Simple ETA calculation for demo
        distance = route.get("distance_km", 10)
        average_speed = 40  # km/h
        eta_hours = distance / average_speed
        eta_time = datetime.now() + timedelta(hours=eta_hours)
        return eta_time.isoformat()

# Global GPS tracker instance
gps_tracker = GPSTracker()

# Demo locations for Indian cities
DEMO_LOCATIONS = {
    "HAL Bangalore": {"lat": 12.9716, "lng": 77.5946},
    "Bangalore Airport": {"lat": 13.1986, "lng": 77.7066},
    "Electronic City": {"lat": 12.8456, "lng": 77.6603},
    "Whitefield": {"lat": 12.9698, "lng": 77.7500},
    "Koramangala": {"lat": 12.9279, "lng": 77.6271},
    "Indiranagar": {"lat": 12.9784, "lng": 77.6408},
    "MG Road": {"lat": 12.9759, "lng": 77.6037},
    "Hebbal": {"lat": 13.0358, "lng": 77.5970}
}

def get_demo_route(origin: str, destination: str) -> dict:
    """Get demo route data"""
    origin_coords = DEMO_LOCATIONS.get(origin, DEMO_LOCATIONS["HAL Bangalore"])
    dest_coords = DEMO_LOCATIONS.get(destination, DEMO_LOCATIONS["Bangalore Airport"])
    
    return {
        "origin": origin_coords,
        "destination": dest_coords,
        "distance_km": random.uniform(5, 25),
        "estimated_duration_minutes": random.uniform(15, 45)
    }

async def simulate_all_trips():
    """Background task to simulate GPS updates for all active trips"""
    while True:
        try:
            for trip_id in list(gps_tracker.active_trips.keys()):
                gps_tracker.simulate_trip_progress(trip_id)
            await asyncio.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Error in GPS simulation: {e}")
            await asyncio.sleep(10)
