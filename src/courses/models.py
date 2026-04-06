from django.db import models
from django.utils.text import slugify
import uuid
import helpers
from cloudinary.models import CloudinaryField

helpers.cloudinary_init()

# Create your models here.
class AccessRequirement(models.TextChoices):
    ANYONE = "any", "Anyone"
    ENROLLED = "enrolled", "Enrolled"

class CourseStatus(models.TextChoices):
    COMPLETED = "completed", "Completed"
    COMING_SOON = "soon", "Coming Soon"
    ONGOING = "ongoing", "Ongoing"
    DRAFT = "draft", "Draft"
    
class VideoType(models.TextChoices):
    CLOUDINARY = "cloudinary", "Cloudinary"
    YOUTUBE = "youtube", "YouTube"
    

def handle_upload(instance, filename):
    return f"{filename}"

def generate_public_id(instance, *args, **kwargs):
    title = instance.title
    unique_id = str(uuid.uuid4()).replace("-", "")[:5]
    if not title:
        return unique_id
    slug = slugify(title)
    unique_id_short = unique_id[:5]
    return f"{slug}-{unique_id_short}"

def get_public_id_prefix(instance, *args, **kwargs):
    if hasattr(instance, 'path'):
        path = instance.path
        if path.endswith("/"):
            path = path[:-1]
        if path.startswith("/"):
            path = path[1:]
        return path
    public_id = instance.public_id
    model_class = instance.__class__
    model_name = model_class.__name__
    model_name_slug = slugify(model_name)
    if not public_id:
        return f"{model_name_slug}"
    return f"{model_name_slug}/{public_id}"

def get_display_name(instance, *args, **kwargs):
    if hasattr(instance, 'get_display_name'):
        return instance.get_display_name()
    elif hasattr(instance, 'title'):
        return instance.title
    model_class = instance.__class__
    model_name = model_class.__name__
    return f"{model_name} Upload"

class Course(models.Model):
    title = models.CharField(max_length=125)
    description = models.TextField(blank=True, null=True)
    public_id = models.CharField(max_length=140, blank=True, null=True, db_index=True)
    # image = models.ImageField(upload_to=handle_upload, blank=True, null=True)
    image = CloudinaryField("image", 
                            resource_type="image",
                            null=True, 
                            public_id_prefix=get_public_id_prefix,
                            display_name = get_display_name,
                            tags=['course', 'thumbnail'])
    access = models.CharField(
        max_length=20, 
        choices=AccessRequirement.choices,
        default=AccessRequirement.ENROLLED)
    status = models.CharField(
        max_length=10, 
        choices=CourseStatus.choices, 
        default=CourseStatus.DRAFT)
    
    lecturer = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, related_name="courses")
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.public_id == "" or self.public_id is None:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)

    @property
    def path(self):
        return f"/courses/{self.public_id}"
    
    def get_absolute_url(self):
        return self.path
    
    def get_display_name(self):
        return f"{self.title} - Course"
    
    def get_thumbnail(self):
        if not self.image:
            return None
        return helpers.get_cloudinary_image_object(
            self,
            field_name="image",
            as_html=False,
            width=382,
        )
    
    def get_display_image(self):
        if not self.image:
            return None
        return helpers.get_cloudinary_image_object(
            self,
            field_name="image",
            as_html=False,
            width=750,
        )
    
    @property
    def is_completed(self):
        return self.status == CourseStatus.COMPLETED
    
    def __str__(self):
        return self.title
    

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=125)
    description = models.TextField(blank=True, null=True)
    public_id = models.CharField(max_length=140, blank=True, null=True, db_index=True)
    thumbnail = CloudinaryField("image", 
                            resource_type="image",
                            public_id_prefix=get_public_id_prefix,
                            display_name = get_display_name,
                            tags=['lesson', 'thumbnail'],
                            blank=True, null=True)
    video_type = models.CharField(
        max_length=20,
        choices=VideoType.choices,
        default=VideoType.CLOUDINARY
    )

    video_url = models.URLField(blank=True, null=True)  # for YouTube
    video = CloudinaryField("video", 
                            public_id_prefix=get_public_id_prefix,
                            display_name = get_display_name,
                            type="private",
                            tags=['video', 'lesson'],
                            blank=True, null=True, resource_type="video")
    order = models.IntegerField(default=0)
    can_preview = models.BooleanField(default=False, help_text="If user does not have access to course, "
    "can they see this?")
    status = models.CharField(
        max_length=10, 
        choices=CourseStatus.choices, 
        default=CourseStatus.ONGOING)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.public_id == "" or self.public_id is None:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)

    @property
    def is_coming_soon(self):
        return self.status == CourseStatus.COMING_SOON
    
    @property
    def has_video(self):
        if self.video_type == VideoType.YOUTUBE:
            return self.video_url is not None
        return self.video  is not None
    
    @property
    def requires_enrollment(self):
        return self.course.access == AccessRequirement.ENROLLED

    @property
    def path(self):
        course_path = self.course.path
        if course_path.endswith("/"):
            course_path = course_path[:-1]
        return f"{course_path}/lessons/{self.public_id}"
    
    def get_absolute_url(self):
        return self.path
    
    def get_display_name(self):
        return f"{self.title} - {self.course.get_display_name()}"
    
    def get_thumbnail(self):
        if self.thumbnail:
            return helpers.get_cloudinary_image_object(
            self,
            field_name="thumbnail",
            as_html=False,
            width=382,
        )
    
        return helpers.get_cloudinary_image_object(
            self,
            field_name="video",
            format='jpg',
            as_html=False,
            width=382,
        )
        
    def get_next_lesson(self):
        return Lesson.objects.filter(
            course=self.course, 
            order__gt=self.order
        ).order_by('order').first()

    def get_previous_lesson(self):
        return Lesson.objects.filter(
            course=self.course, 
            order__lt=self.order
        ).order_by('-order').first()
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', '-updated']

