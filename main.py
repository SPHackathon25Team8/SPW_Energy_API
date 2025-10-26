from fastapi import FastAPI
from typing import List
from pydantic import BaseModel

app = FastAPI()

# Define the data model
class UsageEntry(BaseModel):
    time: str
    usage: float
    devices: List[str]

# Static data for the "day" endpoint
day_data = [
    {"time": "12AM", "usage": 1.2, "devices": ["fridge", "tv"]},
    {"time": "2AM", "usage": 0.8, "devices": ["fridge"]},
    {"time": "4AM", "usage": 0.9, "devices": ["fridge"]},
    {"time": "6AM", "usage": 1.5, "devices": ["fridge", "kettle"]},
    {"time": "8AM", "usage": 2.3, "devices": ["fridge", "washing-machine", "tv"]},
    {"time": "10AM", "usage": 1.8, "devices": ["fridge", "dishwasher"]},
    {"time": "12PM", "usage": 2.1, "devices": ["fridge", "oven", "tv"]},
    {"time": "2PM", "usage": 2.5, "devices": ["fridge", "dryer", "computer"]},
    {"time": "4PM", "usage": 2.2, "devices": ["fridge", "tv", "computer"]},
    {"time": "6PM", "usage": 3.8, "devices": ["fridge", "oven", "tv", "dishwasher"]},
    {"time": "8PM", "usage": 3.4, "devices": ["fridge", "tv", "washing-machine", "ev-car"]},
    {"time": "10PM", "usage": 2.1, "devices": ["fridge", "tv"]},
]

@app.get("/day", response_model=List[UsageEntry])
def get_day_usage():
    return day_data
