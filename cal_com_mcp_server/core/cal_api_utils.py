import httpx
import logging # Added for logger
import json # Added for logging params and headers
from datetime import datetime, timedelta, timezone
import pytz # For timezone conversion

from .config import CAL_COM_API_KEY, CAL_COM_API_BASE_URL, DEFAULT_EVENT_TYPE_ID

logger = logging.getLogger(__name__) # Initialize logger

async def convert_to_utc(local_date_str: str, local_time_str: str, local_timezone_str: str) -> str | None:
    """
    Converts a local date, time, and timezone to an ISO 8601 UTC string.
    Example: local_date_str="2024-12-25", local_time_str="10:00", local_timezone_str="Australia/Sydney"
    Returns: "2024-12-24T23:00:00Z"
    """
    try:
        local_tz = pytz.timezone(local_timezone_str)
        dt_str = f"{local_date_str} {local_time_str}"
        local_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        localized_dt = local_tz.localize(local_dt)
        utc_dt = localized_dt.astimezone(timezone.utc)
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        print(f"Error in convert_to_utc: {e}")
        return None

async def check_availability(
    utc_start_time_iso: str, 
    utc_end_time_iso: str, 
    event_type_id: int
) -> bool:
    """
    Checks slot availability with Cal.com API.
    """
    if not CAL_COM_API_KEY:
        print("Cal.com API key not configured.")
        return False

    url = f"{CAL_COM_API_BASE_URL}/slots"
    params = {
        "eventTypeId": event_type_id,
        "start": utc_start_time_iso, # Changed from startTime to start
        "end": utc_end_time_iso,     # Changed from endTime to end
    }
    headers = {
        "Content-Type": "application/json",
        "apiKey": CAL_COM_API_KEY,
        "cal-api-version": "2024-09-04" # Added based on successful curl
    }
    logger.debug(f"Calling Cal.com /slots API. URL: {url}")
    logger.debug(f"Params for /slots: {json.dumps(params)}")
    logger.debug(f"Headers for /slots: {json.dumps(headers)}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status() # Raise an exception for bad status codes
            data = response.json()
            print(f"Cal.com /slots API response data: {data}") # DEBUG LOG
            
            # The Cal.com /slots API returns data keyed by date, e.g., "2024-08-13"
            # We need to check if any slots are returned for the requested period.
            if data.get("data"):
                print(f"Found 'data' key in response: {data['data']}") # DEBUG LOG
                for date_key in data["data"]:
                    print(f"Processing date_key: {date_key}") # DEBUG LOG
                    if data["data"][date_key]: # Check if the list of slots for this date is not empty
                        print(f"Slots found for {date_key}: {data['data'][date_key]}") # DEBUG LOG
                        for slot in data["data"][date_key]:
                            api_slot_time = slot.get("start")
                            print(f"Checking slot: {api_slot_time} against utc_start_time_iso: {utc_start_time_iso}") # DEBUG LOG
                            # Compare up to the seconds, ignoring milliseconds and 'Z' for a more robust comparison
                            # utc_start_time_iso is like "2025-05-22T03:00:00Z"
                            # api_slot_time is like "2025-05-22T03:00:00.000Z"
                            if api_slot_time and utc_start_time_iso:
                                # Ensure utc_start_time_iso is at least 20 chars "YYYY-MM-DDTHH:MM:SSZ"
                                if len(utc_start_time_iso) >= 20:
                                    compare_str = utc_start_time_iso[:-1] # Remove Z
                                    print(f"Comparing api_slot_time: '{api_slot_time}' with compare_str: '{compare_str}'") # DEBUG LOG
                                    if api_slot_time.startswith(compare_str):
                                        print(f"Slot matched: {api_slot_time}") # DEBUG LOG
                                        return True
                                else:
                                    print(f"utc_start_time_iso '{utc_start_time_iso}' is too short for comparison.") # DEBUG LOG
                            else:
                                print(f"Either api_slot_time or utc_start_time_iso is None. api_slot_time: {api_slot_time}, utc_start_time_iso: {utc_start_time_iso}") # DEBUG LOG
                    else:
                        print(f"No slots list found for date_key: {date_key}") # DEBUG LOG
            else:
                print("No 'data' key found in Cal.com /slots API response.") # DEBUG LOG
            print("Slot not found in check_availability after checking all conditions.") # DEBUG LOG
            return False
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error checking availability: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error in check_availability: {e}")
        return False

async def create_cal_booking_api_call(
    utc_start_time_iso: str,
    event_type_id: int,
    attendee_name: str,
    attendee_email: str,
    attendee_timezone: str
) -> dict:
    """
    Creates a booking using the Cal.com v2 API.
    """
    if not CAL_COM_API_KEY:
        return {"success": False, "error": "Cal.com API key not configured."}

    url = f"{CAL_COM_API_BASE_URL}/bookings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CAL_COM_API_KEY}",
        "cal-api-version": "2024-08-13" # Changed to specific version for /bookings endpoint
    }
    # Construct the attendee object first
    attendee_obj = {
        "name": attendee_name,
        "email": attendee_email,
        "timeZone": attendee_timezone,
        "language": "en" # As per your working example and Cal.com docs for attendee
    }

    # Base payload with required fields in specific order
    payload = {
        "start": utc_start_time_iso,
        "eventTypeId": event_type_id,
        "attendee": attendee_obj
    }

    # Optionally add guests and metadata if they are provided by the calling tool
    # For now, we assume they are not passed directly to this low-level function,
    # but this structure allows for future expansion if the MCP tool schema changes.
    # guests_list = [] # Example: if guests were passed
    # metadata_obj = {} # Example: if metadata was passed
    # if guests_list:
    #     payload["guests"] = guests_list
    # if metadata_obj:
    #     payload["metadata"] = metadata_obj
    
    print(f"Attempting to create booking with payload: {json.dumps(payload, indent=2)}")
    print(f"Using headers: {json.dumps(headers, indent=2)}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers) # Using the 'ordered_payload' which is now just 'payload'
            print(f"Cal.com /bookings API raw response status: {response.status_code}") # DEBUG LOG
            print(f"Cal.com /bookings API raw response content: {response.text}") # DEBUG LOG
            response.raise_for_status()
            return {"success": True, "data": response.json()}
    except httpx.HTTPStatusError as e:
        error_message = f"HTTPStatusError for {e.request.url}: {e.response.status_code}"
        try:
            error_details = e.response.json()
            print(f"{error_message} - JSON Response: {error_details}") # DEBUG LOG
        except ValueError: # If response is not JSON
            error_details = {"error": "Failed to parse error response from Cal.com", "details": e.response.text, "status_code": e.response.status_code}
            print(f"{error_message} - Non-JSON Response: {e.response.text}") # DEBUG LOG
        # Return a consistent error structure
        return {"success": False, "error": f"API Error: {e.response.status_code}", "details": error_details}
    except httpx.RequestError as e:
        print(f"RequestError for {e.request.url}: {str(e)}") # DEBUG LOG
        return {"success": False, "error": "RequestError", "details": f"Cal.com API request failed: {str(e)}"}
    except Exception as e: # Catch any other unexpected errors
        import traceback
        print(f"Unexpected error in create_cal_booking_api_call: {type(e).__name__} - {str(e)}") # DEBUG LOG
        print(traceback.format_exc()) # DEBUG LOG
        return {"success": False, "error": "UnexpectedError", "details": f"An unexpected error occurred: {type(e).__name__} - {str(e)}"}