"""
Predictive Vehicle Maintenance Tracking System
AI-powered maintenance scheduling and vehicle health monitoring
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import random
import logging

logger = logging.getLogger(__name__)

class MaintenanceType(Enum):
    ROUTINE = "routine"
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"

class MaintenanceStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class VehicleHealthStatus(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class MaintenanceRecord:
    id: int
    vehicle_id: int
    maintenance_type: MaintenanceType
    description: str
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    cost: float = 0.0
    mileage_at_service: int = 0
    technician: str = ""
    status: MaintenanceStatus = MaintenanceStatus.SCHEDULED
    parts_replaced: List[str] = None
    notes: str = ""
    next_service_due: Optional[datetime] = None

@dataclass
class VehicleHealthMetrics:
    vehicle_id: int
    overall_health_score: float
    engine_health: float
    brake_health: float
    tire_health: float
    battery_health: float
    transmission_health: float
    last_updated: datetime
    predicted_issues: List[Dict] = None
    maintenance_recommendations: List[str] = None

class VehicleMaintenanceService:
    """Comprehensive vehicle maintenance management system"""
    
    def __init__(self):
        self.maintenance_records = []
        self.health_metrics = {}
        self.maintenance_schedules = self._initialize_maintenance_schedules()
        self.predictive_models = self._initialize_predictive_models()
    
    def _initialize_maintenance_schedules(self) -> Dict:
        """Initialize standard maintenance schedules"""
        return {
            'routine_service': {
                'interval_km': 5000,
                'interval_months': 3,
                'tasks': ['Oil change', 'Filter replacement', 'Fluid check', 'Basic inspection']
            },
            'comprehensive_service': {
                'interval_km': 10000,
                'interval_months': 6,
                'tasks': ['Full inspection', 'Brake check', 'Tire rotation', 'Battery test', 'AC service']
            },
            'major_service': {
                'interval_km': 20000,
                'interval_months': 12,
                'tasks': ['Engine tune-up', 'Transmission service', 'Cooling system', 'Suspension check']
            },
            'annual_inspection': {
                'interval_months': 12,
                'tasks': ['Safety inspection', 'Emissions test', 'Insurance renewal', 'Registration renewal']
            }
        }
    
    def _initialize_predictive_models(self) -> Dict:
        """Initialize predictive maintenance models"""
        return {
            'engine_wear_model': {
                'factors': ['mileage', 'age', 'usage_pattern', 'maintenance_history'],
                'thresholds': {'warning': 70, 'critical': 85}
            },
            'brake_wear_model': {
                'factors': ['mileage', 'driving_style', 'terrain', 'brake_usage'],
                'thresholds': {'warning': 75, 'critical': 90}
            },
            'tire_wear_model': {
                'factors': ['mileage', 'road_conditions', 'tire_pressure', 'alignment'],
                'thresholds': {'warning': 80, 'critical': 95}
            },
            'battery_health_model': {
                'factors': ['age', 'charge_cycles', 'temperature_exposure', 'usage_pattern'],
                'thresholds': {'warning': 65, 'critical': 80}
            }
        }
    
    async def analyze_vehicle_health(self, vehicle_id: int, vehicle_data: Dict) -> VehicleHealthMetrics:
        """Analyze comprehensive vehicle health using AI"""
        
        # Simulate sensor data analysis
        health_scores = await self._calculate_health_scores(vehicle_id, vehicle_data)
        
        # Predict potential issues
        predicted_issues = await self._predict_maintenance_issues(vehicle_id, vehicle_data, health_scores)
        
        # Generate maintenance recommendations
        recommendations = self._generate_maintenance_recommendations(health_scores, predicted_issues)
        
        # Calculate overall health score
        overall_score = self._calculate_overall_health_score(health_scores)
        
        health_metrics = VehicleHealthMetrics(
            vehicle_id=vehicle_id,
            overall_health_score=overall_score,
            engine_health=health_scores['engine'],
            brake_health=health_scores['brakes'],
            tire_health=health_scores['tires'],
            battery_health=health_scores['battery'],
            transmission_health=health_scores['transmission'],
            last_updated=datetime.now(),
            predicted_issues=predicted_issues,
            maintenance_recommendations=recommendations
        )
        
        # Cache the metrics
        self.health_metrics[vehicle_id] = health_metrics
        
        return health_metrics
    
    async def _calculate_health_scores(self, vehicle_id: int, vehicle_data: Dict) -> Dict:
        """Calculate health scores for different vehicle components"""
        
        # Simulate AI-based health analysis
        await asyncio.sleep(0.1)  # Simulate processing time
        
        mileage = vehicle_data.get('mileage', 50000)
        age_years = vehicle_data.get('age_years', 3)
        last_service_km = vehicle_data.get('last_service_km', 45000)
        
        # Engine health calculation
        engine_score = 100
        engine_score -= min(mileage / 1000, 30)  # Mileage impact
        engine_score -= age_years * 5  # Age impact
        engine_score -= max(0, (mileage - last_service_km) / 500)  # Service overdue impact
        engine_score += random.uniform(-5, 5)  # Random variation
        
        # Brake health calculation
        brake_score = 100
        brake_score -= min(mileage / 2000, 25)
        brake_score -= age_years * 3
        brake_score += random.uniform(-8, 8)
        
        # Tire health calculation
        tire_score = 100
        tire_score -= min(mileage / 1500, 35)
        tire_score -= age_years * 4
        tire_score += random.uniform(-10, 10)
        
        # Battery health calculation
        battery_score = 100
        battery_score -= age_years * 15  # Batteries degrade faster
        battery_score -= min(mileage / 5000, 20)
        battery_score += random.uniform(-5, 5)
        
        # Transmission health calculation
        transmission_score = 100
        transmission_score -= min(mileage / 3000, 20)
        transmission_score -= age_years * 3
        transmission_score += random.uniform(-5, 5)
        
        return {
            'engine': max(0, min(100, engine_score)),
            'brakes': max(0, min(100, brake_score)),
            'tires': max(0, min(100, tire_score)),
            'battery': max(0, min(100, battery_score)),
            'transmission': max(0, min(100, transmission_score))
        }
    
    async def _predict_maintenance_issues(self, vehicle_id: int, vehicle_data: Dict, 
                                        health_scores: Dict) -> List[Dict]:
        """Predict potential maintenance issues using ML models"""
        
        predicted_issues = []
        
        # Engine predictions
        if health_scores['engine'] < 70:
            predicted_issues.append({
                'component': 'Engine',
                'issue': 'Oil change required',
                'probability': 0.85,
                'estimated_days': random.randint(7, 21),
                'severity': 'medium',
                'estimated_cost': random.randint(2000, 5000)
            })
        
        if health_scores['engine'] < 50:
            predicted_issues.append({
                'component': 'Engine',
                'issue': 'Engine tune-up needed',
                'probability': 0.75,
                'estimated_days': random.randint(14, 30),
                'severity': 'high',
                'estimated_cost': random.randint(8000, 15000)
            })
        
        # Brake predictions
        if health_scores['brakes'] < 75:
            predicted_issues.append({
                'component': 'Brakes',
                'issue': 'Brake pad replacement',
                'probability': 0.70,
                'estimated_days': random.randint(10, 25),
                'severity': 'high',
                'estimated_cost': random.randint(3000, 8000)
            })
        
        # Tire predictions
        if health_scores['tires'] < 80:
            predicted_issues.append({
                'component': 'Tires',
                'issue': 'Tire rotation/replacement',
                'probability': 0.60,
                'estimated_days': random.randint(5, 15),
                'severity': 'medium',
                'estimated_cost': random.randint(5000, 20000)
            })
        
        # Battery predictions
        if health_scores['battery'] < 65:
            predicted_issues.append({
                'component': 'Battery',
                'issue': 'Battery replacement',
                'probability': 0.80,
                'estimated_days': random.randint(3, 10),
                'severity': 'high',
                'estimated_cost': random.randint(4000, 8000)
            })
        
        return predicted_issues
    
    def _generate_maintenance_recommendations(self, health_scores: Dict, 
                                           predicted_issues: List[Dict]) -> List[str]:
        """Generate actionable maintenance recommendations"""
        recommendations = []
        
        # Priority recommendations based on health scores
        if health_scores['engine'] < 60:
            recommendations.append("🔧 URGENT: Schedule engine inspection immediately")
        elif health_scores['engine'] < 80:
            recommendations.append("⚠️ Schedule engine service within 2 weeks")
        
        if health_scores['brakes'] < 70:
            recommendations.append("🛑 SAFETY: Brake system requires immediate attention")
        elif health_scores['brakes'] < 85:
            recommendations.append("🔍 Schedule brake inspection soon")
        
        if health_scores['tires'] < 75:
            recommendations.append("🛞 Check tire condition and pressure")
        
        if health_scores['battery'] < 70:
            recommendations.append("🔋 Battery health declining - plan replacement")
        
        # Preventive recommendations
        recommendations.append("📅 Schedule next routine service")
        recommendations.append("📊 Monitor vehicle performance metrics")
        
        # Cost optimization recommendations
        if len(predicted_issues) > 2:
            recommendations.append("💰 Consider bundling multiple services for cost savings")
        
        return recommendations
    
    def _calculate_overall_health_score(self, health_scores: Dict) -> float:
        """Calculate weighted overall health score"""
        weights = {
            'engine': 0.3,
            'brakes': 0.25,
            'tires': 0.2,
            'battery': 0.15,
            'transmission': 0.1
        }
        
        overall_score = sum(health_scores[component] * weight 
                          for component, weight in weights.items())
        
        return round(overall_score, 1)
    
    async def schedule_maintenance(self, vehicle_id: int, maintenance_type: MaintenanceType,
                                 description: str, scheduled_date: datetime,
                                 estimated_cost: float = 0.0) -> MaintenanceRecord:
        """Schedule maintenance for a vehicle"""
        
        record_id = len(self.maintenance_records) + 1
        
        maintenance_record = MaintenanceRecord(
            id=record_id,
            vehicle_id=vehicle_id,
            maintenance_type=maintenance_type,
            description=description,
            scheduled_date=scheduled_date,
            cost=estimated_cost,
            status=MaintenanceStatus.SCHEDULED
        )
        
        self.maintenance_records.append(maintenance_record)
        
        # Send notifications (simulate)
        await self._send_maintenance_notification(maintenance_record)
        
        return maintenance_record
    
    async def _send_maintenance_notification(self, record: MaintenanceRecord):
        """Send maintenance notification to relevant parties"""
        # Simulate notification sending
        logger.info(f"Maintenance notification sent for vehicle {record.vehicle_id}: {record.description}")
    
    def get_maintenance_schedule(self, vehicle_id: int, days_ahead: int = 30) -> List[Dict]:
        """Get upcoming maintenance schedule for a vehicle"""
        
        upcoming_maintenance = []
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        for record in self.maintenance_records:
            if (record.vehicle_id == vehicle_id and 
                record.status in [MaintenanceStatus.SCHEDULED, MaintenanceStatus.OVERDUE] and
                record.scheduled_date <= cutoff_date):
                
                upcoming_maintenance.append({
                    'id': record.id,
                    'type': record.maintenance_type.value,
                    'description': record.description,
                    'scheduled_date': record.scheduled_date.isoformat(),
                    'estimated_cost': record.cost,
                    'status': record.status.value,
                    'days_until_due': (record.scheduled_date - datetime.now()).days
                })
        
        return sorted(upcoming_maintenance, key=lambda x: x['scheduled_date'])
    
    def get_maintenance_history(self, vehicle_id: int, limit: int = 10) -> List[Dict]:
        """Get maintenance history for a vehicle"""
        
        history = []
        
        for record in self.maintenance_records:
            if record.vehicle_id == vehicle_id and record.status == MaintenanceStatus.COMPLETED:
                history.append({
                    'id': record.id,
                    'type': record.maintenance_type.value,
                    'description': record.description,
                    'completed_date': record.completed_date.isoformat() if record.completed_date else None,
                    'cost': record.cost,
                    'mileage': record.mileage_at_service,
                    'technician': record.technician,
                    'parts_replaced': record.parts_replaced or [],
                    'notes': record.notes
                })
        
        return sorted(history, key=lambda x: x['completed_date'], reverse=True)[:limit]
    
    async def generate_maintenance_report(self, vehicle_id: int) -> Dict:
        """Generate comprehensive maintenance report"""
        
        # Get vehicle health metrics
        if vehicle_id not in self.health_metrics:
            # Simulate vehicle data for demo
            vehicle_data = {
                'mileage': random.randint(30000, 100000),
                'age_years': random.randint(1, 8),
                'last_service_km': random.randint(25000, 95000)
            }
            health_metrics = await self.analyze_vehicle_health(vehicle_id, vehicle_data)
        else:
            health_metrics = self.health_metrics[vehicle_id]
        
        # Get maintenance schedule and history
        upcoming_maintenance = self.get_maintenance_schedule(vehicle_id)
        maintenance_history = self.get_maintenance_history(vehicle_id)
        
        # Calculate maintenance costs
        total_cost_last_year = sum(
            record.cost for record in self.maintenance_records
            if (record.vehicle_id == vehicle_id and 
                record.completed_date and
                record.completed_date >= datetime.now() - timedelta(days=365))
        )
        
        # Generate recommendations
        cost_optimization_tips = self._generate_cost_optimization_tips(health_metrics, maintenance_history)
        
        return {
            'vehicle_id': vehicle_id,
            'report_generated_at': datetime.now().isoformat(),
            'health_summary': {
                'overall_score': health_metrics.overall_health_score,
                'health_status': self._get_health_status(health_metrics.overall_health_score).value,
                'component_scores': {
                    'engine': health_metrics.engine_health,
                    'brakes': health_metrics.brake_health,
                    'tires': health_metrics.tire_health,
                    'battery': health_metrics.battery_health,
                    'transmission': health_metrics.transmission_health
                }
            },
            'predicted_issues': health_metrics.predicted_issues or [],
            'maintenance_recommendations': health_metrics.maintenance_recommendations or [],
            'upcoming_maintenance': upcoming_maintenance,
            'maintenance_history': maintenance_history,
            'cost_analysis': {
                'total_cost_last_year': total_cost_last_year,
                'average_monthly_cost': total_cost_last_year / 12,
                'cost_optimization_tips': cost_optimization_tips
            },
            'performance_metrics': {
                'maintenance_compliance_rate': self._calculate_compliance_rate(vehicle_id),
                'average_downtime_hours': random.randint(2, 8),
                'reliability_score': min(100, health_metrics.overall_health_score + random.randint(-5, 10))
            }
        }
    
    def _get_health_status(self, score: float) -> VehicleHealthStatus:
        """Convert health score to status"""
        if score >= 90:
            return VehicleHealthStatus.EXCELLENT
        elif score >= 75:
            return VehicleHealthStatus.GOOD
        elif score >= 60:
            return VehicleHealthStatus.FAIR
        elif score >= 40:
            return VehicleHealthStatus.POOR
        else:
            return VehicleHealthStatus.CRITICAL
    
    def _generate_cost_optimization_tips(self, health_metrics: VehicleHealthMetrics, 
                                       history: List[Dict]) -> List[str]:
        """Generate cost optimization recommendations"""
        tips = []
        
        if health_metrics.overall_health_score > 80:
            tips.append("💡 Vehicle in good condition - extend service intervals slightly")
        
        if len(history) > 3:
            tips.append("📊 Consider preventive maintenance to reduce emergency repairs")
        
        tips.append("🔧 Bundle multiple services to reduce labor costs")
        tips.append("📅 Schedule maintenance during off-peak seasons for better rates")
        tips.append("🛠️ Use genuine parts for critical components, aftermarket for others")
        
        return tips
    
    def _calculate_compliance_rate(self, vehicle_id: int) -> float:
        """Calculate maintenance compliance rate"""
        total_scheduled = len([r for r in self.maintenance_records 
                             if r.vehicle_id == vehicle_id])
        
        completed_on_time = len([r for r in self.maintenance_records 
                               if (r.vehicle_id == vehicle_id and 
                                   r.status == MaintenanceStatus.COMPLETED and
                                   r.completed_date and r.completed_date <= r.scheduled_date)])
        
        if total_scheduled == 0:
            return 100.0
        
        return round((completed_on_time / total_scheduled) * 100, 1)

# Create global instance
vehicle_maintenance_service = VehicleMaintenanceService()

"""
Fuel Management System
Cost optimization and fuel efficiency tracking
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
import random

