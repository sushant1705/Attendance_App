import face_recognition
import os
import cv2
import boto3

s3 = boto3.client('s3', region_name='ap-south-1')
bucket_name = 'faceattendbucket'

known_faces_dir = "D:/VS CODES/Pyhton CV/Attendance_App/known"

known_face_encodings = []
known_face_names = []

for person_name in os.listdir(known_faces_dir):
    person_folder = os.path.join(known_faces_dir, person_name)
    if os.path.isdir(person_folder):
        for filename in os.listdir(person_folder):
            if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
                image_path = os.path.join(person_folder, filename)
                face_image = face_recognition.load_image_file(image_path)
                face_encoding = face_recognition.face_encodings(face_image)[0]
                known_face_encodings.append(face_encoding)
                known_face_names.append(person_name)
                s3.upload_file(image_path, bucket_name, f'Known-Images/{person_name}/{filename}')

face_locations = []
face_encodings = []
face_names = []

video_capture = cv2.VideoCapture(0)
video_capture_bgr = cv2.imread('D:/VS CODES/Pyhton CV/Attendance_App/Resources/background.png')

imgModelist= []
modes_dir="D:/VS CODES/Pyhton CV/Attendance_App/Resources/modes"
for image in os.listdir(modes_dir):
    imgModelist.append(cv2.imread(os.path.join(modes_dir,image)))


while True:
    ret, frame = video_capture.read()
    
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        face_names.append(name)

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Calculate scaling factor
    x_scaling_factor = 535 / frame.shape[1]
    y_scaling_factor = 400 / frame.shape[0]

    scaling_factor = min(x_scaling_factor, y_scaling_factor)

    frame_resized = cv2.resize(frame, None, fx=scaling_factor, fy=scaling_factor)

    # Calculate the upper-left coordinates to fit the scaled frame
    x_offset = int((540 - frame_resized.shape[1]) / 2)
    y_offset = int((410 - frame_resized.shape[0]) / 2)

    # Overlay the scaled frame on the background image
    video_capture_bgr[210+y_offset: 210+y_offset+frame_resized.shape[0], 89+x_offset: 89+x_offset+frame_resized.shape[1], :] = frame_resized
    video_capture_bgr[0: imgModelist[2].shape[0], 748: 748 + imgModelist[2].shape[1], :] = imgModelist[2]
    # cv2.imshow('Face Recognition', frame)
    cv2.imshow('Face Recognition', video_capture_bgr)

    if cv2.waitKey(1) ==13 :
        break

video_capture.release()
cv2.destroyAllWindows()
