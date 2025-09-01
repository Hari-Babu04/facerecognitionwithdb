import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests
from firebase_admin import credentials, db
from datetime import datetime
from dotenv import load_dotenv

# Firebase setup
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-28101-default-rtdb.firebaseio.com/"
})

# Cloudinary setup
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

# Import mode images
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# Load face encodings
print("Loading Encode File ...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)

encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = None

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]

                if counter == 0:
                    modeType = 1  # Show Student Details
                    counter = 1  # Start processing attendance

        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                cloudinary_url = studentInfo.get("image_url", "")
                imgStudent = None

                if cloudinary_url:
                    try:
                        response = requests.get(cloudinary_url, stream=True)
                        if response.status_code == 200:
                            img_array = np.asarray(bytearray(response.raw.read()), dtype=np.uint8)
                            imgStudent = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        else:
                            print(f"Error: Unable to fetch image from {cloudinary_url}, Status Code: {response.status_code}")
                    except Exception as e:
                        print(f"Error fetching image: {str(e)}")

                last_attendance = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - last_attendance).total_seconds()

                cv2.imshow("Face Attendance", imgBackground)
                cv2.waitKey(1500)  # Hold modeType = 1 for 1.5 sec

                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    modeType = 2  # Attendance Marked
                    counter = 30  # Keep modeType = 2 for a while
                else:
                    modeType = 4  # Already Marked
                    counter = 0

            if modeType == 2:  # Ensure mode 2 is displayed fully
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo['Major']), (1006, 550),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(id), (1006, 493),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                if imgStudent is not None:
                    imgStudent = cv2.resize(imgStudent, (216, 216))
                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent
                else:
                    print("Error: Student image not found or not loaded correctly.")

                cv2.imshow("Face Attendance", imgBackground)
                cv2.waitKey(2000)  # Display mode 2 for 2 sec

                modeType = 0  # Reset to default state
                counter = 0

            if modeType == 4:
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(750)
