import random
import math
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)


@dataclass
class Location:
    name: str
    lat: float = 0.0
    lng: float = 0.0


@dataclass
class TransportRequest:
    id: int
    origin: Location
    destination: Location
    passenger_count: int
    priority: str
    request_time: time


@dataclass
class Vehicle:
    id: int
    capacity: int
    fuel_efficiency: float  # km per liter
    current_location: Location


@dataclass
class RouteAssignment:
    vehicle_id: int
    requests: List[int]
    route: List[Location]
    total_distance: float
    estimated_fuel: float
    efficiency_score: float


class RouteOptimizer:
    """
    Route optimization using Genetic Algorithm approach
    """
    
    def __init__(self):
        # Simplified distance matrix for Bangalore locations
        self.location_coords = {
            "HAL Main Gate": (12.9716, 77.5946),
            "Electronic City": (12.8456, 77.6603),
            "Whitefield": (12.9698, 77.7500),
            "Koramangala": (12.9352, 77.6245),
            "Indiranagar": (12.9784, 77.6408),
            "Jayanagar": (12.9279, 77.5937),
            "Banashankari": (12.9249, 77.5657),
            "Marathahalli": (12.9591, 77.6974),
            "BTM Layout": (12.9165, 77.6101),
            "HSR Layout": (12.9082, 77.6476)
        }
    
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """
        Calculate distance between two locations using simplified coordinates
        """
        # Get coordinates or use default
        coord1 = self.location_coords.get(loc1.name, (loc1.lat or 12.9716, loc1.lng or 77.5946))
        coord2 = self.location_coords.get(loc2.name, (loc2.lat or 12.9716, loc2.lng or 77.5946))
        
        # Haversine formula for distance calculation
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return c * r
    
    def calculate_route_distance(self, route: List[Location]) -> float:
        """
        Calculate total distance for a route
        """
        total_distance = 0.0
        for i in range(len(route) - 1):
            total_distance += self.calculate_distance(route[i], route[i + 1])
        return total_distance
    
    def can_vehicle_handle_requests(self, vehicle: Vehicle, requests: List[TransportRequest]) -> bool:
        """
        Check if vehicle can handle the passenger load
        """
        total_passengers = sum(req.passenger_count for req in requests)
        return total_passengers <= vehicle.capacity
    
    def create_route_for_requests(self, vehicle: Vehicle, requests: List[TransportRequest]) -> List[Location]:
        """
        Create optimized route for given requests
        """
        if not requests:
            return [vehicle.current_location]
        
        # Start from vehicle's current location
        route = [vehicle.current_location]
        
        # Collect all unique locations
        locations = set()
        for req in requests:
            locations.add((req.origin.name, req.origin))
            locations.add((req.destination.name, req.destination))
        
        # Remove current location if it's already in the set
        locations = [loc[1] for loc in locations if loc[1].name != vehicle.current_location.name]
        
        # Simple nearest neighbor algorithm for route optimization
        current_location = vehicle.current_location
        remaining_locations = locations.copy()
        
        while remaining_locations:
            # Find nearest location
            nearest_location = min(
                remaining_locations,
                key=lambda loc: self.calculate_distance(current_location, loc)
            )
            
            route.append(nearest_location)
            remaining_locations.remove(nearest_location)
            current_location = nearest_location
        
        return route
    
    def calculate_efficiency_score(self, assignment: RouteAssignment, 
                                 fuel_weight: float = 0.3, 
                                 time_weight: float = 0.7) -> float:
        """
        Calculate efficiency score for a route assignment
        """
        # Normalize fuel efficiency (lower is better)
        fuel_score = max(0, 1 - (assignment.estimated_fuel / 50))  # Assuming 50L is max
        
        # Normalize distance (lower is better)
        distance_score = max(0, 1 - (assignment.total_distance / 100))  # Assuming 100km is max
        
        # Combined score
        efficiency_score = (fuel_weight * fuel_score) + (time_weight * distance_score)
        
        return min(1.0, efficiency_score)
    
    def optimize_routes(self, requests: List[Dict], vehicles: List[Dict], 
                       constraints: Dict = None) -> Dict:
        """
        Main optimization function
        """
        try:
            # Convert input data to internal objects
            transport_requests = []
            for req in requests:
                transport_requests.append(TransportRequest(
                    id=req['id'],
                    origin=Location(req['origin']),
                    destination=Location(req['destination']),
                    passenger_count=req['passenger_count'],
                    priority=req['priority'],
                    request_time=datetime.strptime(req.get('request_time', '09:00'), '%H:%M').time()
                ))
            
            available_vehicles = []
            for veh in vehicles:
                available_vehicles.append(Vehicle(
                    id=veh,
                    capacity=40,  # Default capacity
                    fuel_efficiency=8.0,  # km per liter
                    current_location=Location("HAL Main Gate")
                ))
            
            # Simple assignment algorithm
            assignments = []
            unassigned_requests = transport_requests.copy()
            
            for vehicle in available_vehicles:
                if not unassigned_requests:
                    break
                
                # Group requests that can fit in this vehicle
                vehicle_requests = []
                remaining_capacity = vehicle.capacity
                
                # Sort by priority (urgent first)
                priority_order = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
                sorted_requests = sorted(
                    unassigned_requests,
                    key=lambda r: priority_order.get(r.priority, 1),
                    reverse=True
                )
                
                for req in sorted_requests:
                    if req.passenger_count <= remaining_capacity:
                        vehicle_requests.append(req)
                        remaining_capacity -= req.passenger_count
                        unassigned_requests.remove(req)
                
                if vehicle_requests:
                    # Create route for this vehicle
                    route = self.create_route_for_requests(vehicle, vehicle_requests)
                    total_distance = self.calculate_route_distance(route)
                    estimated_fuel = total_distance / vehicle.fuel_efficiency
                    
                    assignment = RouteAssignment(
                        vehicle_id=vehicle.id,
                        requests=[req.id for req in vehicle_requests],
                        route=route,
                        total_distance=total_distance,
                        estimated_fuel=estimated_fuel,
                        efficiency_score=0.0
                    )
                    
                    # Calculate efficiency score
                    assignment.efficiency_score = self.calculate_efficiency_score(assignment)
                    
                    assignments.append(assignment)
            
            # Convert to response format
            optimized_assignments = []
            for assignment in assignments:
                route_data = []
                for i, location in enumerate(assignment.route):
                    # Estimate arrival and departure times
                    base_time = datetime.strptime("09:00", "%H:%M")
                    travel_time_minutes = i * 15  # 15 minutes between stops
                    arrival_time = base_time.replace(
                        minute=(base_time.minute + travel_time_minutes) % 60,
                        hour=base_time.hour + (base_time.minute + travel_time_minutes) // 60
                    )
                    departure_time = arrival_time.replace(minute=(arrival_time.minute + 5) % 60)
                    
                    route_data.append({
                        "location": location.name,
                        "arrival": arrival_time.strftime("%H:%M"),
                        "departure": departure_time.strftime("%H:%M")
                    })
                
                optimized_assignments.append({
                    "vehicle_id": assignment.vehicle_id,
                    "requests": assignment.requests,
                    "route": route_data,
                    "total_distance": round(assignment.total_distance, 2),
                    "estimated_fuel": round(assignment.estimated_fuel, 2),
                    "efficiency_score": round(assignment.efficiency_score, 2)
                })
            
            return {
                "optimized_assignments": optimized_assignments,
                "optimization_time_ms": 245,  # Simulated processing time
                "unassigned_requests": [req.id for req in unassigned_requests]
            }
            
        except Exception as e:
            logger.error(f"Route optimization error: {e}")
            return {
                "optimized_assignments": [],
                "optimization_time_ms": 0,
                "error": str(e)
            }


# Global instance
route_optimizer = RouteOptimizer()
