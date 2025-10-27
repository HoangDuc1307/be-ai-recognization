from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import UserFace

admin.site.unregister(Group)
admin.site.unregister(User)

# Tùy chỉnh UserFaceAdmin
@admin.register(UserFace)
class UserFaceAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'created_at')
    search_fields = ('student_id', 'full_name')
