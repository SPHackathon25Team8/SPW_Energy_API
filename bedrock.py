# bedrock.py
from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from fastapi import Query
import boto3
import json


def get_usage(mode:str,data:list,devices:str) -> dict:
    correctedMode = ""
    if mode == "week":
        correctedMode = "day"
    elif mode == "month":
        correctedMode = "week"
    else:
        correctedMode = "time"

    # Prepare usage data for the model (time + usage only)
    filtered_day_data = [{correctedMode: entry[correctedMode], "usage": entry["usage"]} for entry in data]
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