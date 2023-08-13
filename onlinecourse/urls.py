from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'onlinecourse'

# Core views

core_patterns = [ 
    path(route='', view=views.CourseListView.as_view(), name='index'),
    path('registration/', views.registration_request, name='registration'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
]

# Course related views
course_patterns = [
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details'),
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),
    path('<int:course_id>/submit/', views.submit, name='submit'),
  
]

# Exam related views
exam_patterns = [
    path('course/<int:course_id>/submission/<int:submission_id>/result/', views.show_exam_result , name='show_exam_result')
 
]
urlpatterns = core_patterns + course_patterns + exam_patterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
