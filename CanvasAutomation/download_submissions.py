import os
import requests

CANVAS_URL = "https://rutgers.instructure.com/api/v1"
CANVAS_API = "6948~hvukEe7Wf83QQPhKPQYtzRfTRChN3trFCaPtGUc323MMFu2PCGWcLaG7BkCfFQY2"
COURSE_ID = "330127"  
ASSIGNMENT_ID = "3460468" 
DOWNLOAD_DIR = "C:\\Workspace\\Rutgers\\Sem3\\CS142_Data101_Sem3\\Spring 2025\\Assessments\\Prediction Challenge 1"
SECTIONS = {"198-142-05", "198-142-07"}

headers={
    "Authorization" : f"Bearer {CANVAS_API}"
}

def get_section_ids():
    url = f"{CANVAS_URL}/courses/{COURSE_ID}/sections"
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    sectionId = {}
    output = response.json()


    for row in output:
        for sections in SECTIONS:
            if sections in row['sis_section_id']:
                sectionId[sections[-1:]] = row['id']
    

    return sectionId

def get_student_name(userId):
    url = f"{CANVAS_URL}/courses/{COURSE_ID}/users/{userId}"
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    return(response.json()['name'])

def get_student_ids_for_section(section_id):
    students_url = f"{CANVAS_URL}/courses/{COURSE_ID}/sections/{section_id}?include[]=students&include[]=enrollments"
    print(students_url)
    response = requests.get(students_url, headers=headers)
    response.raise_for_status()  

    students = response.json()

    student_netids = [student['sis_user_id'] for student in students["students"]]
    student_userids = []
    student_net_userids = {}
    for student in students["students"]:
        for enrollment in student["enrollments"]:
            user_id = enrollment["user_id"]
            name = student["name"]
            student_net_userids[name] = user_id
            student_userids.append(user_id)
    
    return student_net_userids

def download_submission(sectionId, sectionName,studentlist):
    sectionDir = os.path.join(DOWNLOAD_DIR,f"Section {sectionName}")
    os.makedirs(sectionDir,exist_ok=True)
    for studentname, studentid in studentlist.items():
        submissions_url = f"{CANVAS_URL}/courses/{COURSE_ID}/assignments/{ASSIGNMENT_ID}/submissions/{studentid}"
        print(submissions_url)
        response = requests.get(submissions_url, headers=headers)
        if response.status_code == 200:
            submission = response.json()      
            studir = os.path.join(sectionDir,f"{studentname}")
            os.makedirs(studir,exist_ok=True)
            
            if "attachments" in submission:
                for attachment in submission["attachments"]:
                    file_url = attachment["url"]
                    file_name = attachment["filename"]
                    response = requests.get(file_url,headers=headers)
                    if response.status_code==200:
                        file_path = os.path.join(studir,file_name)
                        with open(file_path, "wb") as file:
                            file.write(response.content)
                        print(f"Downloaded {file_name} for student {studentname}")




sectionId = get_section_ids()

for sectionName, sectionId in sectionId.items():
    studentids = get_student_ids_for_section(section_id=sectionId)
    download_submission(sectionId=sectionId, sectionName=sectionName, studentlist=studentids)





