from typing import List, Dict, Any
from pydantic import BaseModel

class TariffRate(BaseModel):
    period: str  # e.g., "peak", "off-peak", "night", "weekend"
    rate_per_kwh: float  # pence per kWh
    time_range: str  # e.g., "7AM-7PM", "7PM-7AM", "All day"
    days: str  # e.g., "Mon-Fri", "Sat-Sun", "All week"

class Tariff(BaseModel):
    id: str
    name: str
    provider: str
    tariff_type: str  # "fixed", "variable", "time_of_use", "economy_7"
    standing_charge: float  # pence per day
    rates: List[TariffRate]
    description: str
    best_for: str
    annual_estimate_low: float  # £ per year for low usage
    annual_estimate_medium: float  # £ per year for medium usage
    annual_estimate_high: float  # £ per year for high usage

# ScottishPower-only tariff database
tariffs_database = [
    {
        "id": "sp_fix_beatcancer_2026",
        "name": "Beat Cancer Fixed Nov 2026",
        "provider": "ScottishPower",
        "tariff_type": "fixed",
        "standing_charge": 53.0,  # pence/day
        "rates": [
            {
                "period": "all_time",
                "rate_per_kwh": 24.5,  # pence/kWh
                "time_range": "All day",
                "days": "All week"
            }
        ],
        "description": "Fixed rate for 24 months. £10 donated to cancer research per year.",
        "best_for": "Customers wanting budget certainty and to support cancer research",
        "contract_length": "24 months",
        "exit_fee": 0
    },
    {
        "id": "sp_captracker_2026",
        "name": "Cap Tracker Dec 2026",
        "provider": "ScottishPower",
        "tariff_type": "variable",
        "standing_charge": 48.0,
        "rates": [
            {
                "period": "all_time",
                "rate_per_kwh": 23.5,
                "time_range": "All day",
                "days": "All week"
            }
        ],
        "description": "Tracks Ofgem price cap, rates adjust quarterly.",
        "best_for": "Customers who want to follow the price cap with no fixed contract",
        "contract_length": "Rolling monthly",
        "exit_fee": 0
    },
    {
        "id": "sp_greenfixed_2026",
        "name": "Green Fixed Nov 2026",
        "provider": "ScottishPower",
        "tariff_type": "fixed",
        "standing_charge": 55.0,
        "rates": [
            {
                "period": "all_time",
                "rate_per_kwh": 25.5,
                "time_range": "All day",
                "days": "All week"
            }
        ],
        "description": "100% renewable electricity fixed for 24 months.",
        "best_for": "Environmentally conscious customers seeking price certainty",
        "contract_length": "24 months",
        "exit_fee": 0
    },
    {
        "id": "sp_std_var",
        "name": "Standard Variable",
        "provider": "ScottishPower",
        "tariff_type": "variable",
        "standing_charge": 60.0,
        "rates": [
            {
                "period": "all_time",
                "rate_per_kwh": 28.5,
                "time_range": "All day",
                "days": "All week"
            }
        ],
        "description": "Default tariff with rolling monthly contract.",
        "best_for": "Customers who want flexibility with no exit fees",
        "contract_length": "Rolling monthly",
        "exit_fee": 0
    },
    {
        "id": "sp_ev",
        "name": "EV Tariff",
        "provider": "ScottishPower",
        "tariff_type": "time_of_use",
        "standing_charge": 50.0,
        "rates": [
            {
                "period": "off_peak",
                "rate_per_kwh": 8.5,
                "time_range": "12AM-7AM",
                "days": "All week"
            },
            {
                "period": "peak",
                "rate_per_kwh": 38.5,
                "time_range": "7AM-12AM",
                "days": "All week"
            }
        ],
        "description": "Special EV tariff with cheap overnight charging.",
        "best_for": "EV owners charging overnight",
        "contract_length": "12 months",
        "exit_fee": 50
    },
    {
        "id": "sp_smart",
        "name": "Smart Tariff",
        "provider": "ScottishPower",
        "tariff_type": "time_of_use",
        "standing_charge": 52.0,
        "rates": [
            {
                "period": "off_peak",
                "rate_per_kwh": 12.5,
                "time_range": "12AM-7AM",
                "days": "All week"
            },
            {
                "period": "standard",
                "rate_per_kwh": 24.5,
                "time_range": "7AM-4PM, 8PM-12AM",
                "days": "All week"
            },
            {
                "period": "peak",
                "rate_per_kwh": 34.5,
                "time_range": "4PM-8PM",
                "days": "Mon-Fri"
            }
        ],
        "description": "Smart meter required. Cheaper overnight and standard rates.",
        "best_for": "Households with smart meters and flexible usage",
        "contract_length": "12 months",
        "exit_fee": 30
    },
    {
        "id": "sp_heatpump",
        "name": "Heat Pump Tariff",
        "provider": "ScottishPower",
        "tariff_type": "time_of_use",
        "standing_charge": 48.0,
        "rates": [
            {
                "period": "super_off_peak",
                "rate_per_kwh": 9.5,
                "time_range": "2AM-5AM",
                "days": "All week"
            },
            {
                "period": "off_peak",
                "rate_per_kwh": 15.5,
                "time_range": "12AM-2AM, 5AM-7AM, 11PM-12AM",
                "days": "All week"
            },
            {
                "period": "peak",
                "rate_per_kwh": 32.5,
                "time_range": "7AM-11PM",
                "days": "All week"
            }
        ],
        "description": "Special tariff for heat pump households with very cheap super off-peak.",
        "best_for": "Homes with heat pumps and flexible heating schedules",
        "contract_length": "12 months",
        "exit_fee": 50
    }
]

