import logging
import datetime
import json
from typing import Optional, Dict
from fastapi import Request
from uuid import uuid4

# Initialize logger
logger = logging.getLogger("activity_tracker")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("activity_logs.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# --- Activity Tracker --- #

def log_user_activity(
    request: Request,
    action: str,
    user_id: Optional[str] = None,
    metadata: Optional[Dict] = None,
):
    """
    Logs detailed user activity for RLG Data and RLG Fans platform.

    Parameters:
    - request: HTTP request object
    - action: Description of the action performed
    - user_id: ID of the user (if available)
    - metadata: Additional context (scraping actions, pricing region, AI tool usage, etc.)
    """
    try:
        client_host = request.client.host
        user_agent = request.headers.get("User-Agent")
        geo_data = request.headers.get("Geo-Location", "N/A")

        log_entry = {
            "activity_id": str(uuid4()),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "user_id": user_id,
            "client_ip": client_host,
            "geo_data": geo_data,
            "user_agent": user_agent,
            "action": action,
            "metadata": metadata or {},
        }

        logger.info(json.dumps(log_entry))

    except Exception as e:
        logger.error(f"Failed to log activity: {e}")


# --- Examples of usage --- #
# These examples would be used throughout services like scraping, pricing logic, AI tools, etc.

async def track_scraping_activity(request: Request, user_id: str, tool_name: str, keywords: list):
    log_user_activity(
        request=request,
        action="Data scraping initiated",
        user_id=user_id,
        metadata={
            "tool": tool_name,
            "keywords": keywords,
        },
    )

async def track_ai_insight_usage(request: Request, user_id: str, feature_name: str):
    log_user_activity(
        request=request,
        action="AI Insights used",
        user_id=user_id,
        metadata={
            "feature": feature_name
        },
    )

async def track_pricing_selection(request: Request, user_id: str, region: str, pricing_tier: str):
    locked_region = "Israel (Special Region)" if region.lower() == "israel" else region
    log_user_activity(
        request=request,
        action="Pricing tier viewed",
        user_id=user_id,
        metadata={
            "region": locked_region,
            "pricing": pricing_tier,
        },
    )

async def track_newsletter_signup(request: Request, user_id: str, email: str):
    log_user_activity(
        request=request,
        action="RLG Newsletter signup",
        user_id=user_id,
        metadata={
            "email": email
        },
    )

async def track_super_tool_usage(request: Request, user_id: str, module: str, inputs: dict):
    log_user_activity(
        request=request,
        action="RLG Super Tool module triggered",
        user_id=user_id,
        metadata={
            "module": module,
            "inputs": inputs
        },
    )

async def track_rlg_agent_chat(request: Request, user_id: str, message: str):
    log_user_activity(
        request=request,
        action="RLG Agent Chat interaction",
        user_id=user_id,
        metadata={
            "message": message
        },
    )
