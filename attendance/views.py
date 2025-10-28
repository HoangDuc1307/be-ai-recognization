from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import UserFace
import face_recognition
import numpy as np
import os
import datetime
import cv2
from PIL import Image
from io import BytesIO
import base64

# Hàm tải dữ liệu khuôn mặt đã biết từ cơ sở dữ liệu
def load_known_faces():
    known_encodings = []
    known_infos = []

    # Lặp qua tất cả bản ghi trong model UserFace
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

# View xử lý yêu cầu nhận diện khuôn mặt
@csrf_exempt # Bỏ qua kiểm tra CSRF
def recognize_faces(request):
     # Kiểm tra phương thức POST và có file ảnh
    if request.method != 'POST' or 'image' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    file = request.FILES['image']
    image = face_recognition.load_image_file(file)
    encodings = face_recognition.face_encodings(image)
    face_locations = face_recognition.face_locations(image)
    
    # Lấy mã hóa khuôn mặt đầu tiên
    face_encoding = encodings[0]

    # Tải dữ liệu khuôn mặt đã biết
    known_face_encodings, known_face_infos = load_known_faces()
    # So sánh khuôn mặt với dữ liệu đã biết
    TOLERANCE = 0.4
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=TOLERANCE)
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

    # Chuyển ảnh sang BGR để vẽ bằng OpenCV
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Vẽ khung quanh khuôn mặt
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(image_bgr, (left, top), (right, bottom), (0, 255, 0), 2)

    # Chuyển ảnh có khung về base64 để gửi lại cho FE
    _, buffer = cv2.imencode('.jpg', image_bgr)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')

    # Nếu có khuôn mặt khớp
    if True in matches:
        best_match_index = np.argmin(face_distances)
        info = known_face_infos[best_match_index]
        current_time = datetime.datetime.now().strftime('%H:%M:%S')

        # Trả về thông tin người dùng và ảnh đã vẽ khung
        return JsonResponse({
            'success': True,
            'student_id': info['student_id'],
            'full_name': info['full_name'],
            'image': info['image_filename'],
            'time': current_time,
            'message': 'Điểm danh thành công!',
            'framed_image': f"data:image/jpeg;base64,{jpg_as_text}"
        })
    
    # Nếu không khớp với ai
    return JsonResponse({
        'success': False,
        'message': 'Không khớp với ai trong danh sách',
        'framed_image': f"data:image/jpeg;base64,{jpg_as_text}"
    })
