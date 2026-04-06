from .models import Course, Lesson, CourseStatus

from enrollments.models import Enrollment

def get_published_courses():
    return Course.objects.filter(status__in=[CourseStatus.ONGOING,CourseStatus.COMPLETED,])


def get_course_detail(course_id=None):
    if course_id is None:
        return None
    obj = None
    try:
        obj = Course.objects.get(
            public_id=course_id, 
            status=CourseStatus.ONGOING)
    except:
        pass
    return obj

def get_course_lessons(course_obj):
    lessons = Lesson.objects.none()
    if not isinstance(course_obj, Course):
        return lessons
    lessons = course_obj.lessons.filter(
            course__status=CourseStatus.ONGOING,
            status__in=[CourseStatus.ONGOING, 
                        CourseStatus.COMPLETED,
                        CourseStatus.COMING_SOON])
    return lessons


def get_lesson_detail(course_id=None, lesson_id=None):
    if lesson_id is None or course_id is None:
        return None
    obj = None
    try:
        obj = Lesson.objects.get(
            course__public_id=course_id,
            course__status=CourseStatus.ONGOING,
            public_id=lesson_id, 
            status__in=[CourseStatus.ONGOING,
                        CourseStatus.COMPLETED,
                        CourseStatus.COMING_SOON])
    except:
        pass
    
    return obj

def user_has_access_to_course(user, course):
    if course.access == "any":
        return True
    
    if not user.is_authenticated:
        return False

    return Enrollment.objects.filter(
        student=user,
        course=course,
        is_active=True
    ).exists()