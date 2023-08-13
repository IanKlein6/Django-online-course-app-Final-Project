from django.contrib import admin
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionInline(admin.TabularInline):
    model = Question
    inlines = [ChoiceInline]
    extra = 1

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'question_text', 'question_grade')
    fieldsets = [
        (None, {'fields': ['title', 'course', 'question_text', 'question_grade']}),
    ]

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']
    inlines = [LessonInline]

class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']
    inlines = [QuestionInline]

# Registration of models to the admin site
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Submission)
