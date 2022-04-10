from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='no_picture.png', upload_to='avatars')

    def __str__(self):
        return f"Profile of: {self.user.first_name} {self.user.last_name}"