import pyodbc
import requests
from secrets import *

# REST API endpoint and authentication
API_URL = 'http://localhost:8000/students/'
API_AUTH_TOKEN = 'your_auth_token'  # Use Django Rest Framework's token authentication

def fetch_students_from_db():
    """Fetch student records from the SQL Server database."""
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD}'
    query = """
    SELECT [First Name] AS first_name,
           [Last name] AS last_name,
           [Student Email] AS email,
           [Preferred first name] AS preferred_name,
           [Tutor Group] AS tutor_group,
           [FAM email] AS fam_email,
           [GIS ID Number] AS school_code,
           [Person BK] AS warehouse_bk
    FROM [dbo].[dim_students_isams]
    WHERE [Row Expiration Date] IS NULL
      AND [On Roll] = 'On Roll'
      AND [Year Group] >= 7
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

def fetch_student_id(warehouse_bk):
    """Fetch the Django student ID based on the warehouse_bk."""
    headers = {'Authorization': f'Token {API_AUTH_TOKEN}', 'Content-Type': 'application/json'}
    response = requests.get(f"{API_URL}?search={warehouse_bk}", headers=headers)
    if response.status_code == 200:
        student_list = response.json()
        for student in student_list:
            if student.get('warehouse_bk') == warehouse_bk:
                return student.get('id')  # Return the ID of the matching student
    print(f"Warning: No matching student found for warehouse_bk={warehouse_bk}")
    return None

def fetch_tutor_group_id(tutor_group_name):
    """Fetch the Django tutor group ID based on the tutor group name."""
    headers = {'Authorization': f'Token {API_AUTH_TOKEN}', 'Content-Type': 'application/json'}
    response = requests.get(f"http://localhost:8000/tutor-groups/?search={tutor_group_name}", headers=headers)
    if response.status_code == 200:
        tutor_group_list = response.json()
        for group in tutor_group_list:
            if group.get('name') == tutor_group_name:
                return group.get('id')  # Return the ID of the matching tutor group
    print(f"Warning: No matching tutor group found for name={tutor_group_name}")
    return None

def sync_students_with_api(students):
    """Sync student data with the Django REST API."""
    headers = {'Authorization': f'Token {API_AUTH_TOKEN}', 'Content-Type': 'application/json'}

    for student in students:
        # Fetch tutor group ID
        tutor_group_id = fetch_tutor_group_id(student['tutor_group'])

        if not tutor_group_id:
            print(f"Skipping student {student['first_name']} {student['last_name']} due to missing tutor group.")
            continue

        # Map student fields
        payload = {
            'first_name': student['first_name'],
            'last_name': student['last_name'],
            'email': student['email'],
            'preferred_name': student['preferred_name'],
            'tutor_group': tutor_group_id,  # Pass tutor group ID
            'fam_email': student['fam_email'],
            'school_code': student['school_code'],
            'warehouse_bk': student['warehouse_bk']
        }

        # Check if the student exists using the warehouse_bk
        student_id = fetch_student_id(student['warehouse_bk'])

        if student_id:
            # Student exists, update their record
            update_response = requests.put(f"{API_URL}{student_id}/", json=payload, headers=headers)
            if update_response.status_code == 200:
                print(f"Updated student: {payload['first_name']} {payload['last_name']}")
            else:
                print(f"Failed to update student: {update_response.status_code} - {update_response.text}")
        else:
            # Student does not exist, create a new record
            create_response = requests.post(API_URL, json=payload, headers=headers)
            if create_response.status_code == 201:
                print(f"Created student: {payload['first_name']} {payload['last_name']}")
            else:
                print(f"Failed to create student: {create_response.status_code} - {create_response.text}")

if __name__ == "__main__":
    students = fetch_students_from_db()
    if students:
        sync_students_with_api(students)
    else:
        print("No student data fetched from the database.")
