from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import UserFace

import face_recognition
import numpy as np
import os
import datetime

# Đường dẫn thư mục chứa ảnh gốc
KNOWN_FACES_DIR = os.path.join(settings.BASE_DIR, 'attendance', 'faces', 'known_faces')

# Tạo danh sách vector và liên kết với DB
known_face_encodings = []
known_face_infos = []

for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            encoding = encodings[0]

            # Lấy thông tin từ DB
            try:
                user = UserFace.objects.get(image_filename=filename)
                known_face_encodings.append(encoding)
                known_face_infos.append({
                    'student_id': user.student_id,
                    'full_name': user.full_name,
                    'image_filename': user.image_filename
                })
            except UserFace.DoesNotExist:
                pass

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

    # Giảm tolerance để nhận chính xác hơn
    TOLERANCE = 0.4
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=TOLERANCE)
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

    if True in matches:
        best_match_index = np.argmin(face_distances)
        best_distance = face_distances[best_match_index]

        # Kiểm tra chênh lệch giữa 2 người giống nhất
        sorted_distances = sorted(face_distances)
        diff = sorted_distances[1] - sorted_distances[0] if len(sorted_distances) > 1 else 1

        # Chỉ chấp nhận nếu thực sự chắc chắn
        if matches[best_match_index] and best_distance < TOLERANCE and diff > 0.1:
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
        else:
            return JsonResponse({'success': False, 'message': 'Khuôn mặt không khớp rõ ràng hoặc không đủ chính xác'})
    else:
        return JsonResponse({'success': False, 'message': 'Không khớp với ai trong danh sách'})
