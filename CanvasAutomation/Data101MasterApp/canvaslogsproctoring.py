import os
import requests
import csv
from collections import defaultdict
from config import key
import pandas as pd
import config

CANVAS_URL = "https://rutgers.instructure.com/api/v1"
ACCESS_TOKEN = key
COURSE_ID = "330127"
QUIZ_ID = "911882"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def get_quiz_submissions(course_id, quiz_id):
    submissions = []
    url = f"{CANVAS_URL}/courses/{course_id}/quizzes/{quiz_id}/submissions"
    params = {'per_page': 100}
    
    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        submissions.extend(data['quiz_submissions'])
        url = response.links.get('next', {}).get('url')
    
    return submissions

def get_submission_events(course_id, quiz_id, submission_id):
    url = f"{CANVAS_URL}/courses/{course_id}/quizzes/{quiz_id}/submissions/{submission_id}/events"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data.get('quiz_submission_events', data)

def export_flagged_students_blur_events(course_id, quiz_id, output_file="flagged_students_blur_log_quiz7.csv"):
    submissions = get_quiz_submissions(course_id, quiz_id)

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["user_id", "submission_id", "timestamp", "message", "blur_count"])

        for sub in submissions:
            user_id = sub['user_id']
            submission_id = sub['id']
            blur_events = []

            try:
                events = get_submission_events(course_id, quiz_id, submission_id)
                for event in events:
                    if event.get('event_type') == 'page_blurred':
                        blur_events.append(event)
                
                if len(blur_events) > 0:
                    print(f"User {user_id} had {len(blur_events)} 'page_blurred' events.")
                    for e in blur_events:
                        timestamp = e.get('created_at', '')
                        message = 'Stopped viewing the Canvas quiz-taking page...'
                        writer.writerow([user_id, submission_id, timestamp, message, len(blur_events)])
            except Exception as e:
                print(f"Error processing user {user_id}: {e}")

    print(f"\nExported students with >2 blur events to {output_file}")

def get_user_name(sheet_id):
    gid = "0"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    df['UID'] = df['UID'].fillna(0).astype(int).astype(str)
    return dict(zip(df['UID'],df['FirstName']))


def get_blur_events(course_id, quiz_id):
    quiz_url = f"{CANVAS_URL}/courses/{course_id}/quizzes/{quiz_id}"

    try:
        response = requests.get(quiz_url, headers=headers)
        response.raise_for_status()
        assignment_id = response.json().get("assignment_id")
    except Exception as e:
        raise Exception(f"Failed to fetch assignment_id for quiz {quiz_id}: {e}")
    
    submissions = get_quiz_submissions(course_id, quiz_id)
    result = []
    useridnames = get_user_name(config.sheetid)
    print(useridnames)

    for sub in submissions:
        user_id = sub['user_id']
        submission_id = sub['id']
        blur_events = []

        try:
            events = get_submission_events(course_id, quiz_id, submission_id)
            for event in events:
                if event.get('event_type') == 'page_blurred':
                    blur_events.append(event)

            if blur_events:
                result.append({
                    'user_id': user_id,
                    'name': useridnames.get(str(user_id), "Unknown"),
                    'submission_id': submission_id,
                    'speedgrader_url': f"https://rutgers.instructure.com/courses/{course_id}/gradebook/speed_grader?assignment_id={assignment_id}&student_id={user_id}"
                    })
        except Exception as e:
            print(f"Error processing user {user_id}: {e}")
            continue

    return result


