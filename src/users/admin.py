from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User
from enrollments.models import Enrollment

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1 # number of extra forms to display
    autocomplete_fields = ["course"]  # optional: if you want to have a search box for courses


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("Roles", {
            "fields": ("is_student", "is_instructor"),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Roles", {
            "fields": ("is_student", "is_instructor"),
        }),
    )

    list_display = ("username", "email", "is_student", "is_instructor", "is_staff")

    list_filter = ("is_student", "is_instructor", "is_staff")

    inlines = [EnrollmentInline]