def get_all_tariffs() -> List[Dict[str, Any]]:
    """Return all available tariffs"""
    return tariffs_database

def get_tariff_by_id(tariff_id: str) -> Dict[str, Any]:
    """Get a specific tariff by ID"""
    for tariff in tariffs_database:
        if tariff["id"] == tariff_id:
            return tariff
    return None

def get_tariffs_by_type(tariff_type: str) -> List[Dict[str, Any]]:
    """Get tariffs filtered by type"""
    return [t for t in tariffs_database if t["tariff_type"] == tariff_type]

def calculate_cost_for_usage(tariff: Dict[str, Any], usage_data: List[Dict], period_type: str = "day") -> float:
    """
    Calculate the cost for given usage data using a specific tariff
    
    Args:
        tariff: Tariff dictionary
        usage_data: List of usage entries (day_data, week_data, or month_data format)
        period_type: "day", "week", or "month"
    
    Returns:
        Total cost in pence
    """
    total_cost = 0.0
    
    # Add standing charge (daily)
    if period_type == "day":
        total_cost += tariff["standing_charge"]
    elif period_type == "week":
        total_cost += tariff["standing_charge"] * 7
    elif period_type == "month":
        total_cost += tariff["standing_charge"] * 30
    
    # Calculate usage costs
    for entry in usage_data:
        usage_kwh = entry["usage"]
        
        # Find applicable rate
        applicable_rate = get_applicable_rate(tariff, entry, period_type)
        total_cost += usage_kwh * applicable_rate
    
    return total_cost

