"""
Driver Performance Analytics System
Comprehensive driver performance monitoring and improvement recommendations
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import random
import logging
import statistics

logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    SAFETY = "safety"
    EFFICIENCY = "efficiency"
    PUNCTUALITY = "punctuality"
    CUSTOMER_SERVICE = "customer_service"
    VEHICLE_CARE = "vehicle_care"

class PerformanceRating(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"

@dataclass
class DriverPerformanceMetrics:
    driver_id: int
    evaluation_period: str
    overall_score: float
    safety_score: float
    efficiency_score: float
    punctuality_score: float
    customer_service_score: float
    vehicle_care_score: float
    total_trips: int
    total_distance_km: float
    total_hours_driven: float
    incidents_count: int
    customer_ratings: List[float]
    fuel_efficiency_kmpl: float
    on_time_percentage: float
    last_updated: datetime

@dataclass
class PerformanceIncident:
    id: int
    driver_id: int
    incident_type: str
    severity: str
    description: str
    date_occurred: datetime
    resolved: bool = False
    resolution_notes: str = ""

class DriverAnalyticsService:
    """Comprehensive driver performance analytics and monitoring"""
    
    def __init__(self):
        self.performance_data = {}
        self.incidents = []
        self.performance_benchmarks = self._initialize_benchmarks()
        self.scoring_weights = {
            PerformanceMetric.SAFETY: 0.30,
            PerformanceMetric.EFFICIENCY: 0.25,
            PerformanceMetric.PUNCTUALITY: 0.20,
            PerformanceMetric.CUSTOMER_SERVICE: 0.15,
            PerformanceMetric.VEHICLE_CARE: 0.10
        }
    
    def _initialize_benchmarks(self) -> Dict:
        """Initialize performance benchmarks"""
        return {
            'safety_score_min': 85.0,
            'efficiency_score_min': 80.0,
            'punctuality_score_min': 90.0,
            'customer_service_min': 4.0,  # out of 5
            'fuel_efficiency_min': 15.0,  # km/l
            'incident_threshold_monthly': 2,
            'on_time_percentage_min': 85.0
        }
    
    async def analyze_driver_performance(self, driver_id: int, 
                                       trip_data: List[Dict],
                                       period_days: int = 30) -> DriverPerformanceMetrics:
        """Comprehensive driver performance analysis"""
        
        # Filter data for the specified period
        cutoff_date = datetime.now() - timedelta(days=period_days)
        recent_trips = [trip for trip in trip_data 
                       if datetime.fromisoformat(trip['completed_at']) >= cutoff_date]
        
        if not recent_trips:
            return self._create_empty_metrics(driver_id, period_days)
        
        # Calculate individual performance scores
        safety_score = await self._calculate_safety_score(driver_id, recent_trips)
        efficiency_score = await self._calculate_efficiency_score(driver_id, recent_trips)
        punctuality_score = await self._calculate_punctuality_score(driver_id, recent_trips)
        customer_service_score = await self._calculate_customer_service_score(driver_id, recent_trips)
        vehicle_care_score = await self._calculate_vehicle_care_score(driver_id, recent_trips)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score({
            PerformanceMetric.SAFETY: safety_score,
            PerformanceMetric.EFFICIENCY: efficiency_score,
            PerformanceMetric.PUNCTUALITY: punctuality_score,
            PerformanceMetric.CUSTOMER_SERVICE: customer_service_score,
            PerformanceMetric.VEHICLE_CARE: vehicle_care_score
        })
        
        # Calculate aggregate statistics
        total_trips = len(recent_trips)
        total_distance = sum(trip.get('distance_km', 0) for trip in recent_trips)
        total_hours = sum(trip.get('duration_hours', 0) for trip in recent_trips)
        
        # Get incidents
        recent_incidents = self._get_recent_incidents(driver_id, cutoff_date)
        
        # Customer ratings
        customer_ratings = [trip.get('customer_rating', 0) for trip in recent_trips 
                          if trip.get('customer_rating', 0) > 0]
        
        # Fuel efficiency
        fuel_efficiency = self._calculate_fuel_efficiency(recent_trips)
        
        # On-time percentage
        on_time_percentage = self._calculate_on_time_percentage(recent_trips)
        
        metrics = DriverPerformanceMetrics(
            driver_id=driver_id,
            evaluation_period=f"{period_days} days",
            overall_score=overall_score,
            safety_score=safety_score,
            efficiency_score=efficiency_score,
            punctuality_score=punctuality_score,
            customer_service_score=customer_service_score,
            vehicle_care_score=vehicle_care_score,
            total_trips=total_trips,
            total_distance_km=total_distance,
            total_hours_driven=total_hours,
            incidents_count=len(recent_incidents),
            customer_ratings=customer_ratings,
            fuel_efficiency_kmpl=fuel_efficiency,
            on_time_percentage=on_time_percentage,
            last_updated=datetime.now()
        )
        
        # Cache the metrics
        self.performance_data[driver_id] = metrics
        
        return metrics
    
    async def _calculate_safety_score(self, driver_id: int, trips: List[Dict]) -> float:
        """Calculate safety performance score"""
        base_score = 100.0
        
        # Get recent incidents
        recent_incidents = self._get_recent_incidents(driver_id, datetime.now() - timedelta(days=30))
        
        # Deduct points for incidents
        for incident in recent_incidents:
            if incident.severity == 'high':
                base_score -= 20
            elif incident.severity == 'medium':
                base_score -= 10
            else:
                base_score -= 5
        
        # Deduct points for speeding (simulated)
        speeding_violations = sum(1 for trip in trips if trip.get('speeding_incidents', 0) > 0)
        base_score -= speeding_violations * 5
        
        # Deduct points for harsh braking/acceleration (simulated)
        harsh_driving_events = sum(trip.get('harsh_driving_events', 0) for trip in trips)
        base_score -= harsh_driving_events * 2
        
        # Bonus for accident-free periods
        if len(recent_incidents) == 0 and len(trips) > 10:
            base_score += 5
        
        return max(0, min(100, base_score))
    
    async def _calculate_efficiency_score(self, driver_id: int, trips: List[Dict]) -> float:
        """Calculate driving efficiency score"""
        if not trips:
            return 0
        
        # Route efficiency (actual vs optimal time)
        route_efficiency_scores = []
        for trip in trips:
            actual_time = trip.get('actual_duration_minutes', 60)
            optimal_time = trip.get('estimated_duration_minutes', 50)
            if optimal_time > 0:
                efficiency = min(100, (optimal_time / actual_time) * 100)
                route_efficiency_scores.append(efficiency)
        
        route_efficiency = statistics.mean(route_efficiency_scores) if route_efficiency_scores else 70
        
        # Fuel efficiency
        fuel_efficiency = self._calculate_fuel_efficiency(trips)
        fuel_score = min(100, (fuel_efficiency / self.performance_benchmarks['fuel_efficiency_min']) * 100)
        
        # Idle time efficiency
        idle_time_scores = []
        for trip in trips:
            total_time = trip.get('actual_duration_minutes', 60)
            idle_time = trip.get('idle_time_minutes', 5)
            idle_percentage = (idle_time / total_time) * 100
            idle_score = max(0, 100 - idle_percentage * 2)  # Penalize excessive idling
            idle_time_scores.append(idle_score)
        
        idle_efficiency = statistics.mean(idle_time_scores) if idle_time_scores else 80
        
        # Combined efficiency score
        efficiency_score = (route_efficiency * 0.4 + fuel_score * 0.4 + idle_efficiency * 0.2)
        
        return round(efficiency_score, 1)
    
    async def _calculate_punctuality_score(self, driver_id: int, trips: List[Dict]) -> float:
        """Calculate punctuality performance score"""
        if not trips:
            return 0
        
        on_time_trips = 0
        early_trips = 0
        late_trips = 0
        
        for trip in trips:
            scheduled_time = datetime.fromisoformat(trip.get('scheduled_start_time', ''))
            actual_time = datetime.fromisoformat(trip.get('actual_start_time', ''))
            
            time_diff_minutes = (actual_time - scheduled_time).total_seconds() / 60
            
            if -5 <= time_diff_minutes <= 5:  # Within 5 minutes is on time
                on_time_trips += 1
            elif time_diff_minutes < -5:
                early_trips += 1
            else:
                late_trips += 1
        
        total_trips = len(trips)
        on_time_percentage = (on_time_trips / total_trips) * 100
        
        # Bonus for being early (but not too early)
        early_bonus = min(5, (early_trips / total_trips) * 10)
        
        # Penalty for being late
        late_penalty = (late_trips / total_trips) * 20
        
        punctuality_score = on_time_percentage + early_bonus - late_penalty
        
        return max(0, min(100, punctuality_score))
    
    async def _calculate_customer_service_score(self, driver_id: int, trips: List[Dict]) -> float:
        """Calculate customer service score"""
        ratings = [trip.get('customer_rating', 0) for trip in trips 
                  if trip.get('customer_rating', 0) > 0]
        
        if not ratings:
            return 75.0  # Default score if no ratings
        
        average_rating = statistics.mean(ratings)
        
        # Convert 5-star rating to 100-point scale
        service_score = (average_rating / 5.0) * 100
        
        # Bonus for high number of ratings (engagement)
        if len(ratings) > 20:
            service_score += 5
        
        # Penalty for complaints (simulated)
        complaints = sum(1 for trip in trips if trip.get('customer_complaint', False))
        complaint_penalty = (complaints / len(trips)) * 30
        
        service_score -= complaint_penalty
        
        return max(0, min(100, service_score))
    
    async def _calculate_vehicle_care_score(self, driver_id: int, trips: List[Dict]) -> float:
        """Calculate vehicle care score"""
        base_score = 85.0  # Default good score
        
        # Vehicle condition reports
        vehicle_issues = sum(trip.get('vehicle_issues_reported', 0) for trip in trips)
        if vehicle_issues > 0:
            base_score -= vehicle_issues * 5
        
        # Maintenance compliance (simulated)
        maintenance_compliance = random.uniform(0.8, 1.0)  # 80-100% compliance
        base_score *= maintenance_compliance
        
        # Cleanliness reports (simulated)
        cleanliness_score = random.uniform(80, 95)
        base_score = (base_score + cleanliness_score) / 2
        
        return round(base_score, 1)
    
    def _calculate_overall_score(self, scores: Dict[PerformanceMetric, float]) -> float:
        """Calculate weighted overall performance score"""
        overall_score = sum(scores[metric] * weight 
                          for metric, weight in self.scoring_weights.items())
        
        return round(overall_score, 1)
    
    def _get_recent_incidents(self, driver_id: int, cutoff_date: datetime) -> List[PerformanceIncident]:
        """Get recent incidents for a driver"""
        return [incident for incident in self.incidents 
                if (incident.driver_id == driver_id and 
                    incident.date_occurred >= cutoff_date)]
    
    def _calculate_fuel_efficiency(self, trips: List[Dict]) -> float:
        """Calculate average fuel efficiency"""
        efficiencies = [trip.get('fuel_efficiency_kmpl', 15.0) for trip in trips]
        return round(statistics.mean(efficiencies) if efficiencies else 15.0, 1)
    
    def _calculate_on_time_percentage(self, trips: List[Dict]) -> float:
        """Calculate on-time delivery percentage"""
        if not trips:
            return 0
        
        on_time_count = sum(1 for trip in trips if trip.get('delivered_on_time', True))
        return round((on_time_count / len(trips)) * 100, 1)
    
    def _create_empty_metrics(self, driver_id: int, period_days: int) -> DriverPerformanceMetrics:
        """Create empty metrics for drivers with no data"""
        return DriverPerformanceMetrics(
            driver_id=driver_id,
            evaluation_period=f"{period_days} days",
            overall_score=0.0,
            safety_score=0.0,
            efficiency_score=0.0,
            punctuality_score=0.0,
            customer_service_score=0.0,
            vehicle_care_score=0.0,
            total_trips=0,
            total_distance_km=0.0,
            total_hours_driven=0.0,
            incidents_count=0,
            customer_ratings=[],
            fuel_efficiency_kmpl=0.0,
            on_time_percentage=0.0,
            last_updated=datetime.now()
        )
    
    async def generate_performance_report(self, driver_id: int, period_days: int = 30) -> Dict:
        """Generate comprehensive performance report"""
        
        # Simulate trip data for demo
        trip_data = self._generate_sample_trip_data(driver_id, period_days)
        
        # Analyze performance
        metrics = await self.analyze_driver_performance(driver_id, trip_data, period_days)
        
        # Generate recommendations
        recommendations = self._generate_performance_recommendations(metrics)
        
        # Performance trends
        trends = self._analyze_performance_trends(driver_id)
        
        # Ranking among peers
        peer_ranking = self._calculate_peer_ranking(driver_id, metrics)
        
        return {
            'driver_id': driver_id,
            'report_period': f"{period_days} days",
            'generated_at': datetime.now().isoformat(),
            'performance_summary': {
                'overall_score': metrics.overall_score,
                'performance_rating': self._get_performance_rating(metrics.overall_score).value,
                'total_trips': metrics.total_trips,
                'total_distance_km': metrics.total_distance_km,
                'total_hours_driven': metrics.total_hours_driven
            },
            'detailed_scores': {
                'safety': metrics.safety_score,
                'efficiency': metrics.efficiency_score,
                'punctuality': metrics.punctuality_score,
                'customer_service': metrics.customer_service_score,
                'vehicle_care': metrics.vehicle_care_score
            },
            'key_metrics': {
                'incidents_count': metrics.incidents_count,
                'average_customer_rating': round(statistics.mean(metrics.customer_ratings), 1) if metrics.customer_ratings else 0,
                'fuel_efficiency_kmpl': metrics.fuel_efficiency_kmpl,
                'on_time_percentage': metrics.on_time_percentage
            },
            'performance_trends': trends,
            'peer_ranking': peer_ranking,
            'recommendations': recommendations,
            'achievements': self._get_achievements(metrics),
            'improvement_areas': self._identify_improvement_areas(metrics)
        }
    
    def _generate_sample_trip_data(self, driver_id: int, days: int) -> List[Dict]:
        """Generate sample trip data for demo purposes"""
        trips = []
        
        for i in range(random.randint(10, 50)):  # 10-50 trips
            trip_date = datetime.now() - timedelta(days=random.randint(0, days))
            
            trips.append({
                'id': i + 1,
                'driver_id': driver_id,
                'scheduled_start_time': trip_date.isoformat(),
                'actual_start_time': (trip_date + timedelta(minutes=random.randint(-10, 15))).isoformat(),
                'completed_at': (trip_date + timedelta(hours=random.randint(1, 4))).isoformat(),
                'distance_km': random.uniform(5, 50),
                'duration_hours': random.uniform(0.5, 3.0),
                'actual_duration_minutes': random.randint(30, 180),
                'estimated_duration_minutes': random.randint(25, 150),
                'customer_rating': random.choice([3, 4, 4, 5, 5, 5]),  # Weighted towards higher ratings
                'fuel_efficiency_kmpl': random.uniform(12, 20),
                'delivered_on_time': random.choice([True, True, True, False]),  # 75% on time
                'speeding_incidents': random.randint(0, 2),
                'harsh_driving_events': random.randint(0, 3),
                'idle_time_minutes': random.randint(2, 15),
                'vehicle_issues_reported': random.randint(0, 1),
                'customer_complaint': random.choice([False, False, False, False, True])  # 20% complaints
            })
        
        return trips
    
    def _get_performance_rating(self, score: float) -> PerformanceRating:
        """Convert score to performance rating"""
        if score >= 90:
            return PerformanceRating.EXCELLENT
        elif score >= 80:
            return PerformanceRating.GOOD
        elif score >= 70:
            return PerformanceRating.AVERAGE
        elif score >= 60:
            return PerformanceRating.NEEDS_IMPROVEMENT
        else:
            return PerformanceRating.POOR
    
    def _generate_performance_recommendations(self, metrics: DriverPerformanceMetrics) -> List[str]:
        """Generate personalized performance recommendations"""
        recommendations = []
        
        if metrics.safety_score < 80:
            recommendations.append("🛡️ PRIORITY: Attend defensive driving course to improve safety score")
            recommendations.append("⚠️ Review recent incidents and implement corrective measures")
        
        if metrics.efficiency_score < 75:
            recommendations.append("⛽ Focus on fuel-efficient driving techniques")
            recommendations.append("🗺️ Use route optimization tools to reduce travel time")
        
        if metrics.punctuality_score < 85:
            recommendations.append("⏰ Improve time management and departure planning")
            recommendations.append("📱 Use traffic apps to avoid delays")
        
        if metrics.customer_service_score < 80:
            recommendations.append("😊 Attend customer service training program")
            recommendations.append("💬 Focus on professional communication with passengers")
        
        if metrics.vehicle_care_score < 80:
            recommendations.append("🔧 Improve vehicle maintenance awareness")
            recommendations.append("🧽 Maintain higher vehicle cleanliness standards")
        
        # Positive reinforcement
        if metrics.overall_score >= 85:
            recommendations.append("🌟 Excellent performance! Consider mentoring new drivers")
        
        return recommendations
    
    def _analyze_performance_trends(self, driver_id: int) -> Dict:
        """Analyze performance trends over time"""
        # Simulated trend analysis
        return {
            'overall_trend': random.choice(['improving', 'stable', 'declining']),
            'safety_trend': random.choice(['improving', 'stable']),
            'efficiency_trend': random.choice(['improving', 'stable', 'declining']),
            'punctuality_trend': random.choice(['improving', 'stable']),
            'trend_period': '3 months'
        }
    
    def _calculate_peer_ranking(self, driver_id: int, metrics: DriverPerformanceMetrics) -> Dict:
        """Calculate ranking among peer drivers"""
        # Simulated peer ranking
        total_drivers = random.randint(20, 50)
        rank = random.randint(1, total_drivers)
        percentile = ((total_drivers - rank) / total_drivers) * 100
        
        return {
            'rank': rank,
            'total_drivers': total_drivers,
            'percentile': round(percentile, 1),
            'performance_tier': 'top' if percentile >= 80 else 'middle' if percentile >= 40 else 'bottom'
        }
    
    def _get_achievements(self, metrics: DriverPerformanceMetrics) -> List[str]:
        """Get driver achievements based on performance"""
        achievements = []
        
        if metrics.safety_score >= 95:
            achievements.append("🏆 Safety Champion - 95+ Safety Score")
        
        if metrics.punctuality_score >= 95:
            achievements.append("⏰ Punctuality Master - 95+ On-Time Performance")
        
        if metrics.customer_service_score >= 90:
            achievements.append("⭐ Customer Favorite - 90+ Service Score")
        
        if metrics.total_trips >= 100:
            achievements.append("🚗 Century Driver - 100+ Trips Completed")
        
        if metrics.fuel_efficiency_kmpl >= 18:
            achievements.append("🌱 Eco Driver - Excellent Fuel Efficiency")
        
        return achievements
    
    def _identify_improvement_areas(self, metrics: DriverPerformanceMetrics) -> List[Dict]:
        """Identify specific areas for improvement"""
        areas = []
        
        scores = {
            'Safety': metrics.safety_score,
            'Efficiency': metrics.efficiency_score,
            'Punctuality': metrics.punctuality_score,
            'Customer Service': metrics.customer_service_score,
            'Vehicle Care': metrics.vehicle_care_score
        }
        
        # Find lowest scoring areas
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        
        for area, score in sorted_scores[:2]:  # Top 2 improvement areas
            if score < 80:
                priority = 'high' if score < 70 else 'medium'
                areas.append({
                    'area': area,
                    'current_score': score,
                    'target_score': 85,
                    'priority': priority,
                    'improvement_needed': 85 - score
                })
        
        return areas

# Create global instance
driver_analytics_service = DriverAnalyticsService()
