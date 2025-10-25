from django.db import models

# Create your models here.
class UserFace(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    image_filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