def get_applicable_rate(tariff: Dict[str, Any], usage_entry: Dict, period_type: str) -> float:
    """
    Determine which rate applies to a specific usage entry
    """
    # For simple tariffs with one rate
    if len(tariff["rates"]) == 1:
        return tariff["rates"][0]["rate_per_kwh"]
    
    # For time-of-use tariffs, we need to match time periods
    # This is a simplified implementation - in reality you'd need more complex time matching
    
    if period_type == "day":
        time = usage_entry.get("time", "")
        # Simple time-based matching (this could be more sophisticated)
        if "12AM" in time or "2AM" in time or "4AM" in time or "6AM" in time:
            # Night rate
            night_rates = [r for r in tariff["rates"] if "night" in r["period"] or "off_peak" in r["period"]]
            if night_rates:
                return night_rates[0]["rate_per_kwh"]
        elif "6PM" in time or "8PM" in time:
            # Peak rate
            peak_rates = [r for r in tariff["rates"] if "peak" in r["period"]]
            if peak_rates:
                return peak_rates[0]["rate_per_kwh"]
    
    elif period_type == "week":
        day = usage_entry.get("day", "")
        if day in ["Sat", "Sun"]:
            weekend_rates = [r for r in tariff["rates"] if "weekend" in r["period"]]
            if weekend_rates:
                return weekend_rates[0]["rate_per_kwh"]
    
    # Default to standard rate or first rate
    standard_rates = [r for r in tariff["rates"] if "standard" in r["period"] or "all_time" in r["period"]]
    if standard_rates:
        return standard_rates[0]["rate_per_kwh"]
    
    return tariff["rates"][0]["rate_per_kwh"]

def recommend_best_tariff(usage_data: List[Dict], period_type: str = "day") -> Dict[str, Any]:
    """
    Recommend the best tariff based on usage patterns
    
    Args:
        usage_data: Usage data (day_data, week_data, or month_data format)
        period_type: "day", "week", or "month"
    
    Returns:
        Dictionary with recommendation details
    """
    recommendations = []
    
    for tariff in tariffs_database:
        cost = calculate_cost_for_usage(tariff, usage_data, period_type)
        
        recommendations.append({
            "tariff": tariff,
            "estimated_cost": cost,
            "cost_per_kwh_avg": cost / sum(entry["usage"] for entry in usage_data) if usage_data else 0
        })
    
    # Sort by cost (lowest first)
    recommendations.sort(key=lambda x: x["estimated_cost"])
    
    best_tariff = recommendations[0]
    
    # Analyze usage patterns for additional insights
    usage_analysis = analyze_usage_patterns(usage_data, period_type)
    
    return {
        "recommended_tariff": best_tariff["tariff"],
        "estimated_cost": best_tariff["estimated_cost"],
        "potential_savings": recommendations[-1]["estimated_cost"] - best_tariff["estimated_cost"],
        "usage_analysis": usage_analysis,
        "all_options": recommendations[:5]  # Top 5 options
    }

def analyze_usage_patterns(usage_data: List[Dict], period_type: str) -> Dict[str, Any]:
    """
    Analyze usage patterns to provide insights for tariff selection
    """
    if not usage_data:
        return {}
    
    total_usage = sum(entry["usage"] for entry in usage_data)
    
    analysis = {
        "total_usage": total_usage,
        "average_usage": total_usage / len(usage_data),
        "peak_usage": max(entry["usage"] for entry in usage_data),
        "min_usage": min(entry["usage"] for entry in usage_data),
    }
    
    if period_type == "day":
        # Analyze time-based patterns
        night_usage = sum(entry["usage"] for entry in usage_data 
                         if entry.get("time") in ["12AM", "2AM", "4AM", "6AM"])
        day_usage = total_usage - night_usage
        
        analysis.update({
            "night_usage_percentage": (night_usage / total_usage) * 100 if total_usage > 0 else 0,
            "day_usage_percentage": (day_usage / total_usage) * 100 if total_usage > 0 else 0,
            "suitable_for_economy7": night_usage / total_usage > 0.3 if total_usage > 0 else False
        })
        
    elif period_type == "week":
        # Analyze weekly patterns
        weekend_usage = sum(entry["usage"] for entry in usage_data 
                           if entry.get("day") in ["Sat", "Sun"])
        weekday_usage = total_usage - weekend_usage
        
        analysis.update({
            "weekend_usage_percentage": (weekend_usage / total_usage) * 100 if total_usage > 0 else 0,
            "weekday_usage_percentage": (weekday_usage / total_usage) * 100 if total_usage > 0 else 0,
            "weekend_heavy_user": weekend_usage > weekday_usage
        })
    
    return analysis