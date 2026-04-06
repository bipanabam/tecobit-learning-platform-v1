from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.http import Http404
from . import services

def enrollment_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        lesson = services.get_lesson_detail(
            course_id=kwargs.get("course_id"),
            lesson_id=kwargs.get("lesson_id"),
        )

        if lesson is None:
            raise Http404("Lesson not found")

        if not services.user_can_access_lesson(request.user, lesson):
            request.session['next_url'] = request.path

            messages.warning(
                request,
                "Enroll to unlock this lesson."
            )
            return redirect("course_detail", course_id=lesson.course.public_id)

        return view_func(request, *args, **kwargs)

    return _wrapped_view