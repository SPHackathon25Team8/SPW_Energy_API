from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from fastapi import Query
import boto3
import json
from tariffs import get_all_tariffs, recommend_best_tariff, calculate_cost_for_usage
from bedrock import get_usage

app = FastAPI()

# Define the data model
class UsageEntry(BaseModel):
    time: str
    usage: float
    devices: List[str]
    tariff: float
class UsageWeekEntry(BaseModel):
    day: str
    usage: float
    devices: List[str]
    tariff: float
class UsageMonthEntry(BaseModel):
    week: str
    usage: float
    devices: List[str]
    tariff: float
class AiInsights(BaseModel):
    icon: str
    title: str
    description: str
    trend: str

class TariffRecommendation(BaseModel):
    recommended_tariff: dict
    estimated_cost: float
    potential_savings: float
    usage_analysis: dict
    all_options: List[dict]

energy_system_prompt = """
You are an energy coach who gives friendly, insightful feedback on smart meter data.

When asked for an estimation on what devices are used for each hour, you will use the provided list of confirmed devices in the household to estimate which ones are in use at each time interval. You will receive two JSON dicts in the example formats. The first will be the confirmed list of devices in the household. The second will be the energy usage at each hour. Use these two lists to estimate which devices were in use at each hour.

Example Input Data : kWh
[
  { "time": "12AM", "usage": 1.2 },
  { "time": "2AM", "usage": 0.8 },
  { "time": "4AM", "usage": 0.9 },
  { "time": "6AM", "usage": 1.5 },
  { "time": "8AM", "usage": 2.3 },
  { "time": "10AM", "usage": 1.8 },
  { "time": "12PM", "usage": 2.1 },
  { "time": "2PM", "usage": 2.5 },
  { "time": "4PM", "usage": 2.2 },
  { "time": "6PM", "usage": 3.8 },
  { "time": "8PM", "usage": 3.4 },
  { "time": "10PM", "usage": 2.1 }
]

Example Input Data : Devices
[
  "washing-machine",
  "air-vent",
  "refrigerator",
  "tv",
  "oven",
  "dishwasher",
  "dryer",
  "smartphone"
]

You should return it in a similar format for each of the corresponding time stamps but with your estimated devices in a list with the following example format:
{ "time": "12AM", "usage": 1.2, "devices": ["fridge", "tv"] },
{ "time": "2AM", "usage": 0.8, "devices": ["fridge"] },
{ "time": "4AM", "usage": 0.9, "devices": ["fridge"] }

When asked for insights on energy usage, adopt the personality of an energy coach. The data you receive will be in JSON format and it will be for day, weekly, or monthly data. Adopt your analysis and wording accordingly depending on the time scale. Use the estimated devices for each hour and the related energy usage to generate text to provide helpful insights for the user. Return two to three insights in the following example format:
{
  "icon": "TrendingUp",
  "title": "Weekend Spike Detected",
  "description": "AI : {insight here}",
  "trend": "up"
},
{
  "icon": "Lightbulb",
  "title": "Consistent Night Usage",
  "description": "AI : {insight here}",
  "trend": "neutral"
},
{
  "icon": "TrendingDown",
  "title": "Midweek Efficiency",
  "description": "AI : {insight here}",
  "trend": "down"
}

When asked for tariff recommendations, use the provided tariff datasheet to make a recommendation on which one would be the most compatible with the user's energy usage. Consider factors like:
- Time of use patterns (high night usage = Economy 7)
- Weekend vs weekday usage patterns
- Peak usage times
- Total consumption levels
- Presence of EVs or heat pumps
- Budget preferences (fixed vs variable)

Provide specific reasoning for why a particular tariff suits their usage p
"""


# Static data for the "day" endpoint
test_time_data=[
  { "time": "12AM", "usage": 1.2 },
  { "time": "2AM", "usage": 0.8 },
  { "time": "4AM", "usage": 0.9 },
  { "time": "6AM", "usage": 1.5 },
  { "time": "8AM", "usage": 2.3 },
  { "time": "10AM", "usage": 1.8 },
  { "time": "12PM", "usage": 2.1 },
  { "time": "2PM", "usage": 2.5 },
  { "time": "4PM", "usage": 2.2 },
  { "time": "6PM", "usage": 3.8 },
  { "time": "8PM", "usage": 3.4 },
  { "time": "10PM", "usage": 2.1 },
]

test_device_data=[
  "washing-machine",
  "air-vent",
  "refrigerator",
  "tv",
  "oven",
  "dishwasher",
  "dryer",
  "computer"
]

