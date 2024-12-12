import pyodbc
import requests
from secrets import *

# Database connection details


# REST API endpoint and authentication
API_URL = 'http://localhost:8000/tutor-groups/'
API_AUTH_TOKEN = 'your_auth_token'  # Use Django Rest Framework's token authentication or similar

def fetch_tutor_groups_from_db():
    """Fetch tutor group records from the SQL Server database."""
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD}'
    query = """
    SELECT [Tutor group] AS name,
           [Year Group] AS year_group,
           [Tutor bk] AS tutor_bk,
           [Head of Year bk] AS head_of_year_bk,
           [AHT bk] AS aht_bk
    FROM [dbo].[dim Pastroal Structure]
    WHERE [Row expiry date] IS NULL
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

def fetch_staff_id(warehouse_bk):
    """Fetch the Django staff ID based on the warehouse_bk."""
    headers = {'Authorization': f'Token {API_AUTH_TOKEN}', 'Content-Type': 'application/json'}
    response = requests.get(f"http://localhost:8000/staff/?search={warehouse_bk}", headers=headers)
    if response.status_code == 200:
        staff_list = response.json()
        for staff in staff_list:
            if staff.get('warehouse_bk') == warehouse_bk:
                return staff.get('id')  # Return the ID of the matching staff
    print(f"Warning: No matching staff found for warehouse_bk={warehouse_bk}")
    return None

def sync_tutor_groups_with_api(tutor_groups):
    """Sync tutor group data with the Django REST API."""
    headers = {'Authorization': f'Token {API_AUTH_TOKEN}', 'Content-Type': 'application/json'}

    for group in tutor_groups:
        # Fetch staff IDs using the bk fields
        tutor_id = fetch_staff_id(group['tutor_bk'])
        head_of_year_id = fetch_staff_id(group['head_of_year_bk'])
        assistant_head_id = fetch_staff_id(group['aht_bk'])

        # Skip if any staff member is not found
        if not (tutor_id and head_of_year_id and assistant_head_id):
            print(f"Skipping group {group['name']} due to missing staff.")
            continue

        # Map tutor group fields
        payload = {
            'name': group['name'],
            'tutor': tutor_id,  # Pass ID only
            'head_of_year': head_of_year_id,  # Pass ID only
            'assistant_head': assistant_head_id,  # Pass ID only
        }

        # Check if the tutor group exists using the name
        response = requests.get(f"{API_URL}?search={group['name']}", headers=headers)

        if response.status_code == 200 and response.json():
            # Tutor group exists, update its record
            group_id = response.json()[0]['id']  # Get the existing group's ID
            update_response = requests.put(f"{API_URL}{group_id}/", json=payload, headers=headers)
            if update_response.status_code == 200:
                print(f"Updated tutor group: {payload['name']}")
            else:
                print(f"Failed to update tutor group: {update_response.status_code} - {update_response.text}")
        elif response.status_code == 200:
            # Tutor group does not exist, create a new record
            create_response = requests.post(API_URL, json=payload, headers=headers)
            if create_response.status_code == 201:
                print(f"Created tutor group: {payload['name']}")
            else:
                print(f"Failed to create tutor group: {create_response.status_code} - {create_response.text}")
        else:
            print(f"Failed to fetch tutor group: {response.status_code} - {response.text}")

if __name__ == "__main__":
    tutor_groups = fetch_tutor_groups_from_db()
    if tutor_groups:
        sync_tutor_groups_with_api(tutor_groups)
    else:
        print("No tutor group data fetched from the database.")