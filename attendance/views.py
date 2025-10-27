from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import UserFace
import face_recognition
import numpy as np
import os, datetime

def load_known_faces():
    known_encodings = []
    known_infos = []

    for user in UserFace.objects.all():
        path = user.face_image.path
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_infos.append({
                'student_id': user.student_id,
                'full_name': user.full_name,
                'image_filename': os.path.basename(path)
            })
    return known_encodings, known_infos

@csrf_exempt
def recognize_faces(request):
    if request.method != 'POST' or 'image' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

    file = request.FILES['image']
    image = face_recognition.load_image_file(file)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return JsonResponse({'success': False, 'message': 'Không nhận được khuôn mặt nào'})

    face_encoding = encodings[0]

    known_face_encodings, known_face_infos = load_known_faces()

    TOLERANCE = 0.4
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=TOLERANCE)
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

    if True in matches:
        best_match_index = np.argmin(face_distances)
        info = known_face_infos[best_match_index]
        current_time = datetime.datetime.now().strftime('%H:%M:%S')

        return JsonResponse({
            'success': True,
            'student_id': info['student_id'],
            'full_name': info['full_name'],
            'image': info['image_filename'],
            'time': current_time,
            'message': 'Điểm danh thành công!'
        })

    return JsonResponse({'success': False, 'message': 'Không khớp với ai trong danh sách'})
