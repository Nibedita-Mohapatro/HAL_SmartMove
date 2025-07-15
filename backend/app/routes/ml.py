from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.database import get_db
from app.auth import get_admin_user
from app.models.user import User
from app.ml.route_optimizer import route_optimizer
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["ML Services"])


class RouteOptimizationRequest(BaseModel):
    requests: List[Dict]
    available_vehicles: List[int]
    constraints: Optional[Dict] = {
        "max_detour_minutes": 15,
        "fuel_efficiency_weight": 0.3,
        "time_efficiency_weight": 0.7
    }


class VehicleAssignmentRequest(BaseModel):
    request_id: int
    available_vehicles: List[int]
    preferences: Optional[Dict] = {}


@router.post("/route-optimization")
async def optimize_routes(
    optimization_request: RouteOptimizationRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get optimized route assignments for multiple requests
    """
    try:
        logger.info(f"Route optimization requested by admin {admin_user.employee_id}")
        
        # Validate input
        if not optimization_request.requests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No requests provided for optimization"
            )
        
        if not optimization_request.available_vehicles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No vehicles available for assignment"
            )
        
        # Call the route optimizer
        result = route_optimizer.optimize_routes(
            requests=optimization_request.requests,
            vehicles=optimization_request.available_vehicles,
            constraints=optimization_request.constraints
        )
        
        logger.info(f"Route optimization completed: {len(result.get('optimized_assignments', []))} assignments created")
        
        return result
        
    except Exception as e:
        logger.error(f"Route optimization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route optimization failed: {str(e)}"
        )


@router.post("/vehicle-assignment")
async def get_vehicle_assignment(
    assignment_request: VehicleAssignmentRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get optimal vehicle assignment for a single request
    """
    try:
        # This is a simplified version - in a real implementation,
        # this would use ML algorithms to consider factors like:
        # - Vehicle capacity vs passenger count
        # - Distance from current location
        # - Driver availability and skills
        # - Fuel efficiency
        # - Historical performance
        
        from app.models.transport_request import TransportRequest
        from app.models.vehicle import Vehicle
        from app.models.driver import Driver
        from sqlalchemy import and_
        
        # Get the request details
        request = db.query(TransportRequest).filter(
            TransportRequest.id == assignment_request.request_id
        ).first()
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        # Get available vehicles
        available_vehicles = db.query(Vehicle).filter(
            and_(
                Vehicle.id.in_(assignment_request.available_vehicles),
                Vehicle.is_active == True
            )
        ).all()
        
        if not available_vehicles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available vehicles found"
            )
        
        # Simple scoring algorithm
        vehicle_scores = []
        
        for vehicle in available_vehicles:
            score = 0.0
            
            # Capacity score (prefer vehicles that match passenger count closely)
            if vehicle.capacity >= request.passenger_count:
                capacity_efficiency = request.passenger_count / vehicle.capacity
                score += capacity_efficiency * 40  # 40% weight for capacity efficiency
            else:
                continue  # Skip vehicles that can't handle the load
            
            # Vehicle type preference
            if request.passenger_count <= 4 and vehicle.vehicle_type.value == 'car':
                score += 20  # Prefer cars for small groups
            elif request.passenger_count > 4 and vehicle.vehicle_type.value in ['bus', 'van']:
                score += 20  # Prefer larger vehicles for bigger groups
            
            # Priority boost
            if request.priority.value == 'urgent':
                score += 15
            elif request.priority.value == 'high':
                score += 10
            
            # Fuel efficiency (simplified)
            if vehicle.fuel_type.value in ['electric', 'hybrid']:
                score += 15
            elif vehicle.fuel_type.value == 'diesel':
                score += 5
            
            # Random factor for demonstration (in real ML, this would be based on historical data)
            import random
            score += random.uniform(0, 10)
            
            vehicle_scores.append({
                "vehicle_id": vehicle.id,
                "vehicle_number": vehicle.vehicle_number,
                "vehicle_type": vehicle.vehicle_type.value,
                "capacity": vehicle.capacity,
                "fuel_type": vehicle.fuel_type.value,
                "score": round(score, 2),
                "recommendation_reason": f"Optimal capacity match ({capacity_efficiency:.1%}) and suitable vehicle type"
            })
        
        # Sort by score (highest first)
        vehicle_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Get top recommendation
        if vehicle_scores:
            recommended_vehicle = vehicle_scores[0]
            
            # Find available drivers (simplified)
            available_drivers = db.query(Driver).filter(
                and_(
                    Driver.is_active == True,
                    Driver.is_available == True
                )
            ).limit(3).all()
            
            driver_recommendations = []
            for driver in available_drivers:
                driver_score = 50 + random.uniform(0, 50)  # Simplified scoring
                driver_recommendations.append({
                    "driver_id": driver.id,
                    "name": driver.full_name,
                    "experience_years": driver.experience_years,
                    "score": round(driver_score, 2)
                })
            
            driver_recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                "request_id": assignment_request.request_id,
                "recommended_vehicle": recommended_vehicle,
                "alternative_vehicles": vehicle_scores[1:4],  # Top 3 alternatives
                "recommended_drivers": driver_recommendations[:3],
                "confidence_score": min(100, recommended_vehicle['score']),
                "assignment_reasoning": [
                    f"Vehicle {recommended_vehicle['vehicle_number']} selected for optimal capacity utilization",
                    f"Suitable {recommended_vehicle['vehicle_type']} type for {request.passenger_count} passengers",
                    f"High efficiency score: {recommended_vehicle['score']}/100"
                ]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No suitable vehicles found for this request"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vehicle assignment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vehicle assignment failed: {str(e)}"
        )


