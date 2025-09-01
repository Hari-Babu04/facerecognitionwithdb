import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{'databaseURL':'https://faceattendancerealtime-28101-default-rtdb.firebaseio.com/'})

ref = db.reference('Students')

data={
    "123453":{
        "name":"Hari",
        "Major":"ECE",
        "starting_year":2022,
        "total_attendance":7,
        "standing":"G",
        "year":4,
        "last_attendance_time":"2025-02-10 00:54:34"

    },"123454":{
        "name":"MAN 1",
        "Major":"Civics",
        "starting_year":2023,
        "total_attendance":6,
        "standing":"G",
        "year":3,
        "last_attendance_time":"2025-02-10 05:54:34"

    },"123455":{
        "name":"Man 2",
        "Major":"Fashion Technology",
        "starting_year":2024,
        "total_attendance":7,
        "standing":"B",
        "year":2,
        "last_attendance_time":"2025-01-10 00:54:34"

    },"123456":{
        "name":"Teacher",
        "Major":"Compter Vision / robotics",
        "starting_year":2022,
        "total_attendance":7,
        "standing":"G",
        "year":4,
        "last_attendance_time":"2025-02-10 00:54:34"

    },"123457":{
        "name":"emily blunt",
        "Major":"acting",
        "starting_year":2025,
        "total_attendance":7,
        "standing":"B",
        "year":1,
        "last_attendance_time":"2025-01-10 00:54:34"

    },"123458":{
        "name":"Musk",
        "Major":"physics",
        "starting_year":2022,
        "total_attendance":7,
        "standing":"G",
        "year":4,
        "last_attendance_time":"2025-02-10 00:44:34"

    }

}

for key,value in data.items():
    ref.child(key).set(value)
