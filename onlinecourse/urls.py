from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'onlinecourse'
urlpatterns = [
    path(route='', view=views.CourseListView.as_view(), name='index'),
    path('registration/', views.registration_request, name='registration'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    # ex: /onlinecourse/5/
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details'),
    # ex: /enroll/5/
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),
    #question_quiz
    path('get_quiz_questions/<int:course_id>/', views.get_quiz_questions, name='get_quiz_questions'),
    # Submit
    path('<int:course_id>/submit/', views.submit, name='submit'),
    # Exam Results
    path('<int:course_id>/results/<int:submission_id>/', views.show_exam_result, name='show_exam_result'),
    
 ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