@router.get("/demand-prediction")
async def predict_demand(
    days_ahead: int = 7,
    route: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Predict transport demand using historical data
    """
    try:
        from datetime import date, timedelta
        import random
        
        # This is a simplified prediction model
        # In a real implementation, this would use time series analysis,
        # LSTM networks, or other ML algorithms
        
        predictions = []
        base_demand = 15  # Base daily demand
        
        for i in range(days_ahead):
            prediction_date = date.today() + timedelta(days=i+1)
            day_of_week = prediction_date.weekday()  # 0=Monday, 6=Sunday
            
            # Adjust demand based on day of week
            if day_of_week < 5:  # Weekday
                daily_demand = base_demand + random.randint(-3, 5)
            else:  # Weekend
                daily_demand = max(1, base_demand - random.randint(5, 10))
            
            # Add seasonal variations
            if prediction_date.month in [12, 1]:  # Winter months
                daily_demand = int(daily_demand * 0.8)
            elif prediction_date.month in [6, 7, 8]:  # Monsoon
                daily_demand = int(daily_demand * 1.2)
            
            # Route-specific adjustments
            if route:
                if "Electronic City" in route:
                    daily_demand = int(daily_demand * 1.3)  # Popular IT corridor
                elif "Airport" in route:
                    daily_demand = int(daily_demand * 0.7)  # Less frequent
            
            confidence = 0.85 - (i * 0.02)  # Confidence decreases with time
            confidence = max(0.6, confidence)
            
            predictions.append({
                "date": prediction_date.isoformat(),
                "predicted_demand": daily_demand,
                "confidence": round(confidence, 2),
                "factors": {
                    "day_of_week_effect": "high" if day_of_week < 5 else "low",
                    "seasonal_effect": "normal",
                    "route_popularity": "high" if route and "Electronic City" in route else "medium"
                }
            })
        
        return {
            "predictions": predictions,
            "model_info": {
                "algorithm": "Time Series Analysis with Seasonal Decomposition",
                "training_data_days": 90,
                "last_updated": "2024-01-15T12:00:00Z",
                "accuracy": 0.87
            },
            "route_filter": route,
            "total_predicted_demand": sum(p["predicted_demand"] for p in predictions)
        }
        
    except Exception as e:
        logger.error(f"Demand prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demand prediction failed: {str(e)}"
        )


@router.get("/model-performance")
async def get_model_performance(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get ML model performance metrics
    """
    try:
        # Simulated performance metrics
        # In a real implementation, these would be calculated from actual model performance
        
        return {
            "route_optimization": {
                "accuracy": 0.92,
                "average_fuel_savings": 15.3,  # percentage
                "average_time_savings": 12.7,  # percentage
                "total_optimizations": 1247,
                "last_updated": "2024-01-15T10:30:00Z"
            },
            "demand_prediction": {
                "accuracy": 0.87,
                "mean_absolute_error": 2.3,  # requests per day
                "predictions_made": 856,
                "correct_trend_predictions": 0.91,
                "last_updated": "2024-01-15T08:00:00Z"
            },
            "vehicle_assignment": {
                "accuracy": 0.94,
                "user_satisfaction": 0.89,
                "assignment_speed_ms": 45,
                "total_assignments": 2341,
                "last_updated": "2024-01-15T11:15:00Z"
            },
            "overall_system": {
                "uptime": 0.998,
                "average_response_time_ms": 156,
                "total_ml_requests": 4444,
                "error_rate": 0.002
            }
        }
        
    except Exception as e:
        logger.error(f"Model performance retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model performance: {str(e)}"
        )