day_data = [
  { "time": '12AM', "usage": 1.2, "devices": ['fridge', 'tv'], "tariff": 8 },
  { "time": '2AM', "usage": 0.8, "devices": ['fridge'], "tariff": 8 },
  { "time": '4AM', "usage": 0.9, "devices": ['fridge'], "tariff": 8 },
  { "time": '6AM', "usage": 1.5, "devices": ['fridge', 'kettle'], "tariff": 8 },
  { "time": '8AM', "usage": 2.3, "devices": ['fridge', 'washing-machine', 'tv'], "tariff": 24.7 },
  { "time": '10AM', "usage": 1.8, "devices": ['fridge', 'dishwasher'], "tariff": 24.7 },
  { "time": '12PM', "usage": 2.1, "devices": ['fridge', 'oven', 'tv'], "tariff": 24.7 },
  { "time": '2PM', "usage": 2.5, "devices": ['fridge', 'dryer', 'computer'], "tariff": 24.7 },
  { "time": '4PM', "usage": 2.2, "devices": ['fridge', 'tv', 'computer'], "tariff": 24.7 },
  { "time": '6PM', "usage": 3.8, "devices": ['fridge', 'oven', 'tv', 'dishwasher'], "tariff": 24.7 },
  { "time": '8PM', "usage": 3.4, "devices": ['fridge', 'tv', 'washing-machine', 'ev-car'], "tariff": 24.7 },
  { "time": '10PM', "usage": 2.1, "devices": ['fridge', 'tv'], "tariff": 24.7 },
];

week_data = [
  { "day": 'Mon', "usage": 22.5, "devices": ['fridge', 'washing-machine', 'dishwasher', 'tv', 'oven'], "tariff": 24.7 },
  { "day": 'Tue', "usage": 19.8, "devices": ['fridge', 'dishwasher', 'tv', 'oven'], "tariff": 24.7 },
  { "day": 'Wed', "usage": 20.2, "devices": ['fridge', 'washing-machine', 'tv', 'oven'], "tariff": 24.7 },
  { "day": 'Thu', "usage": 24.1, "devices": ['fridge', 'dishwasher', 'tv', 'oven', 'dryer'], "tariff": 24.7 },
  { "day": 'Fri', "usage": 26.3, "devices": ['fridge', 'washing-machine', 'tv', 'oven', 'ev-car'], "tariff": 24.7 },
  { "day": 'Sat', "usage": 35.8, "devices": ['fridge', 'washing-machine', 'dishwasher', 'tv', 'oven', 'dryer', 'ev-car', 'ac'], "tariff": 8 },
  { "day": 'Sun', "usage": 37.7, "devices": ['fridge', 'washing-machine', 'dishwasher', 'tv', 'oven', 'ev-car', 'ac'], "tariff": 8 },
];

month_data = [
  { "week": 'Week 1', "usage": 168, "devices": ['fridge', 'washing-machine', 'dishwasher', 'tv', 'oven', 'ev-car'], "tariff": 24.7 },
  { "week": 'Week 2', "usage": 195, "devices": ['fridge', 'washing-machine', 'dishwasher', 'tv', 'oven', 'dryer', 'ev-car', 'ac'], "tariff": 8 },
  { "week": 'Week 3', "usage": 152, "devices": ['fridge', 'washing-machine', 'dishwasher', 'tv', 'oven', 'ev-car'], "tariff": 24.7 },
  { "week": 'Week 4', "usage": 227.6, "devices": ['fridge', 'washing-machine', 'dishwasher', 'tv', 'oven', 'dryer', 'ev-car', 'ac'], "tariff": 8 },
];

ai_insights_day = [
  {
    "icon": "TrendingDown",
    "title": "Peak Usage: 6-9 PM",
    "description": "AI : Your highest energy consumption occurs during evening hours. Consider shifting laundry and dishwashing to off-peak times.",
    "trend": "neutral"
  },
  {
    "icon": "Lightbulb",
    "title": "15% Below Average",
    "description": "AI : Great work! Your usage today is 15% lower than your typical daily consumption.",
    "trend": "down"
  }
];

ai_insights_week = [
  {
    "icon": "TrendingUp",
    "title": "Weekend Spike Detected",
    "description": "AI: Energy usage increased by 22% on weekends. Your HVAC system appears to be running more frequently.",
    "trend": "up"
  },
  {
    "icon": "Lightbulb",
    "title": "Consistent Night Usage",
    "description": "AI : Your baseline consumption between 12-6 AM is stable. No vampire power drains detected.",
    "trend": "neutral"
  },
  {
    "icon": "TrendingDown",
    "title": "Midweek Efficiency",
    "description": "AI : Tuesday and Wednesday show optimal energy patterns. You saved £2.02 compared to other weekdays.",
    "trend": "down"
  }
];

