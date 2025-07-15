"""
AI-Powered Automated Scheduling System
Intelligent trip scheduling with resource optimization and conflict resolution
"""

import asyncio
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple
import random
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class SchedulingStatus(Enum):
    SCHEDULED = "scheduled"
    CONFLICT = "conflict"
    PENDING = "pending"
    OPTIMIZED = "optimized"

@dataclass
class SchedulingRequest:
    id: int
    user_id: str
    origin: str
    destination: str
    requested_date: datetime
    requested_time: time
    passenger_count: int
    priority: Priority
    flexibility_minutes: int = 30  # How flexible the user is with timing
    recurring: bool = False
    recurring_pattern: Optional[str] = None  # daily, weekly, monthly
    special_requirements: List[str] = None

@dataclass
class ScheduledTrip:
    request_id: int
    scheduled_date: datetime
    scheduled_time: time
    estimated_duration: int
    assigned_vehicle_id: Optional[int] = None
    assigned_driver_id: Optional[int] = None
    status: SchedulingStatus = SchedulingStatus.PENDING
    confidence_score: float = 0.0
    alternative_slots: List[Dict] = None

class AutomatedScheduler:
    """AI-powered scheduling system with conflict resolution"""
    
    def __init__(self):
        self.scheduled_trips = []
        self.scheduling_rules = self._initialize_scheduling_rules()
        self.optimization_weights = {
            'priority': 0.3,
            'efficiency': 0.25,
            'user_preference': 0.2,
            'resource_utilization': 0.15,
            'cost_optimization': 0.1
        }
    
    def _initialize_scheduling_rules(self) -> Dict:
        """Initialize scheduling business rules"""
        return {
            'working_hours': {
                'start': time(6, 0),  # 6:00 AM
                'end': time(22, 0)    # 10:00 PM
            },
            'peak_hours': [
                {'start': time(8, 0), 'end': time(10, 0)},   # Morning rush
                {'start': time(17, 0), 'end': time(20, 0)}   # Evening rush
            ],
            'buffer_time_minutes': 15,  # Buffer between trips
            'max_daily_trips_per_vehicle': 12,
            'max_daily_hours_per_driver': 10,
            'priority_time_slots': {
                Priority.URGENT: 0,      # Immediate scheduling
                Priority.HIGH: 30,       # Within 30 minutes
                Priority.MEDIUM: 120,    # Within 2 hours
                Priority.LOW: 480        # Within 8 hours
            }
        }
    
    async def schedule_request(self, request: SchedulingRequest, 
                             available_vehicles: List[Dict], 
                             available_drivers: List[Dict]) -> Dict:
        """Schedule a single transport request"""
        
        # Analyze request and find optimal time slots
        optimal_slots = await self._find_optimal_time_slots(request)
        
        # Check resource availability
        resource_availability = self._check_resource_availability(
            optimal_slots, available_vehicles, available_drivers
        )
        
        # Apply scheduling algorithm
        scheduled_trip = await self._apply_scheduling_algorithm(
            request, optimal_slots, resource_availability
        )
        
        # Handle conflicts if any
        if scheduled_trip.status == SchedulingStatus.CONFLICT:
            scheduled_trip = await self._resolve_scheduling_conflicts(
                request, scheduled_trip, available_vehicles, available_drivers
            )
        
        # Add to scheduled trips
        self.scheduled_trips.append(scheduled_trip)
        
        return {
            'success': True,
            'scheduled_trip': asdict(scheduled_trip),
            'scheduling_details': {
                'original_request_time': request.requested_time.strftime('%H:%M'),
                'scheduled_time': scheduled_trip.scheduled_time.strftime('%H:%M'),
                'time_adjustment_minutes': self._calculate_time_adjustment(request, scheduled_trip),
                'confidence_score': scheduled_trip.confidence_score,
                'optimization_factors': self._get_optimization_factors(request, scheduled_trip)
            },
            'alternatives': scheduled_trip.alternative_slots or []
        }
    
    async def schedule_multiple_requests(self, requests: List[SchedulingRequest],
                                       available_vehicles: List[Dict],
                                       available_drivers: List[Dict]) -> Dict:
        """Schedule multiple requests with global optimization"""
        
        # Sort requests by priority and requested time
        sorted_requests = sorted(requests, key=lambda r: (r.priority.value, r.requested_time))
        
        scheduled_results = []
        conflicts = []
        optimizations = []
        
        for request in sorted_requests:
            result = await self.schedule_request(request, available_vehicles, available_drivers)
            
            if result['scheduled_trip']['status'] == SchedulingStatus.CONFLICT.value:
                conflicts.append(result)
            else:
                scheduled_results.append(result)
        
        # Global optimization pass
        if len(scheduled_results) > 1:
            optimizations = await self._global_optimization_pass(scheduled_results)
        
        return {
            'success': True,
            'total_requests': len(requests),
            'successfully_scheduled': len(scheduled_results),
            'conflicts': len(conflicts),
            'scheduled_trips': scheduled_results,
            'conflict_details': conflicts,
            'optimizations_applied': optimizations,
            'scheduling_summary': self._generate_scheduling_summary(scheduled_results, conflicts),
            'generated_at': datetime.now().isoformat()
        }
    
    async def _find_optimal_time_slots(self, request: SchedulingRequest) -> List[Dict]:
        """Find optimal time slots for a request"""
        slots = []
        base_time = datetime.combine(request.requested_date, request.requested_time)
        
        # Primary slot (requested time)
        slots.append({
            'slot_time': base_time,
            'score': 100,
            'type': 'requested',
            'factors': ['user_preference']
        })
        
        # Alternative slots within flexibility window
        for offset in [-30, -15, 15, 30, 45, 60]:
            if abs(offset) <= request.flexibility_minutes:
                alt_time = base_time + timedelta(minutes=offset)
                
                # Check if within working hours
                if self._is_within_working_hours(alt_time.time()):
                    score = self._calculate_slot_score(alt_time, request)
                    slots.append({
                        'slot_time': alt_time,
                        'score': score,
                        'type': 'alternative',
                        'factors': self._get_slot_factors(alt_time)
                    })
        
        # Sort by score (highest first)
        return sorted(slots, key=lambda s: s['score'], reverse=True)
    
    def _calculate_slot_score(self, slot_time: datetime, request: SchedulingRequest) -> float:
        """Calculate score for a time slot"""
        score = 50  # Base score
        
        # Priority bonus
        score += request.priority.value * 10
        
        # Peak hours penalty
        if self._is_peak_hour(slot_time.time()):
            score -= 20
        
        # Efficiency bonus (less congested times)
        if 10 <= slot_time.hour <= 16:  # Mid-day efficiency
            score += 15
        
        # Weekend bonus
        if slot_time.weekday() >= 5:  # Saturday, Sunday
            score += 10
        
        return min(100, max(0, score))
    
    def _is_within_working_hours(self, check_time: time) -> bool:
        """Check if time is within working hours"""
        rules = self.scheduling_rules['working_hours']
        return rules['start'] <= check_time <= rules['end']
    
    def _is_peak_hour(self, check_time: time) -> bool:
        """Check if time is during peak hours"""
        for peak in self.scheduling_rules['peak_hours']:
            if peak['start'] <= check_time <= peak['end']:
                return True
        return False
    
    def _get_slot_factors(self, slot_time: datetime) -> List[str]:
        """Get factors affecting this time slot"""
        factors = []
        
        if self._is_peak_hour(slot_time.time()):
            factors.append('peak_hour')
        
        if 10 <= slot_time.hour <= 16:
            factors.append('efficient_time')
        
        if slot_time.weekday() >= 5:
            factors.append('weekend')
        
        return factors
    
    def _check_resource_availability(self, time_slots: List[Dict], 
                                   vehicles: List[Dict], 
                                   drivers: List[Dict]) -> Dict:
        """Check resource availability for time slots"""
        availability = {}
        
        for slot in time_slots:
            slot_time = slot['slot_time']
            available_vehicles = []
            available_drivers = []
            
            # Check vehicle availability
            for vehicle in vehicles:
                if self._is_vehicle_available(vehicle, slot_time):
                    available_vehicles.append(vehicle)
            
            # Check driver availability
            for driver in drivers:
                if self._is_driver_available(driver, slot_time):
                    available_drivers.append(driver)
            
            availability[slot_time.isoformat()] = {
                'vehicles': available_vehicles,
                'drivers': available_drivers,
                'resource_score': len(available_vehicles) * len(available_drivers)
            }
        
        return availability
    
    def _is_vehicle_available(self, vehicle: Dict, slot_time: datetime) -> bool:
        """Check if vehicle is available at given time"""
        # Check against existing scheduled trips
        buffer_minutes = self.scheduling_rules['buffer_time_minutes']
        
        for trip in self.scheduled_trips:
            if trip.assigned_vehicle_id == vehicle['id']:
                trip_start = datetime.combine(trip.scheduled_date, trip.scheduled_time)
                trip_end = trip_start + timedelta(minutes=trip.estimated_duration + buffer_minutes)
                
                if trip_start <= slot_time <= trip_end:
                    return False
        
        return vehicle.get('status') == 'available'
    
    def _is_driver_available(self, driver: Dict, slot_time: datetime) -> bool:
        """Check if driver is available at given time"""
        # Similar logic to vehicle availability
        buffer_minutes = self.scheduling_rules['buffer_time_minutes']
        
        for trip in self.scheduled_trips:
            if trip.assigned_driver_id == driver['id']:
                trip_start = datetime.combine(trip.scheduled_date, trip.scheduled_time)
                trip_end = trip_start + timedelta(minutes=trip.estimated_duration + buffer_minutes)
                
                if trip_start <= slot_time <= trip_end:
                    return False
        
        return driver.get('status') == 'available'
    
    async def _apply_scheduling_algorithm(self, request: SchedulingRequest,
                                        time_slots: List[Dict],
                                        resource_availability: Dict) -> ScheduledTrip:
        """Apply AI scheduling algorithm"""
        
        best_slot = None
        best_score = 0
        best_resources = None
        
        for slot in time_slots:
            slot_key = slot['slot_time'].isoformat()
            if slot_key in resource_availability:
                availability = resource_availability[slot_key]
                
                if availability['vehicles'] and availability['drivers']:
                    # Calculate combined score
                    combined_score = (
                        slot['score'] * self.optimization_weights['user_preference'] +
                        availability['resource_score'] * self.optimization_weights['resource_utilization'] +
                        request.priority.value * 20 * self.optimization_weights['priority']
                    )
                    
                    if combined_score > best_score:
                        best_score = combined_score
                        best_slot = slot
                        best_resources = availability
        
        if best_slot:
            # Select best vehicle and driver
            selected_vehicle = self._select_best_vehicle(best_resources['vehicles'], request)
            selected_driver = self._select_best_driver(best_resources['drivers'], request)
            
            return ScheduledTrip(
                request_id=request.id,
                scheduled_date=best_slot['slot_time'].date(),
                scheduled_time=best_slot['slot_time'].time(),
                estimated_duration=self._estimate_trip_duration(request),
                assigned_vehicle_id=selected_vehicle['id'],
                assigned_driver_id=selected_driver['id'],
                status=SchedulingStatus.SCHEDULED,
                confidence_score=best_score / 100,
                alternative_slots=self._generate_alternative_slots(time_slots, best_slot)
            )
        else:
            return ScheduledTrip(
                request_id=request.id,
                scheduled_date=request.requested_date,
                scheduled_time=request.requested_time,
                estimated_duration=self._estimate_trip_duration(request),
                status=SchedulingStatus.CONFLICT,
                confidence_score=0.0
            )
    
    def _select_best_vehicle(self, vehicles: List[Dict], request: SchedulingRequest) -> Dict:
        """Select best vehicle for request"""
        # Score vehicles based on capacity, fuel efficiency, etc.
        scored_vehicles = []
        
        for vehicle in vehicles:
            score = 0
            
            # Capacity match
            if vehicle.get('capacity', 4) >= request.passenger_count:
                score += 30
            
            # Fuel efficiency
            if vehicle.get('fuel_type') == 'electric':
                score += 20
            elif vehicle.get('fuel_type') == 'hybrid':
                score += 15
            
            # Vehicle condition
            score += vehicle.get('condition_score', 80)
            
            scored_vehicles.append((vehicle, score))
        
        # Return highest scored vehicle
        return max(scored_vehicles, key=lambda x: x[1])[0]
    
    def _select_best_driver(self, drivers: List[Dict], request: SchedulingRequest) -> Dict:
        """Select best driver for request"""
        # Score drivers based on rating, experience, etc.
        scored_drivers = []
        
        for driver in drivers:
            score = 0
            
            # Rating
            score += (driver.get('rating', 3.0) * 20)
            
            # Experience
            score += min(driver.get('total_trips', 0) / 10, 20)
            
            # Availability score
            score += 10
            
            scored_drivers.append((driver, score))
        
        # Return highest scored driver
        return max(scored_drivers, key=lambda x: x[1])[0]
    
    def _estimate_trip_duration(self, request: SchedulingRequest) -> int:
        """Estimate trip duration in minutes"""
        # Simplified duration estimation
        # In production, integrate with route optimization service
        base_duration = random.randint(20, 90)  # 20-90 minutes
        
        # Add buffer for passenger count
        if request.passenger_count > 2:
            base_duration += 10
        
        return base_duration
    
    def _generate_alternative_slots(self, all_slots: List[Dict], selected_slot: Dict) -> List[Dict]:
        """Generate alternative time slots"""
        alternatives = []
        
        for slot in all_slots[:3]:  # Top 3 alternatives
            if slot != selected_slot:
                alternatives.append({
                    'time': slot['slot_time'].strftime('%H:%M'),
                    'score': slot['score'],
                    'factors': slot['factors']
                })
        
        return alternatives
    
    async def _resolve_scheduling_conflicts(self, request: SchedulingRequest,
                                          conflicted_trip: ScheduledTrip,
                                          vehicles: List[Dict],
                                          drivers: List[Dict]) -> ScheduledTrip:
        """Resolve scheduling conflicts using AI"""
        
        # Try extending the search window
        extended_request = SchedulingRequest(
            **{**asdict(request), 'flexibility_minutes': request.flexibility_minutes + 60}
        )
        
        # Find new time slots with extended flexibility
        extended_slots = await self._find_optimal_time_slots(extended_request)
        extended_availability = self._check_resource_availability(extended_slots, vehicles, drivers)
        
        # Try to reschedule
        resolved_trip = await self._apply_scheduling_algorithm(
            extended_request, extended_slots, extended_availability
        )
        
        if resolved_trip.status == SchedulingStatus.SCHEDULED:
            resolved_trip.status = SchedulingStatus.OPTIMIZED
            return resolved_trip
        
        return conflicted_trip
    
    async def _global_optimization_pass(self, scheduled_results: List[Dict]) -> List[Dict]:
        """Apply global optimization to improve overall efficiency"""
        optimizations = []
        
        # Look for optimization opportunities
        # 1. Shared rides
        # 2. Route consolidation
        # 3. Resource reallocation
        
        # Simplified optimization example
        for i, result1 in enumerate(scheduled_results):
            for j, result2 in enumerate(scheduled_results[i+1:], i+1):
                if self._can_optimize_together(result1, result2):
                    optimization = {
                        'type': 'shared_ride_opportunity',
                        'trip_ids': [result1['scheduled_trip']['request_id'], 
                                   result2['scheduled_trip']['request_id']],
                        'potential_savings': {
                            'time_minutes': random.randint(10, 30),
                            'cost_percentage': random.randint(15, 35)
                        }
                    }
                    optimizations.append(optimization)
        
        return optimizations
    
    def _can_optimize_together(self, result1: Dict, result2: Dict) -> bool:
        """Check if two trips can be optimized together"""
        trip1 = result1['scheduled_trip']
        trip2 = result2['scheduled_trip']
        
        # Check time proximity (within 30 minutes)
        time1 = datetime.strptime(trip1['scheduled_time'], '%H:%M:%S').time()
        time2 = datetime.strptime(trip2['scheduled_time'], '%H:%M:%S').time()
        
        time_diff = abs((datetime.combine(datetime.today(), time1) - 
                        datetime.combine(datetime.today(), time2)).total_seconds() / 60)
        
        return time_diff <= 30
    
    def _calculate_time_adjustment(self, request: SchedulingRequest, 
                                 scheduled_trip: ScheduledTrip) -> int:
        """Calculate time adjustment in minutes"""
        requested_datetime = datetime.combine(request.requested_date, request.requested_time)
        scheduled_datetime = datetime.combine(scheduled_trip.scheduled_date, scheduled_trip.scheduled_time)
        
        return int((scheduled_datetime - requested_datetime).total_seconds() / 60)
    
    def _get_optimization_factors(self, request: SchedulingRequest, 
                                scheduled_trip: ScheduledTrip) -> List[str]:
        """Get factors that influenced the scheduling decision"""
        factors = []
        
        if scheduled_trip.confidence_score > 0.8:
            factors.append('high_confidence_match')
        
        if request.priority == Priority.HIGH:
            factors.append('priority_scheduling')
        
        if scheduled_trip.status == SchedulingStatus.OPTIMIZED:
            factors.append('conflict_resolution_applied')
        
        return factors
    
    def _generate_scheduling_summary(self, scheduled_results: List[Dict], 
                                   conflicts: List[Dict]) -> Dict:
        """Generate scheduling summary statistics"""
        total_requests = len(scheduled_results) + len(conflicts)
        
        if total_requests == 0:
            return {}
        
        success_rate = len(scheduled_results) / total_requests * 100
        avg_confidence = sum(r['scheduled_trip']['confidence_score'] for r in scheduled_results) / max(1, len(scheduled_results))
        
        return {
            'success_rate_percentage': round(success_rate, 1),
            'average_confidence_score': round(avg_confidence, 2),
            'total_time_adjustments': sum(abs(r['scheduling_details']['time_adjustment_minutes']) for r in scheduled_results),
            'peak_hour_assignments': len([r for r in scheduled_results if 'peak_hour' in r['scheduling_details'].get('optimization_factors', [])]),
            'optimization_score': min(100, success_rate + avg_confidence * 20)
        }

# Create global instance
automated_scheduler = AutomatedScheduler()
