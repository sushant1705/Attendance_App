import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("D:/VS CODES/Pyhton CV/Attendance_App/Resources/serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': 'https://faceattenddb-default-rtdb.firebaseio.com/'
})

ref = db.reference('Students')

data = {
    'Dhoni': 
    {
        "name" : "Mahendra Singh Dhoni",
        "dept": "CSE",
        "starting_year":2010,
        "totalAttendace": 1,
        "standing": 1,
        "year" : 4,
        "last_attendance_time": "2024-03-12 00:45:12"
    },
    'Modi': 
    {
        "name" : "Modi ji",
        "dept": "admin",
        "starting_year":2010,
        "totalAttendace": 1,
        "standing": 1,
        "year" : 4,
        "last_attendance_time": "2024-03-12 00:45:12"
    }
    
}


for key,value in data.items():
    ref.child(key).set(value)