import pyodbc
import requests
from secrets import *

# Database connection details


# REST API endpoint and authentication
API_URL = 'http://localhost:8000/staff/'
API_AUTH_TOKEN = 'your_auth_token'  # Use Django Rest Framework's token authentication or similar


def fetch_staff_from_db():
    """Fetch staff records from the SQL Server database."""
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD}'
    query = """
        SELECT [pk],
               [Warehouse PK] AS person_bk,
               [SIMS pk],
               [Title],
               [First name],
               [Last name],
               [Staff code],
               [Full name],
               [Email address],
               [Row effective date],
               [Row expiry date],
               [FAM email address]
        FROM [dbo].[dim Staff]
        WHERE [Row expiry date] IS NULL
        AND [Email address] IS NOT NULL
    """
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return []


def sync_staff_with_api(staff_data):
    """Sync the staff data with the Django REST API."""
    headers = {'Authorization': f'Token {API_AUTH_TOKEN}', 'Content-Type': 'application/json'}

    for staff in staff_data:
        payload = {
            'warehouse_bk': staff['person_bk'],  # Map 'Warehouse PK' to Django field 'warehouse_bk'
            'first_name': staff['First name'],
            'last_name': staff['Last name'],
            'email': staff['Email address'],
        }

        # Check if the staff exists using 'warehouse_bk'
        response = requests.get(f"{API_URL}?warehouse_bk={staff['person_bk']}", headers=headers)

        if response.status_code == 200 and response.json():
            # Staff exists, update their record
            staff_id = response.json()[0]['id']  # Get the existing staff record's ID
            update_response = requests.put(f"{API_URL}{staff_id}/", json=payload, headers=headers)
            if update_response.status_code == 200:
                print(f"Updated staff: {payload['first_name']} {payload['last_name']}")
            else:
                print(f"Failed to update staff: {update_response.status_code} - {update_response.text}")
        elif response.status_code == 200:
            # Staff does not exist, create a new record
            create_response = requests.post(API_URL, json=payload, headers=headers)
            if create_response.status_code == 201:
                print(f"Created staff: {payload['first_name']} {payload['last_name']}")
            else:
                print(f"Failed to create staff: {create_response.status_code} - {create_response.text}")
        else:
            print(f"Failed to fetch staff: {response.status_code} - {response.text}")


if __name__ == "__main__":
    staff_data = fetch_staff_from_db()
    if staff_data:
        sync_staff_with_api(staff_data)
    else:
        print("No staff data fetched from the database.")

