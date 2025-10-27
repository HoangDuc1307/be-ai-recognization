from django.db import models
from PIL import Image
import os

def face_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    safe_name = f"{instance.student_id}_{instance.full_name.replace(' ', '_')}.{ext}"
    return os.path.join('faces/known_faces', safe_name)

class UserFace(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    face_image = models.ImageField(upload_to=face_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img_path = self.face_image.path
        img = Image.open(img_path)

        # Resize ảnh để tránh quá nặng
        max_size = (512, 512)
        img.thumbnail(max_size)
        img.save(img_path, quality=85)

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"

