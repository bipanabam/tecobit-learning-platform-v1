from django.shortcuts import render
from django.http import Http404, JsonResponse

from . import services
from .decorators import enrollment_required

import helpers

# Create your views here.
def course_list_view(request):
    queryset = services.get_published_courses()
    # return JsonResponse({"data":[x.path for x in queryset]})
    context = {
        "courses": queryset,
    }
    return render(request, "courses/course_list.html", context)

def course_detail_view(request, course_id=None, *args, **kwargs):
    course_obj = services.get_course_detail(course_id=course_id)
    if course_obj is None:
        raise Http404("Course not found")
    lessons_queryset = services.get_course_lessons(course_obj)
    has_access =  services.user_has_access_to_course(request.user, course_obj)
    context = {
        "course": course_obj,
        "lessons": lessons_queryset,
        "has_access": has_access
    }
    # return JsonResponse({"data": course_obj.title, "lessons": [x.path for x in lessons_queryset]})
    return render(request, "courses/course_detail.html", context)

@enrollment_required
def lesson_detail_view(request, course_id=None, lesson_id=None, *args, **kwargs):
    lesson_obj = services.get_lesson_detail(
        course_id=course_id, 
        lesson_id=lesson_id,
    )
    if lesson_obj is None:
        raise Http404("Course not found")
    if not services.user_can_access_lesson(request.user, lesson_obj):
        request.session['next_url'] = request.path
        print(request.path)
        return render(request, "courses/enrollment-required.html", {})

    template_name = "courses/lesson-coming-soon.html"
    context = {
        "lesson": lesson_obj
    }
    if not lesson_obj.is_coming_soon and lesson_obj.has_video:
        template_name = "courses/lesson.html"
        all_lessons = services.get_course_lessons(lesson_obj.course)
        context['all_lessons'] = all_lessons
        
        video_embed_html = helpers.get_video_embed(
            lesson_obj,
        )
        context['video_embed'] = video_embed_html
    
    return render(request, template_name, context)