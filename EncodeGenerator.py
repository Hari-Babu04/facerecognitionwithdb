import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials, db
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-28101-default-rtdb.firebaseio.com/"
})

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

# Importing student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
print("Images Found:", pathList)

imgList = []
studentIds = []

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentId = os.path.splitext(path)[0]  # Extract student ID from filename
    studentIds.append(studentId)

    filePath = os.path.join(folderPath, path)
    
    # Upload image to Cloudinary
    response = cloudinary.uploader.upload(filePath, folder="face_recognition")
    print(f"Uploaded {studentId}: {response['secure_url']}")

    # Get existing student data to avoid overwriting
    student_ref = db.reference(f'Students/{studentId}')
    student_data = student_ref.get() or {}  # Fetch existing data

    # Update Firebase with new image URL while keeping other fields
    student_ref.update({
        **student_data,  # Preserve existing data
        "image_url": response["secure_url"]
    })

print("Uploaded images to Cloudinary and updated Firebase successfully!")

# Face Encoding
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            encodeList.append(encodings[0])
        else:
            print("Warning: No face found in an image.")
    return encodeList

print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

# Save encodings locally
with open("EncodeFile.p", 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)

print("Encodings Saved Successfully!")
