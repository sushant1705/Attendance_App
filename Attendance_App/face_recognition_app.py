import face_recognition
import os
import cv2

# Directory containing known faces
known_faces_dir = "D:/VS CODES/Pyhton CV/Face Detection/known"

# Load known faces
known_faces = []
known_names = []
# train model
for person_name in os.listdir(known_faces_dir):
    person_folder = os.path.join(known_faces_dir, person_name)
    if os.path.isdir(person_folder):
        for filename in os.listdir(person_folder):
            if filename.endswith(".jpeg"):
                image_path = os.path.join(person_folder, filename)
                image = face_recognition.load_image_file(image_path)
                face_encoding = face_recognition.face_encodings(image)[0]
                known_faces.append(face_encoding)
                known_names.append(person_name)

# Load an unknown image to recognize faces
unknown_image = face_recognition.load_image_file("D:/VS CODES/Pyhton CV/Face Detection/unknowm/images (2).jpeg")

# Find all face locations and face encodings in the unknown image
face_locations = face_recognition.face_locations(unknown_image)
face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

# Loop through each face found in the unknown image
for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    # Compare the face to known faces
    matches = face_recognition.compare_faces(known_faces, face_encoding)

    name = "Unknown"  # Default name if no match found

    if True in matches:
        match_index = matches.index(True)
        name = known_names[match_index]

    # Draw a rectangle around the face and label it
    import cv2
    cv2.rectangle(unknown_image, (left, top), (right, bottom), (0, 0, 255), 2)
    cv2.putText(unknown_image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

# Display the result
cv2.imshow("Face Recognition", unknown_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
