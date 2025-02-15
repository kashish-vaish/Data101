import pandas as pd
import csv

data = pd.read_csv("C:\\Workspace\\Rutgers\\Sem3\\CS142_Data101_Sem3\\Spring 2025\\Logistics\\Attendance\\Feb 14\\Feb14.csv")
studentlist = pd.read_csv("C:\\Workspace\\Rutgers\\Sem3\\CS142_Data101_Sem3\\Spring 2025\\Logistics\\Attendance\\studentlist.csv")


data = data.drop([0,1,2])
data = data[['uid','Longt','Lati']]
uids_na_coord = data[data['Longt'].isna()]
data = data.dropna(subset=['Longt'])
uids_na_coord = uids_na_coord[~uids_na_coord['uid'].isin(data['uid'])]

studentlist['Attendance'] = studentlist['uid'].isin(data['uid'])



studentlist.to_csv("C:\\Workspace\\Rutgers\\Sem3\\CS142_Data101_Sem3\\Spring 2025\\Logistics\\Attendance\\Feb 14\\student_attendance.csv",index=False)
uids_na_coord.to_csv("C:\\Workspace\\Rutgers\\Sem3\\CS142_Data101_Sem3\\Spring 2025\\Logistics\\Attendance\\Feb 14\\students_with_attendance_withoutcoordinates.csv",index=False)



