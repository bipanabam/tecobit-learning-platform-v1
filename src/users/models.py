from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField


def user_profile_public_id(instance, *args, **kwargs):
    return f"users/{instance.username}/profile"

class User(AbstractUser):
    # additional fields for our user model
    is_student = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    
    profile_image = CloudinaryField(
        'image',
        public_id=user_profile_public_id,
        overwrite=True,
        blank=True,
        null=True
    )
    
    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def get_profile_image_url(self):
        if self.profile_image:
            return self.profile_image.url
        return None
    
    def __str__(self):
        return self.username
    