from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.http import Http404
from . import services

def enrollment_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        course_id = kwargs.get("course_id")
        course = services.get_course_detail(course_id=course_id)

        if course is None:
            raise Http404("Course not found")

        if not services.user_has_access_to_course(request.user, course):
            request.session['next_url'] = request.path
            
            messages.warning(
                request,
                "You need to enroll in this course to access the lessons."
            )
            return redirect("course_detail", course_id=course_id)

        return view_func(request, *args, **kwargs)

    return _wrapped_view