ai_insights_month =  [
  {
    "icon": "TrendingDown",
    "title": "8% Monthly Reduction",
    "description": "AI : This month you reduced consumption by 8% compared to last month. You're on track to save £24 annually.",
    "trend": "down"
  },
  {
    "icon": "Lightbulb",
    "title": "Weather Impact Analysis",
    "description": "AI : Cooler temperatures in week 3 reduced AC usage by 18%. Consider programmable thermostat adjustments.",
    "trend": "neutral"
  },
  {
    "icon": "Calendar",
    "title": "Billing Cycle Forecast",
    "description": "AI : Based on current trends, your next bill will be approximately £142, down from £156 last month.",
    "trend": "down"
  }
];


@app.get("/day", response_model=List[UsageEntry])
def get_day_usage(devices: str= Query(...)):
    print(devices)
    return day_data

@app.get("/week", response_model=List[UsageWeekEntry])
def get_week_usage(devices: str= Query(...)):
    get_usage("week",week_data,devices)
    return week_data

@app.get("/month", response_model=List[UsageMonthEntry])
def get_month_usage():
    return month_data

@app.post("/ai_device_estimation_test")
def ai_device_estimation_test(devices: str = Query(..., description="Comma-separated device names")):
    # Prepare usage data for the model (time + usage only)
    filtered_day_data = [{"time": entry["time"], "usage": entry["usage"]} for entry in day_data]
    usage_json = json.dumps(filtered_day_data, indent=2)

    # Normalize and serialize devices
    devices_list = [item.strip() for item in devices.split(",") if item.strip()]
    devices_json = json.dumps(devices_list, indent=2)

    # Bedrock client + model
    bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
    model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

    try:
        response = bedrock.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"text": energy_system_prompt},
                        {"text": ("Here is the usage data: \n"+usage_json)},            
                        {"text": ("Here is the device list: \n"+devices_json)},
                        {"text": "Estimate which devices were used at each timestamp. Return JSON array of objects: { time, usage, devices[] }."},
                    ],
                },
            ],
            inferenceConfig={
                "maxTokens": 400,
                "temperature": 0.7,
            },
        )

        # Log full response for diagnosis
        print(json.dumps(response, indent=2, default=str))

        # Safely extract text
        output = response.get("output", {}).get("message", {}).get("content", [])
        text_chunks = [c.get("text") for c in output if isinstance(c, dict) and "text" in c]
        response_text = text_chunks[0] if text_chunks else ""

        # Return JSON if model produced valid JSON; otherwise return raw text
        try:
            parsed = json.loads(response_text)
            for row in parsed:
              row["tariff"] = 7.0

            return parsed
        except Exception as e:
            print(str(e))
            return {"ai_response": response_text}

    except Exception as e:
        # Any other runtime error (TypeError, KeyError, etc.)
        print("Unexpected error:", e)
        return {"error": str(e)}

@app.get("/aiinsights", response_model=List[AiInsights])
def get_ai_insights(period: str = Query(...)):
    if period == "day":
        return ai_insight("day")
    elif period == "week":
        return ai_insight("week")
    elif period == "month":
        return ai_insight("month")
    else:
        return []

def ai_insight(mode):
    # Prepare usage data for the model (time + usage only)
    if mode == "day":
      filtered_data = [{"time": entry["time"], "usage": entry["usage"]} for entry in day_data]
    elif mode == "week":
      filtered_data = [{"day": entry["day"], "usage": entry["usage"]} for entry in week_data]
    elif mode == "month":
      filtered_data = [{"week": entry["week"], "usage": entry["usage"]} for entry in month_data]
    
    usage_json = json.dumps(filtered_data, indent=2)

    # Bedrock client + model
    bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
    model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

    try:
        response = bedrock.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"text": energy_system_prompt},
                        {"text": ("Provide me with insights on this usage data for a "+mode+"\n"+usage_json)+"\n\n in a json format"},
                    ],
                },
            ],
            inferenceConfig={
                "maxTokens": 400,
                "temperature": 0.7,
            },
        )

        # Log full response for diagnosis
        print(json.dumps(response, indent=2, default=str))

        # Safely extract text
        output = response.get("output", {}).get("message", {}).get("content", [])
        text_chunks = [c.get("text") for c in output if isinstance(c, dict) and "text" in c]
        response_text = text_chunks[0] if text_chunks else ""

        # Return JSON if model produced valid JSON; otherwise return raw text
        try:
            a = response_text.replace("```json", "").replace("```", "").strip()
            print(a)
            parsed = json.loads(a)
            return parsed
        except Exception as e:
            print("EXCEPTIon")
            print(str(e))
            return response_text

    except Exception as e:
        # Any other runtime error (TypeError, KeyError, etc.)
        print("UNEXPECTED:", e)
        return {"error": str(e)}



