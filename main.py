from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from fastapi import Query

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

# Static data for the "day" endpoint
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
def get_week_usage():
    return week_data

@app.get("/month", response_model=List[UsageMonthEntry])
def get_month_usage():
    return month_data

@app.get("/aiinsights", response_model=List[AiInsights])
def get_ai_insights(period: str = Query(...)):
    if period == "day":
        return ai_insights_day
    elif period == "week":
        return ai_insights_week
    elif period == "month":
        return ai_insights_month
    else:
        return []

