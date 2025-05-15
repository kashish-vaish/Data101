import pandas as pd
import requests
import config
import time
import io
import zipfile
from datetime import datetime, timedelta


def get_attendance_window(date_filter):
    windows = {
        2: ("12:10", "13:30"),  
        3: ("12:25", "22:00"),  
        4: ("14:00", "15:20"),  
    }
    weekday = pd.to_datetime(date_filter).weekday()
    if weekday not in windows:
        return None, None
    start_str, end_str = windows[weekday]
    start_time = pd.to_datetime(f"{date_filter} {start_str}")
    end_time = pd.to_datetime(f"{date_filter} {end_str}")
    return start_time, end_time


def fetch_qualtrics_attendance(date_filter):
    API_TOKEN = config.qualtricskey
    BASE_URL = config.qualtricsurl
    headers = {
        "x-api-token": API_TOKEN,
        "Content-Type": "application/json"
    }

    response = requests.get(f"{BASE_URL}/surveys", headers=headers)
    data = response.json()
    survey_id = ""
    for survey in data["result"]["elements"]:
        if survey["name"] == "S25-Data101-Attendance":
            survey_id = survey["id"]

    start = f"{date_filter}T00:00:00-06:00"
    end = f"{date_filter}T23:59:59-06:00"


    export_payload = {
        "format": "csv",
        "startDate": start,
        "endDate": end
    }

    start_resp = requests.post(
        f"{BASE_URL}/surveys/{survey_id}/export-responses",
        json=export_payload,
        headers=headers
    )
    print(start_resp.json())

    progress_id = start_resp.json()["result"]["progressId"]
    

    while True:
        check_resp = requests.get(
            f"{BASE_URL}/surveys/{survey_id}/export-responses/{progress_id}",
            headers=headers
        )
        status = check_resp.json()["result"]["status"]
        if status == "complete":
            file_id = check_resp.json()["result"]["fileId"]
            break
        elif status == "failed":
            raise Exception("Export failed")
        time.sleep(1)

    file_resp = requests.get(
        f"{BASE_URL}/surveys/{survey_id}/export-responses/{file_id}/file",
        headers=headers
    )

    # with open(f"qualtrics_raw_{date_filter}.zip", "wb") as f:
    #     f.write(file_resp.content)
    #     print(f"Raw Qualtrics ZIP saved as qualtrics_raw_{date_filter}.zip")


    with zipfile.ZipFile(io.BytesIO(file_resp.content)) as z:
        with z.open(z.namelist()[0]) as f:
            df = pd.read_csv(f, encoding="ISO-8859-1")

    df = df.drop(index=[0, 1]).reset_index(drop=True)
    return df


def get_attendance_status(date_filter):
    df = fetch_qualtrics_attendance(date_filter)

    data = df[["uid", "StartDate", "EndDate", "Longt", "Lati"]].copy()
    print(data.loc[((data["uid"] == "bd477")), ["uid", "StartDate", "EndDate"]])
    data["StartDate"] = pd.to_datetime(data["StartDate"], errors="coerce") - timedelta(hours=4)
    data["EndDate"] = pd.to_datetime(data["EndDate"], errors="coerce") - timedelta(hours=4)
    data["Longt"] = pd.to_numeric(data["Longt"], errors="coerce")
    data["Lati"] = pd.to_numeric(data["Lati"], errors="coerce")

    start_time, end_time = get_attendance_window(date_filter)
    print(start_time)
    print(end_time)
    if start_time and end_time:
        print(data.loc[~((data["StartDate"] >= start_time) & (data["EndDate"] <= end_time)), ["uid", "StartDate", "EndDate"]])

        data = data[
            (data["StartDate"] >= start_time) &
            (data["EndDate"] <= end_time)
        ]
        

    data = data.dropna(subset=["Longt", "Lati"])


    gid = "0"
    studentlist_path = f"https://docs.google.com/spreadsheets/d/{config.sheetid}/export?format=csv&gid={gid}"

    
    # studentlist_path = "C:\\Workspace\\Rutgers\\Sem3\\CS142_Data101_Sem3\\Spring 2025\\Logistics\\Attendance\\studentlist.csv"
    studentlist = pd.read_csv(studentlist_path)

    studentlist["Attendance"] = studentlist["NetId"].isin(data["uid"]).map({True: "Present", False: "Absent"})
    studentlist["UID"] = studentlist['UID'].fillna(0).astype(int).astype(str)
    return studentlist


if __name__ == "__main__":
    date = "2025-05-01"
    updated_list = get_attendance_status(date)
    print(updated_list.head())
