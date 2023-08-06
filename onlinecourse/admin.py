from django.contrib import admin
# <HINT> Import any new Models here
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission

# <HINT> Register QuestionInline and ChoiceInline classes here
class ChoiseInLine(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionInLine(admin.TabularInline):
    model = Question
    inlines = [ChoiseInLine]
    extra = 1

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


# Register your models here.
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']
    inlines = [QuestionInLine]

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'question_text', 'question_grade')
    fieldsets = [
        (None, {'fields': ['title', 'course','question_text', 'question_grade']}),
    ]

class ChoiceAdmin(admin.ModelAdmin):
    pass    

class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline, QuestionInLine]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']

class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']


# <HINT> Register Question and Choice models here
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Submission)

