"""
HAL Transport Management System - Simplified ML Algorithms for Testing
"""

import math
import random
import numpy as np
from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple, Any

class RouteOptimizer:
    """Simplified Route Optimizer for testing"""
    
    def __init__(self):
        self.population_size = 20
        self.generations = 50
        self.mutation_rate = 0.1
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points on Earth"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def get_coordinates(self, location: str) -> Tuple[float, float]:
        """Get coordinates for common HAL locations"""
        coordinates = {
            "HAL Headquarters": (12.9716, 77.5946),
            "HAL Airport Division": (13.1986, 77.7066),
            "HAL Bangalore Complex": (12.9698, 77.7500),
            "Electronic City": (12.8456, 77.6603),
            "Whitefield": (12.9698, 77.7500),
            "Koramangala": (12.9279, 77.6271),
            "Indiranagar": (12.9784, 77.6408),
            "MG Road": (12.9759, 77.6037),
        }
        return coordinates.get(location, (12.9716, 77.5946))  # Default to HAL HQ
    
    def optimize(self, requests: List[Dict]) -> Dict[str, Any]:
        """Simplified optimization"""
        if not requests:
            return {"optimized_route": [], "total_distance": 0, "optimization_time_ms": 0}
        
        start_time = datetime.now()
        
        # Simple optimization: sort by distance from HAL HQ
        hq_lat, hq_lon = self.get_coordinates("HAL Headquarters")
        
        def distance_from_hq(request):
            origin_lat, origin_lon = self.get_coordinates(request['origin'])
            return self.haversine_distance(hq_lat, hq_lon, origin_lat, origin_lon)
        
        sorted_requests = sorted(requests, key=distance_from_hq)
        
        # Calculate total distance
        total_distance = 0
        for i, request in enumerate(sorted_requests):
            origin_lat, origin_lon = self.get_coordinates(request['origin'])
            dest_lat, dest_lon = self.get_coordinates(request['destination'])
            total_distance += self.haversine_distance(origin_lat, origin_lon, dest_lat, dest_lon)
        
        optimization_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "optimized_route": sorted_requests,
            "total_distance": round(total_distance, 2),
            "optimization_time_ms": round(optimization_time, 2),
            "fuel_estimate": round(total_distance * 0.12, 2),
            "efficiency_score": 0.85
        }

class DemandForecaster:
    """Simplified Demand Forecaster"""
    
    def forecast(self, days: int = 7) -> Dict[str, Any]:
        """Generate simplified demand forecast"""
        start_time = datetime.now()
        
        forecasts = []
        for i in range(days):
            forecast_date = date.today() + timedelta(days=i+1)
            day_of_week = forecast_date.weekday()
            
            # Simple pattern: more requests on weekdays
            base_demand = 15
            if day_of_week < 5:  # Weekdays
                base_demand += 8
            if day_of_week == 0:  # Monday
                base_demand += 3
            
            predicted_demand = base_demand + random.randint(-3, 3)
            
            forecasts.append({
                "date": forecast_date.isoformat(),
                "predicted_requests": predicted_demand,
                "confidence": 0.85,
                "trend_component": base_demand,
                "seasonal_component": 3 if day_of_week < 5 else 0,
                "peak_hours": ["09:00", "17:30"] if day_of_week < 5 else ["10:00", "16:00"]
            })
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "forecast": forecasts,
            "model_accuracy": 0.88,
            "processing_time_ms": round(processing_time, 2),
            "last_updated": datetime.now().isoformat(),
            "historical_trend": {
                "slope": 0.1,
                "recent_average": 18.5
            }
        }

class VehicleAssignmentOptimizer:
    """Simplified Vehicle Assignment Optimizer"""
    
    def __init__(self):
        self.weights = {
            "capacity_match": 0.3,
            "fuel_efficiency": 0.2,
            "vehicle_type": 0.2,
            "maintenance_status": 0.15,
            "driver_rating": 0.15
        }
    
    def calculate_assignment_score(self, request: Dict, vehicle: Dict, driver: Dict = None) -> Dict[str, Any]:
        """Calculate simplified assignment score"""
        scores = {}
        
        # Capacity matching
        passenger_count = request.get('passenger_count', 1)
        vehicle_capacity = vehicle.get('capacity', 4)
        scores['capacity_match'] = min(1.0, vehicle_capacity / max(1, passenger_count))
        
        # Fuel efficiency
        fuel_type = vehicle.get('fuel_type', 'petrol')
        fuel_scores = {'electric': 1.0, 'hybrid': 0.9, 'cng': 0.8, 'diesel': 0.7, 'petrol': 0.6}
        scores['fuel_efficiency'] = fuel_scores.get(fuel_type, 0.6)
        
        # Vehicle type
        scores['vehicle_type'] = 0.8
        
        # Maintenance status
        scores['maintenance_status'] = 0.9 if vehicle.get('status') == 'available' else 0.0
        
        # Driver rating
        if driver:
            scores['driver_rating'] = min(1.0, driver.get('rating', 3.0) / 5.0)
        else:
            scores['driver_rating'] = 0.5
        
        # Calculate weighted total
        total_score = sum(scores[key] * self.weights[key] for key in scores)
        
        return {
            "total_score": round(total_score, 3),
            "component_scores": scores,
            "recommendation_reason": f"Score: {total_score:.2f} - Good match"
        }
    
    def optimize_assignments(self, requests: List[Dict], vehicles: List[Dict], drivers: List[Dict] = None) -> List[Dict]:
        """Simplified assignment optimization"""
        if not drivers:
            drivers = [None] * len(vehicles)
        
        assignments = []
        used_vehicles = set()
        
        for request in requests:
            best_assignment = None
            best_score = 0
            
            for i, vehicle in enumerate(vehicles):
                if vehicle['id'] in used_vehicles:
                    continue
                
                driver = drivers[i] if i < len(drivers) else None
                score_result = self.calculate_assignment_score(request, vehicle, driver)
                
                if score_result['total_score'] > best_score:
                    best_score = score_result['total_score']
                    best_assignment = {
                        "request_id": request.get('id'),
                        "vehicle_id": vehicle['id'],
                        "driver_id": driver.get('id') if driver else None,
                        "assignment_score": score_result['total_score'],
                        "recommendation_reason": score_result['recommendation_reason']
                    }
            
            if best_assignment:
                assignments.append(best_assignment)
                used_vehicles.add(best_assignment['vehicle_id'])
        
        return assignments

# Initialize simplified ML components
route_optimizer = RouteOptimizer()
demand_forecaster = DemandForecaster()
assignment_optimizer = VehicleAssignmentOptimizer()

print("✅ Simplified ML algorithms initialized successfully!")