class FuelType(Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    CNG = "cng"
    ELECTRIC = "electric"
    HYBRID = "hybrid"

@dataclass
class FuelRecord:
    id: int
    vehicle_id: int
    driver_id: int
    fuel_type: FuelType
    quantity_liters: float
    cost_per_liter: float
    total_cost: float
    odometer_reading: int
    fuel_station: str
    timestamp: datetime
    trip_id: Optional[int] = None

class FuelManagementService:
    """Comprehensive fuel management and optimization"""

    def __init__(self):
        self.fuel_records = []
        self.fuel_prices = self._initialize_fuel_prices()
        self.efficiency_targets = {
            FuelType.PETROL: 15.0,  # km/l
            FuelType.DIESEL: 18.0,
            FuelType.CNG: 20.0,
            FuelType.ELECTRIC: 120.0,  # km/kWh equivalent
            FuelType.HYBRID: 25.0
        }

    def _initialize_fuel_prices(self) -> Dict:
        """Initialize current fuel prices (₹/liter)"""
        return {
            FuelType.PETROL: 102.50,
            FuelType.DIESEL: 89.75,
            FuelType.CNG: 75.20,
            FuelType.ELECTRIC: 8.50,  # ₹/kWh
            FuelType.HYBRID: 95.00
        }

    async def record_fuel_transaction(self, vehicle_id: int, driver_id: int,
                                    fuel_type: FuelType, quantity: float,
                                    fuel_station: str, odometer_reading: int) -> FuelRecord:
        """Record a fuel transaction"""

        record_id = len(self.fuel_records) + 1
        cost_per_unit = self.fuel_prices[fuel_type]
        total_cost = quantity * cost_per_unit

        fuel_record = FuelRecord(
            id=record_id,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            fuel_type=fuel_type,
            quantity_liters=quantity,
            cost_per_liter=cost_per_unit,
            total_cost=total_cost,
            odometer_reading=odometer_reading,
            fuel_station=fuel_station,
            timestamp=datetime.now()
        )

        self.fuel_records.append(fuel_record)

        # Analyze efficiency
        efficiency_analysis = await self._analyze_fuel_efficiency(vehicle_id)

        return fuel_record

    async def _analyze_fuel_efficiency(self, vehicle_id: int) -> Dict:
        """Analyze fuel efficiency for a vehicle"""

        vehicle_records = [r for r in self.fuel_records if r.vehicle_id == vehicle_id]

        if len(vehicle_records) < 2:
            return {'status': 'insufficient_data'}

        # Sort by timestamp
        vehicle_records.sort(key=lambda x: x.timestamp)

        # Calculate efficiency between consecutive records
        efficiency_data = []

        for i in range(1, len(vehicle_records)):
            prev_record = vehicle_records[i-1]
            curr_record = vehicle_records[i]

            distance = curr_record.odometer_reading - prev_record.odometer_reading
            fuel_consumed = prev_record.quantity_liters

            if distance > 0 and fuel_consumed > 0:
                efficiency = distance / fuel_consumed
                efficiency_data.append({
                    'period': f"{prev_record.timestamp.date()} to {curr_record.timestamp.date()}",
                    'distance_km': distance,
                    'fuel_consumed_l': fuel_consumed,
                    'efficiency_kmpl': round(efficiency, 2),
                    'cost': prev_record.total_cost
                })

        if not efficiency_data:
            return {'status': 'no_valid_data'}

        # Calculate averages
        avg_efficiency = sum(d['efficiency_kmpl'] for d in efficiency_data) / len(efficiency_data)
        target_efficiency = self.efficiency_targets.get(vehicle_records[0].fuel_type, 15.0)

        return {
            'status': 'success',
            'average_efficiency_kmpl': round(avg_efficiency, 2),
            'target_efficiency_kmpl': target_efficiency,
            'efficiency_rating': 'excellent' if avg_efficiency >= target_efficiency * 1.1 else
                               'good' if avg_efficiency >= target_efficiency else
                               'poor',
            'recent_efficiency_data': efficiency_data[-5:],  # Last 5 records
            'improvement_potential': max(0, target_efficiency - avg_efficiency)
        }

    async def generate_fuel_report(self, vehicle_id: int, days: int = 30) -> Dict:
        """Generate comprehensive fuel report"""

        cutoff_date = datetime.now() - timedelta(days=days)
        recent_records = [r for r in self.fuel_records
                         if r.vehicle_id == vehicle_id and r.timestamp >= cutoff_date]

        if not recent_records:
            return {'status': 'no_data', 'message': 'No fuel records found for the specified period'}

        # Calculate totals
        total_fuel = sum(r.quantity_liters for r in recent_records)
        total_cost = sum(r.total_cost for r in recent_records)

        # Efficiency analysis
        efficiency_analysis = await self._analyze_fuel_efficiency(vehicle_id)

        # Cost analysis
        cost_analysis = self._analyze_fuel_costs(recent_records)

        # Recommendations
        recommendations = self._generate_fuel_recommendations(efficiency_analysis, cost_analysis)

        return {
            'vehicle_id': vehicle_id,
            'report_period_days': days,
            'summary': {
                'total_fuel_consumed_l': round(total_fuel, 2),
                'total_cost': round(total_cost, 2),
                'average_cost_per_liter': round(total_cost / max(1, total_fuel), 2),
                'number_of_refuels': len(recent_records)
            },
            'efficiency_analysis': efficiency_analysis,
            'cost_analysis': cost_analysis,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }

    def _analyze_fuel_costs(self, records: List[FuelRecord]) -> Dict:
        """Analyze fuel cost patterns"""

        if not records:
            return {}

        # Group by fuel station
        station_costs = {}
        for record in records:
            if record.fuel_station not in station_costs:
                station_costs[record.fuel_station] = []
            station_costs[record.fuel_station].append(record.cost_per_liter)

        # Find cheapest and most expensive stations
        station_averages = {
            station: sum(costs) / len(costs)
            for station, costs in station_costs.items()
        }

        cheapest_station = min(station_averages.items(), key=lambda x: x[1])
        most_expensive_station = max(station_averages.items(), key=lambda x: x[1])

        # Calculate potential savings
        current_avg_cost = sum(r.cost_per_liter for r in records) / len(records)
        potential_savings = (current_avg_cost - cheapest_station[1]) * sum(r.quantity_liters for r in records)

        return {
            'average_cost_per_liter': round(current_avg_cost, 2),
            'cheapest_station': {
                'name': cheapest_station[0],
                'avg_price': round(cheapest_station[1], 2)
            },
            'most_expensive_station': {
                'name': most_expensive_station[0],
                'avg_price': round(most_expensive_station[1], 2)
            },
            'potential_monthly_savings': round(potential_savings, 2),
            'cost_variance': round(most_expensive_station[1] - cheapest_station[1], 2)
        }

    def _generate_fuel_recommendations(self, efficiency_analysis: Dict, cost_analysis: Dict) -> List[str]:
        """Generate fuel optimization recommendations"""
        recommendations = []

        if efficiency_analysis.get('status') == 'success':
            if efficiency_analysis['efficiency_rating'] == 'poor':
                recommendations.append("🔧 Vehicle efficiency below target - schedule maintenance check")
                recommendations.append("🚗 Consider driver training for fuel-efficient driving")

            if efficiency_analysis.get('improvement_potential', 0) > 2:
                recommendations.append(f"📈 Potential to improve efficiency by {efficiency_analysis['improvement_potential']:.1f} km/l")

        if cost_analysis:
            if cost_analysis.get('potential_monthly_savings', 0) > 500:
                recommendations.append(f"💰 Switch to {cost_analysis['cheapest_station']['name']} to save ₹{cost_analysis['potential_monthly_savings']:.0f}/month")

            if cost_analysis.get('cost_variance', 0) > 5:
                recommendations.append("📍 Significant price variation between stations - plan refueling strategically")

        recommendations.extend([
            "📱 Use fuel tracking app for real-time price comparison",
            "⏰ Refuel during off-peak hours for better service",
            "🛣️ Plan routes to include fuel-efficient stations"
        ])

        return recommendations

# Create global instance
fuel_management_service = FuelManagementService()
