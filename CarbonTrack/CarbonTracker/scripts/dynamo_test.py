from datetime import datetime

timestamp_str = "2025-03-14T22:50:44.037005"  # Example timestamp
try:
    timestamp_dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f").date()
    #timestamp_dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f").date()
    print(f"Parsed timestamp: {timestamp_dt}")
    #timestamp_dt = timestamp_dt.date()
    #print(f"Converted to date format: {timestamp_dt}")
except ValueError as e:
    print(f"Error parsing timestamp: {e}")