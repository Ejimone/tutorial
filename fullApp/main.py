import os.path
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Added
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import uvicorn

app = FastAPI()

# Added CORS middleware
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "null",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly', 
          'https://www.googleapis.com/auth/classroom.courses',
           'https://www.googleapis.com/auth/classroom.coursework.students',
           'https://www.googleapis.com/auth/classroom.coursework.me',
           'https://www.googleapis.com/auth/classroom.rosters',
           'https://www.googleapis.com/auth/classroom.profile.emails',
           'https://www.googleapis.com/auth/classroom.profile.photos',
           "https://www.googleapis.com/auth/classroom.announcements",
           "https://www.googleapis.com/auth/classroom.addons.student",
           "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly"
        ]






@app.get("/home")
def get_courses_handler(): # Renamed from 'main' for clarity
    """
    Shows a basic usage of the Google Classroom API
    Print the names of first 10 courses
    Fetches the list of available courses from Google Classroom.
    """
    print("DEBUG: /home endpoint accessed") # Added for debugging
    creds = None
    # the token.json file stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("DEBUG: Refreshing token")
                creds.refresh(Request())
            except Exception as e:
                print(f"DEBUG: Error refreshing token: {e}. Re-authenticating.")
                # Fall through to re-authenticate if refresh fails
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES)
                creds = flow.run_local_server(port=0) # port=0 finds a free port
        else:
            print("DEBUG: No valid credentials, starting OAuth flow.")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
            print("DEBUG: Credentials saved to token.json")
    try:
        service = build("classroom", "v1", credentials=creds)
        # Call the Classroom API
        print("DEBUG: Calling Classroom API to list courses")
        results = service.courses().list(pageSize=10).execute()
        courses = results.get("courses", [])

        if not courses:
            print("DEBUG: No courses found from API.")
            return {"message": "No courses found.", "courses": []}
        else:
            print(f"DEBUG: Found {len(courses)} courses.")
            return {"message": "Courses fetched successfully", "courses": courses}
    except HttpError as error:
        error_details = f"An API error occurred: {error.resp.status} - {error._get_reason()}"
        print(f"DEBUG: HttpError: {error_details}")
        raise HTTPException(status_code=error.resp.status, detail=error_details)
    except Exception as e:
        print(f"DEBUG: An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")



@app.get("/assignments")
def get_assignments():
    creds = None
    # The token.json file stores the user's access and refresh tokens.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("DEBUG: Refreshing token for /assignments")
                creds.refresh(Request())
            except Exception as e:
                print(f"DEBUG: Error refreshing token for /assignments: {e}. Re-authenticating.")
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            print("DEBUG: No valid credentials for /assignments, starting OAuth flow.")
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
            print("DEBUG: Credentials saved to token.json from /assignments")

    try:
        service = build("classroom", "v1", credentials=creds)
        
        # 1. Fetch courses
        print("DEBUG: Calling Classroom API to list courses for assignments")
        courses_results = service.courses().list().execute()
        courses = courses_results.get("courses", [])

        if not courses:
            print("DEBUG: No courses found to fetch assignments from.")
            return {"message": "No courses found to fetch assignments from.", "assignments_by_course": []}

        assignments_by_course = []
        # 2. For each course, fetch assignments (courseWork)
        for course in courses:
            course_id = course.get('id')
            course_name = course.get('name', 'Unnamed Course') # Default name if not present
            print(f"DEBUG: Fetching assignments for course: {course_name} (ID: {course_id})")
            
            try:
                course_work_results = service.courses().courseWork().list(courseId=course_id).execute()
                course_work_items = course_work_results.get("courseWork", [])
                
                course_data = {
                    "courseId": course_id,
                    "courseName": course_name,
                    "assignments": course_work_items
                }
                if not course_work_items:
                    course_data["message"] = f"No assignments found for course {course_name}"
                assignments_by_course.append(course_data)

            except HttpError as he:
                # Log error for specific course and continue if possible, or decide to fail all
                print(f"DEBUG: HttpError fetching assignments for course {course_id}: {he}")
                assignments_by_course.append({
                    "courseId": course_id,
                    "courseName": course_name,
                    "assignments": [],
                    "error": f"Failed to fetch assignments: {he._get_reason()}"
                })
            except Exception as e:
                print(f"DEBUG: Unexpected error fetching assignments for course {course_id}: {e}")
                assignments_by_course.append({
                    "courseId": course_id,
                    "courseName": course_name,
                    "assignments": [],
                    "error": f"An unexpected error occurred: {str(e)}"
                })


        if not assignments_by_course and courses: # Should not happen if courses list was not empty
             print("DEBUG: Courses were found, but no assignment data could be compiled.")
             return {"message": "Found courses, but no assignment data could be compiled.", "assignments_by_course": []}
        
        print(f"DEBUG: Successfully fetched assignments for {len(assignments_by_course)} courses.")
        return {"message": "Assignments fetched successfully", "assignments_by_course": assignments_by_course}

    except HttpError as error:
        error_details = f"An API error occurred: {error.resp.status} - {error._get_reason()}"
        print(f"DEBUG: HttpError in get_assignments: {error_details}")
        raise HTTPException(status_code=error.resp.status, detail=error_details)
    except Exception as e:
        # This catches errors like issues with credentials.json file not found during flow init
        print(f"DEBUG: An unexpected error occurred in get_assignments: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")


if __name__ == "__main__":
    print("DEBUG: Starting Uvicorn server on http://0.0.0.0:8000 with reload enabled.")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)