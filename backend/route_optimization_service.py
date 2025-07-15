"""
Advanced Route Optimization Service with Real Traffic Data Integration
Provides intelligent route planning with traffic-aware optimization
"""

import asyncio
import json
import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class TrafficDataProvider:
    """Simulates real traffic data integration"""
    
    def __init__(self):
        self.traffic_cache = {}
        self.cache_timeout = 300  # 5 minutes
        
    async def get_traffic_data(self, origin: str, destination: str) -> Dict:
        """Get real-time traffic data for route"""
        cache_key = f"{origin}->{destination}"
        
        # Check cache
        if cache_key in self.traffic_cache:
            cached_data = self.traffic_cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self.cache_timeout):
                return cached_data['data']
        
        # Simulate traffic API call (in production, integrate with Google Maps, HERE, etc.)
        traffic_data = await self._simulate_traffic_api(origin, destination)
        
        # Cache the result
        self.traffic_cache[cache_key] = {
            'data': traffic_data,
            'timestamp': datetime.now()
        }
        
        return traffic_data
    
    async def _simulate_traffic_api(self, origin: str, destination: str) -> Dict:
        """Simulate traffic API response with realistic data"""
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        # Generate realistic traffic data based on time of day
        current_hour = datetime.now().hour
        
        # Traffic patterns for Bangalore
        traffic_multipliers = {
            # Early morning (5-7 AM)
            5: 1.2, 6: 1.4, 7: 1.8,
            # Morning rush (8-10 AM)
            8: 2.5, 9: 2.8, 10: 2.2,
            # Midday (11 AM - 2 PM)
            11: 1.3, 12: 1.4, 13: 1.5, 14: 1.4,
            # Afternoon (3-5 PM)
            15: 1.6, 16: 1.8, 17: 2.0,
            # Evening rush (6-8 PM)
            18: 2.7, 19: 3.0, 20: 2.4,
            # Night (9 PM - 4 AM)
            21: 1.5, 22: 1.2, 23: 1.0, 0: 0.8, 1: 0.7, 2: 0.6, 3: 0.6, 4: 0.8
        }
        
        base_duration = self._calculate_base_duration(origin, destination)
        traffic_multiplier = traffic_multipliers.get(current_hour, 1.0)
        
        # Add random variation (±20%)
        variation = random.uniform(0.8, 1.2)
        actual_duration = base_duration * traffic_multiplier * variation
        
        # Traffic conditions
        if traffic_multiplier >= 2.5:
            condition = "heavy"
            color = "#FF0000"
        elif traffic_multiplier >= 1.8:
            condition = "moderate"
            color = "#FFA500"
        elif traffic_multiplier >= 1.3:
            condition = "light"
            color = "#FFFF00"
        else:
            condition = "free_flow"
            color = "#00FF00"
        
        return {
            'distance_km': self._calculate_distance(origin, destination),
            'base_duration_minutes': base_duration,
            'current_duration_minutes': int(actual_duration),
            'traffic_condition': condition,
            'traffic_color': color,
            'delay_minutes': int(actual_duration - base_duration),
            'alternative_routes': self._generate_alternative_routes(origin, destination, actual_duration),
            'incidents': self._generate_traffic_incidents(),
            'updated_at': datetime.now().isoformat()
        }
    
    def _calculate_base_duration(self, origin: str, destination: str) -> int:
        """Calculate base travel time without traffic"""
        distance = self._calculate_distance(origin, destination)
        # Average speed in Bangalore: 25 km/h
        return int((distance / 25) * 60)
    
    def _calculate_distance(self, origin: str, destination: str) -> float:
        """Calculate approximate distance between locations"""
        # Simplified distance calculation for demo
        # In production, use proper geocoding and distance APIs
        location_coords = {
            'HAL Headquarters': (12.9716, 77.5946),
            'Electronic City': (12.8456, 77.6603),
            'Whitefield': (12.9698, 77.7500),
            'Koramangala': (12.9279, 77.6271),
            'Indiranagar': (12.9784, 77.6408),
            'MG Road': (12.9759, 77.6037),
            'Airport': (13.1986, 77.7066),
            'Majestic': (12.9767, 77.5993)
        }
        
        origin_coords = location_coords.get(origin, (12.9716, 77.5946))
        dest_coords = location_coords.get(destination, (12.9716, 77.5946))
        
        # Haversine formula
        lat1, lon1 = math.radians(origin_coords[0]), math.radians(origin_coords[1])
        lat2, lon2 = math.radians(dest_coords[0]), math.radians(dest_coords[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in km
        return 6371 * c
    
    def _generate_alternative_routes(self, origin: str, destination: str, primary_duration: float) -> List[Dict]:
        """Generate alternative route options"""
        alternatives = []
        
        for i in range(2):  # Generate 2 alternatives
            # Alternative routes are typically 10-30% longer but may be faster due to traffic
            distance_factor = random.uniform(1.1, 1.3)
            time_factor = random.uniform(0.9, 1.2)
            
            alternatives.append({
                'route_id': f"alt_{i+1}",
                'name': f"Alternative Route {i+1}",
                'duration_minutes': int(primary_duration * time_factor),
                'distance_km': self._calculate_distance(origin, destination) * distance_factor,
                'traffic_condition': random.choice(['light', 'moderate', 'heavy']),
                'highlights': self._generate_route_highlights()
            })
        
        return alternatives
    
    def _generate_route_highlights(self) -> List[str]:
        """Generate route highlights/features"""
        highlights = [
            "Avoids major traffic signals",
            "Uses highway for faster travel",
            "Scenic route through parks",
            "Avoids construction zones",
            "Toll-free route",
            "Shortest distance",
            "Fewer turns and intersections"
        ]
        return random.sample(highlights, random.randint(1, 3))
    
    def _generate_traffic_incidents(self) -> List[Dict]:
        """Generate current traffic incidents"""
        incidents = []
        
        # Randomly generate incidents
        if random.random() < 0.3:  # 30% chance of incidents
            incident_types = [
                "Road construction",
                "Traffic accident",
                "Vehicle breakdown",
                "Heavy rain",
                "Festival/Event",
                "Road closure"
            ]
            
            for _ in range(random.randint(1, 2)):
                incidents.append({
                    'type': random.choice(incident_types),
                    'location': f"Near {random.choice(['Silk Board', 'Marathahalli', 'Hebbal', 'Banashankari'])}",
                    'severity': random.choice(['low', 'medium', 'high']),
                    'delay_minutes': random.randint(5, 30),
                    'description': "Traffic moving slowly due to incident"
                })
        
        return incidents

class RouteOptimizer:
    """Advanced route optimization with traffic integration"""
    
    def __init__(self):
        self.traffic_provider = TrafficDataProvider()
        
    async def optimize_single_route(self, origin: str, destination: str, 
                                  departure_time: Optional[datetime] = None) -> Dict:
        """Optimize a single route with traffic data"""
        if not departure_time:
            departure_time = datetime.now()
        
        # Get traffic data
        traffic_data = await self.traffic_provider.get_traffic_data(origin, destination)
        
        # Calculate optimal route
        optimal_route = {
            'origin': origin,
            'destination': destination,
            'departure_time': departure_time.isoformat(),
            'primary_route': {
                'distance_km': traffic_data['distance_km'],
                'estimated_duration_minutes': traffic_data['current_duration_minutes'],
                'traffic_condition': traffic_data['traffic_condition'],
                'traffic_delay_minutes': traffic_data['delay_minutes']
            },
            'alternative_routes': traffic_data['alternative_routes'],
            'traffic_incidents': traffic_data['incidents'],
            'recommendations': self._generate_recommendations(traffic_data),
            'updated_at': datetime.now().isoformat()
        }
        
        return optimal_route
    
    async def optimize_multiple_routes(self, requests: List[Dict]) -> Dict:
        """Optimize multiple routes for efficient vehicle assignment"""
        optimized_routes = []
        
        for request in requests:
            route = await self.optimize_single_route(
                request['origin'], 
                request['destination'],
                request.get('departure_time')
            )
            route['request_id'] = request['id']
            optimized_routes.append(route)
        
        # Find optimal grouping for shared rides
        shared_opportunities = self._find_shared_ride_opportunities(optimized_routes)
        
        return {
            'optimized_routes': optimized_routes,
            'shared_ride_opportunities': shared_opportunities,
            'total_estimated_time': sum(r['primary_route']['estimated_duration_minutes'] for r in optimized_routes),
            'total_distance': sum(r['primary_route']['distance_km'] for r in optimized_routes),
            'optimization_summary': self._generate_optimization_summary(optimized_routes),
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, traffic_data: Dict) -> List[str]:
        """Generate route recommendations based on traffic data"""
        recommendations = []
        
        if traffic_data['traffic_condition'] == 'heavy':
            recommendations.append("⚠️ Heavy traffic detected. Consider delaying departure by 30-60 minutes.")
            recommendations.append("🛣️ Alternative routes available with potentially shorter travel time.")
        
        if traffic_data['delay_minutes'] > 15:
            recommendations.append(f"⏰ Expected delay: {traffic_data['delay_minutes']} minutes due to traffic.")
        
        if traffic_data['incidents']:
            recommendations.append("🚧 Traffic incidents reported on route. Monitor for updates.")
        
        if traffic_data['traffic_condition'] == 'free_flow':
            recommendations.append("✅ Optimal travel conditions. Good time to depart.")
        
        return recommendations
    
    def _find_shared_ride_opportunities(self, routes: List[Dict]) -> List[Dict]:
        """Find opportunities for shared rides"""
        opportunities = []
        
        # Simple shared ride detection based on similar origins/destinations
        for i, route1 in enumerate(routes):
            for j, route2 in enumerate(routes[i+1:], i+1):
                similarity_score = self._calculate_route_similarity(route1, route2)
                
                if similarity_score > 0.7:  # 70% similarity threshold
                    opportunities.append({
                        'request_ids': [route1['request_id'], route2['request_id']],
                        'similarity_score': similarity_score,
                        'estimated_savings': {
                            'time_minutes': random.randint(10, 30),
                            'distance_km': random.uniform(2, 8),
                            'fuel_cost': random.uniform(50, 200)
                        },
                        'pickup_sequence': self._optimize_pickup_sequence([route1, route2])
                    })
        
        return opportunities
    
    def _calculate_route_similarity(self, route1: Dict, route2: Dict) -> float:
        """Calculate similarity between two routes"""
        # Simplified similarity calculation
        # In production, use proper geospatial analysis
        
        origin_similarity = 0.5 if route1['origin'] == route2['origin'] else 0
        dest_similarity = 0.5 if route1['destination'] == route2['destination'] else 0
        
        return origin_similarity + dest_similarity
    
    def _optimize_pickup_sequence(self, routes: List[Dict]) -> List[Dict]:
        """Optimize pickup sequence for shared rides"""
        # Simplified pickup optimization
        return [
            {
                'order': 1,
                'location': routes[0]['origin'],
                'type': 'pickup',
                'request_id': routes[0]['request_id']
            },
            {
                'order': 2,
                'location': routes[1]['origin'],
                'type': 'pickup',
                'request_id': routes[1]['request_id']
            },
            {
                'order': 3,
                'location': routes[0]['destination'],
                'type': 'dropoff',
                'request_id': routes[0]['request_id']
            },
            {
                'order': 4,
                'location': routes[1]['destination'],
                'type': 'dropoff',
                'request_id': routes[1]['request_id']
            }
        ]
    
    def _generate_optimization_summary(self, routes: List[Dict]) -> Dict:
        """Generate optimization summary"""
        total_routes = len(routes)
        heavy_traffic_routes = len([r for r in routes if r['primary_route']['traffic_condition'] == 'heavy'])
        total_delays = sum(r['primary_route']['traffic_delay_minutes'] for r in routes)
        
        return {
            'total_routes_optimized': total_routes,
            'routes_with_heavy_traffic': heavy_traffic_routes,
            'total_traffic_delay_minutes': total_delays,
            'average_delay_per_route': total_delays / max(1, total_routes),
            'optimization_score': max(0, 100 - (heavy_traffic_routes / max(1, total_routes)) * 50)
        }

# Create global instance
route_optimizer = RouteOptimizer()