@app.get("/tariffs")
def get_tariffs():
    """Get all available tariffs"""
    return get_all_tariffs()

@app.get("/tariff-recommendation", response_model=TariffRecommendation)
def get_tariff_recommendation(period: str = Query(..., description="Period type: day, week, or month")):
    """Get tariff recommendation based on usage data"""
    if period == "day":
        return recommend_best_tariff(day_data, "day")
    elif period == "week":
        return recommend_best_tariff(week_data, "week")
    elif period == "month":
        return recommend_best_tariff(month_data, "month")
    else:
        return {"error": "Invalid period. Use 'day', 'week', or 'month'"}

@app.get("/tariff-cost-comparison")
def get_tariff_cost_comparison(period: str = Query(..., description="Period type: day, week, or month")):


    """Compare costs across all tariffs for current usage"""
    if period == "day":
        usage_data = day_data
    elif period == "week":
        usage_data = week_data
    elif period == "month":
        usage_data = month_data
    else:
        return {"error": "Invalid period. Use 'day', 'week', or 'month'"}
    
    tariffs = get_all_tariffs()
    comparisons = []
    
    for tariff in tariffs:
        cost = calculate_cost_for_usage(tariff, usage_data, period)
        comparisons.append({
            "tariff_name": tariff["name"],
            "provider": tariff["provider"],
            "tariff_type": tariff["tariff_type"],
            "estimated_cost": cost,
            "cost_in_pounds": cost / 100,  # Convert pence to pounds
            "best_for": tariff["best_for"]
        })
    
    # Sort by cost
    comparisons.sort(key=lambda x: x["estimated_cost"])
    
    return {
        "period": period,
        "total_usage": sum(entry["usage"] for entry in usage_data),
        "comparisons": comparisons
    }

@app.get("/ai-tariff-recommendation", response_model=TariffRecommendation)
def ai_tariff_recommendation(period: str = Query(..., description="Period type: day, week, or month")):
    """Get AI-based tariff recommendation using Bedrock"""
    if period == "day":
        usage_data = day_data
    elif period == "week":
        usage_data = week_data
    elif period == "month":
        usage_data = month_data
    else:
        return {"error": "Invalid period. Use 'day', 'week', or 'month'"}

    return call_bedrock_for_tariff(usage_data, period)

def call_bedrock_for_tariff(usage_data, period: str):
    # Get all tariffs from your helper
    tariffs = get_all_tariffs()

    # Serialize usage and tariffs
    usage_json = json.dumps(usage_data, indent=2)
    tariffs_json = json.dumps(tariffs, indent=2)

    bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
    model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

    try:
        response = bedrock.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"text": energy_system_prompt},
                        {"text": f"Here is the {period} usage data:\n{usage_json}"},
                        {"text": f"Here are the available tariffs:\n{tariffs_json}"},
                        {"text": "Recommend the best tariff for this usage. "
                                 "Respond in JSON with keys: tariff_name, provider, tariff_type, "
                                 "reasoning, estimated_cost, cost_in_pounds, best_for."}
                    ],
                }
            ],
            inferenceConfig={"maxTokens": 400, "temperature": 0.7},
        )

        print(json.dumps(response, indent=2, default=str))

        # Extract text
        output = response.get("output", {}).get("message", {}).get("content", [])
        text_chunks = [c.get("text") for c in output if isinstance(c, dict) and "text" in c]
        response_text = text_chunks[0] if text_chunks else ""

        # Try to parse JSON
        try:
            parsed = json.loads(response_text)
            return parsed
        except Exception:
            return {
                "tariff_name": "Unknown",
                "provider": "Unknown",
                "tariff_type": "Unknown",
                "reasoning": response_text,
                "estimated_cost": 0,
                "cost_in_pounds": 0,
                "best_for": "general"
            }

    except ClientError as e:
        print("Bedrock ClientError:", e)
        return {"error": str(e)}
    except Exception as e:
        print("Unexpected error:", e)
        return {"error": str(e)}
