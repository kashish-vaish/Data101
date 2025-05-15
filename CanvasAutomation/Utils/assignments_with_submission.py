import requests

# Canvas API URL, API token, and course/assignment IDs
canvas_url = "https://rutgers.instructure.com/api/v1"
api_token = "<your key>"
course_id = "287710"  
assignment_id = "3153127"  

# headers for authentication
headers = {
    "Authorization": f"Bearer {api_token}"
}

# Function to fetch all submissions with pagination
def fetch_all_submissions(course_id, assignment_id):
    submissions = []
    page_url = f"{canvas_url}/courses/{course_id}/assignments/{assignment_id}/submissions?status=all&per_page=100"  # Starting URL
    
    while page_url:
        # Send the request to the Canvas API
        response = requests.get(page_url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            page_data = response.json()
            submissions.extend(page_data)  # Add the submissions from this page
            
            # Debugging: Print the headers to check if there's a next page
            # print("Response Headers:", response.headers)
            
            # Extract the next page URL from the 'link' header
            links = response.headers.get('link', '')
            next_page_url = None
            for link in links.split(','):
                if 'rel="next"' in link:
                    next_page_url = link[link.find('<')+1:link.find('>')]  # Extract the URL from the < > brackets
                    break

            # Set the next page URL for the next iteration or break if no next page
            page_url = next_page_url
        
        else:
            print(f"Error fetching submissions: {response.status_code}")
            break  # Stop if there was an error

    return submissions

# Fetch all submissions
submissions = fetch_all_submissions(course_id, assignment_id)

# Output the results
print(f"Total submissions fetched: {len(submissions)}")
for submission in submissions:
    user_id = submission["user_id"]
    attachments = submission.get("attachments", [])
    if attachments:
        print(f"Student {user_id} has {len(attachments)} attachment(s).")
    else:
        print(f"Student {user_id} has no attachments.")
