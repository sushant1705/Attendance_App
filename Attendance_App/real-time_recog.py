import face_recognition
import os
import cv2
import boto3
import numpy as np
import json

s3 = boto3.client('s3', region_name='ap-south-1')
bucket_name = 'faceattendbucket'
known_faces_dir = "D:/VS CODES/Pyhton CV/Attendance_App/known"

known_face_encodings = []
known_face_names = []

for person_name in os.listdir(known_faces_dir):
    person_folder = os.path.join(known_faces_dir, person_name)
    if os.path.isdir(person_folder):
        for filename in os.listdir(person_folder):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):  # Check for lowercase extensions
                image_path = os.path.join(person_folder, filename)
                face_image = face_recognition.load_image_file(image_path)
                face_encoding = face_recognition.face_encodings(face_image)[0]
                known_face_encodings.append(face_encoding)
                known_face_names.append(person_name)
                s3.upload_file(image_path, bucket_name, f'Known-Images/{person_name}/{filename}')

face_locations = []
face_encodings = []
face_names = []
modetype = 0
counter = 0
imgStudent = []
recognized_name = ""

file_name = 'persons_data.json'
response = s3.get_object(Bucket=bucket_name, Key=file_name)
persons_data = response['Body'].read().decode('utf-8')
persons_dict = json.loads(persons_data)



video_capture = cv2.VideoCapture(0)
video_capture_bgr = cv2.imread('D:/VS CODES/Pyhton CV/Attendance_App/Resources/background.png')

imgModelist = []
modes_dir = "D:/VS CODES/Pyhton CV/Attendance_App/Resources/modes"
for image in os.listdir(modes_dir):
    imgModelist.append(cv2.imread(os.path.join(modes_dir, image)))

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
        recognized_name = name

    x_scaling_factor = 535 / frame.shape[1]
    y_scaling_factor = 400 / frame.shape[0]

    scaling_factor = min(x_scaling_factor, y_scaling_factor)

    frame_resized = cv2.resize(frame, None, fx=scaling_factor, fy=scaling_factor)

    x_offset = int((540 - frame_resized.shape[1]) / 2)
    y_offset = int((410 - frame_resized.shape[0]) / 2)

    video_capture_bgr[210+y_offset: 210+y_offset+frame_resized.shape[0], 89+x_offset: 89+x_offset+frame_resized.shape[1], :] = frame_resized
    video_capture_bgr[0: imgModelist[modetype].shape[0], 748: 748 + imgModelist[modetype].shape[1], :] = imgModelist[modetype]

    if counter == 0:
        counter = 1
        modetype = 0

    if recognized_name and recognized_name != "Unknown":
        image_key_base = f"Known-Images/{recognized_name}/{recognized_name}"
        extensions = ['.jpg', '.jpeg', '.png']

        for ext in extensions:
            if s3.get_object(Bucket=bucket_name, Key=f"{image_key_base}{ext}"):
                image_key = f"{image_key_base}{ext}"
                break
        else:
            image_key = f"{image_key_base}.jpg"

        # print("Image Key:", image_key)

        if counter != 0:
            if counter == 1:
                modetype = 1
                response = s3.get_object(Bucket=bucket_name, Key=image_key)
                image_data = response['Body'].read()
                img_np = np.frombuffer(image_data, np.uint8)
                imgStudent = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
                print("Image downloaded and displayed successfully.")
                print("Recognized Name:", recognized_name)
                recognized_person = None
                for person in persons_dict['persons']:
                    if person['name'] == recognized_name:
                        recognized_person = person
                        break
                
                for person in persons_dict['persons']:
                    person['total-attendance'] += 1
                    updated_json_str = json.dumps(persons_dict)
                    s3.put_object(Bucket=bucket_name, Key=file_name, Body=updated_json_str)
                    print('Attendance updated for all persons successfully.')

                # Check if the recognized person was found
                print(recognized_person)
                if recognized_person is not None:
                    print("Recognized Person Details:") 
                    print(f"Name: {recognized_person['name']}")
                    print(f"Email: {recognized_person['email']}")
                    print(f"Department: {recognized_person['department']}")
                else:
                    print(f"Details for '{recognized_name}' not found in the JSON data.")      
                    
                      
            if 10<counter <20:
                modetype = 2
            video_capture_bgr[0: imgModelist[modetype].shape[0], 748: 748 + imgModelist[modetype].shape[1], :] = imgModelist[modetype]    
                
            if counter <=10:
                department_text = recognized_person['department'] if recognized_person is not None else "Department Not Found"
                id_text = str(recognized_person['id'] if recognized_person is not None else "ID Not Found")
                attendance_text = str(recognized_person['total-attendance'] if recognized_person is not None else "NA")
                cv2.putText(video_capture_bgr, id_text, (747+190, 503), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0,0,0), 2)
                cv2.putText(video_capture_bgr, attendance_text, (747+108, 150), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,0,0), 2)
                cv2.putText(video_capture_bgr, department_text, (747+190, 582), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0,0,0), 2)
                imgModelist[modetype][210:210+209, 123:123+209] = imgStudent

                   
            counter+=1   
            
            if counter >=20:
                counter  =0
                modetype = 0
                # recognized_person = None   fix this
                imgStudent = []
                video_capture_bgr[0: imgModelist[modetype].shape[0], 748: 748 + imgModelist[modetype].shape[1], :] = imgModelist[modetype] 
 
    
    
    cv2.imshow('Face Recognition', video_capture_bgr)

    if cv2.waitKey(1) == 13:
        break

video_capture.release()
cv2.destroyAllWindows()
