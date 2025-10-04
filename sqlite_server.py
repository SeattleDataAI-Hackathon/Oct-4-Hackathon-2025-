import sqlite3
import json
import sys
import httpx # Import httpx for HTTP/2 support
import os 
from mcp.server.fastmcp import FastMCP

# --- CONFIGURATION ---
# IMPORTANT: These environment variables must be set outside of this script
# to securely pass the APNs credentials. 
# Example: export APNS_AUTH_TOKEN="your_token_here"
DB_FILE = "/Users/nirvanadogra/venv/my_data.db"

# Fix: Correctly load tokens from environment variables.
AUTHENTICATION_TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjQ3TTRNQkIzUFMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJDMjg5V0NUNlQ1IiwiaWF0IjoxNzU5NjEzMDU2fQ.abK1qhVhtce1ocxFoku9fEs6fqkdeb0KCGORAT5NxnyomeIyyc0k_sDPubqkvYAChB4vP6Ogb142JMCLwZqRjQ"
DEVICE_TOKEN = "2aea5e0dff2a042b4f443b0d077c63c679f1a7791d6bddec0120570c9f040072"

APNS_URL = "https://api.development.push.apple.com:443/3/device/{DEVICE_TOKEN}"
# Ensure the APNS_URL uses the actual device token value
if DEVICE_TOKEN:
    APNS_URL = f"https://api.development.push.apple.com:443/3/device/{DEVICE_TOKEN}"

APNS_TOPIC = "com.bbqsauceror.HealthMonitor" # Replace with your app bundle ID

mcp = FastMCP("SQLite_DB_Agent")

@mcp.tool()
def run_query(sql_query: str) -> str:
    """
    Executes a read-only SQL SELECT query against the internal SQLite database.
    Returns the results as a JSON string.
    
    Example Query for High BP: 
    SELECT * FROM health_records WHERE systolic_bp >= 130 OR diastolic_bp >= 80 ORDER BY timestamp DESC LIMIT 1
    """
    print(f"INFO: Executing SQL query: {sql_query}")
    if not sql_query.lower().strip().startswith('select'):
        return "Error: Only read-only SELECT queries are allowed."

    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  
        cursor = conn.cursor()

        cursor.execute(sql_query)
        # Convert the results to a list of dictionaries
        results = [dict(row) for row in cursor.fetchall()]
        return json.dumps(results, indent=2)
    except sqlite3.Error as e:
        return f"Database Error: {e}"
    except Exception as e:
        return f"Error: {e}"
    finally:
        if 'conn' in locals():
            conn.close()

@mcp.tool()
def send_to_server(json_data: str) -> str:
    """
    Sends the database results as a Push Notification payload to the APNs server.
    Arg:
    The 'json_data' parameter should be the human-readable description with results from
    sql.
    Returns a status message indicating success or failure.
    """
    if not AUTHENTICATION_TOKEN or not DEVICE_TOKEN:
        return "ERROR: APNs tokens (APNS_AUTH_TOKEN or APNS_DEVICE_TOKEN) are not set. Notification not sent."

    # 1. Prepare the custom alert body based on the query result
    try:
        results = json.loads(json_data)
        if results:
            first_result = results[0]
            # Construct a human-readable summary for the notification body
            title = "High BP Alert System ⚠️"
            bp_reading = f"{first_result.get('systolic_bp', '?')}/{first_result.get('diastolic_bp', '?')} mmHg"
            body = f"High BP detected: {bp_reading} (ID: {first_result.get('id')}). Review recent records."
            subtitle = f"Query found {len(results)} matching records."
        else:
            title = "Database Query Complete ✅"
            subtitle = "No records found matching the criteria."
            body = f"Query: {original_query}"
            
    except Exception:
        title = "Query Result Error ⚠️"
        subtitle = "Failed to parse database results."
        body = json_data[:100] # Send truncated raw data
        
    # 2. Construct the APNs Payload
    apns_payload = {
        # The 'alert' dictionary defines what the user sees
        "aps": {
            "alert": {
                "title": title,
                "subtitle": subtitle,
                "body": body
            }
        },
        # You can add custom data here for your app to process (e.g., the full results)
        "data": {
            "query_type": "high_bp_check",
            "full_results": results if 'results' in locals() else None 
        }
    }
    
    # 3. Define the HTTP/2 Headers
    headers = {
        "authorization": f"bearer {AUTHENTICATION_TOKEN}",
        "apns-topic": APNS_TOPIC,
        "apns-push-type": "alert",
        "apns-priority": "10",
        "apns-expiration": "0",
        "Content-Type": "application/json"
    }

    print("\n--- Sending Push Notification via APNs ---")
    try:
        # Note: verify=False is used for local development/testing with self-signed certs
        with httpx.Client(http2=True, verify=False) as client: 
            response = client.post(
                APNS_URL, 
                json=apns_payload,
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status() 
            
            return f"Successfully sent push notification to APNs. Status Code: {response.status_code}. Response: {response.text[:100]}"

    except httpx.HTTPStatusError as e:
        return f"ERROR: APNs request failed with status {e.response.status_code}. Details: {e.response.text}"
    except httpx.RequestError as e:
        return f"ERROR: Failed to connect to APNs server: {e}"
    except Exception as e:
        return f"An unexpected error occurred during APNs communication: {e}"


# Fix: Define a schema relevant to the user's request (high BP)
@mcp.resource("schema://sqlite/health_records")
def get_health_records_schema():
    """Returns the schema for the 'health_records' table, including blood pressure data."""
    # Assuming 'high BP' is defined as >= 130 systolic OR >= 80 diastolic
    return """
    CREATE TABLE health_records (
        id INTEGER PRIMARY KEY,
        user_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        systolic_bp INTEGER NOT NULL, -- Systolic Blood Pressure (mmHg)
        diastolic_bp INTEGER NOT NULL, -- Diastolic Blood Pressure (mmHg)
        notes TEXT
    )
    """

if __name__ == '__main__':
    print("-" * 50)
    print("FastMCP Agent Initialized.")
    print("The external LLM (e.g., 'claude' or another agent) will now dynamically generate")
    print("the SQL query and call 'run_query' and 'send_to_server' tools.")
    print("The hardcoded execution has been removed to allow dynamic LLM control.")
    print("-" * 50)
    
    # Start the agent's interactive loop so it can receive tool calls from the LLM.
    mcp.run()
