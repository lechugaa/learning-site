from django.contrib import admin

from .models import Course, Step


class StepInline(admin.StackedInline):
    model = Step


class CourseAdmin(admin.ModelAdmin):
    inlines = [StepInline]


# Register your models here.
admin.site.register(Course, CourseAdmin)
