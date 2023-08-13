
from .models import Course, Enrollment, Submission, Choice, Question
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.views import generic
import logging
from django.http import JsonResponse #for get_quiz_question

# Logger Instace 
logger = logging.getLogger(__name__)


# VIEWS: 

# HTLM exam questions request 
print("before get quiz questions")
def get_quiz_questions(request, course_id):
    print("inside get quiz questioons")
    course = get_object_or_404(Course, pk=course_id)
    quiz_questions = Question.objects.filter(course=course)
    data = []
    for question in quiz_questions:
        question_data = {
            'question_text': question.question_text,
            'choices': [{'id': choice.id, 'text': choice.choice_text} for choice in question.choice_set.all()]
        }
        data.append(question_data)
    return JsonResponse(data, safe=False)


print("before registration")
def registration_request(request):
    print("inside registration")
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)

print("before login request")
def login_request(request):
    print("insdie login request")
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    
print("before logout")
def logout_request(request):
    print("inside logout")
    logout(request)
    return redirect('onlinecourse:index')

print("before enrolled check")
def check_if_enrolled(user, course):
    print("inside enrolled check")
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
print("before courselview")
class CourseListView(generic.ListView):
    print("inside courselview")
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'
    print("inside courveiw, before quryset")
    def get_queryset(self):
        print("inside get queryset")
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        print("finnished query set")
        return courses 

        

class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'

print("before enroll")
def enroll(request, course_id):
    print("inside enroll")
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()
    print("return course list view")
    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))

print("before submit")
def submit(request, course_id):
    print(course_id, "course id submit")
    # Get current user/course object
    user = request.user
    course = get_object_or_404(Course, id=course_id)
    

    # Get associated enrollment object
    enrollment = get_object_or_404(Enrollment, user=user, course=course)

    if request.method == 'POST':
        # Create new submission object referring to enrollment
        submission = Submission.objects.create(enrollment=enrollment)

        # Collect selected choices from HTTP request
        selected_choice_ids = []
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                choice_id = int(value)
                selected_choice_ids.append(choice_id)

        # Add each selected choice object to submission object
        selected_choices = Choice.objects.filter(id__in=selected_choice_ids)
        submission.choices.set(selected_choices)

        # Redirect to show_exam_result view with submission id
        print("before return")
        return HttpResponseRedirect(reverse(viewname="onlinecourse:show_exam_result", args=(course.id, submission.id)))
                                                                                            
    
    else:
        print("after return in else")
        error_message = "An error occurred while processing your submission."
        context = {'error_message': error_message}
        return render(request, 'error_page.html', context, status=HttpResponseServerError.status_code)

print("before extract answers")
#A example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
    print("inside extract answers")
    submitted_anwsers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_anwsers.append(choice_id)
    return submitted_anwsers

print("before show exam reuslts")
def show_exam_result(request, course_id, submission_id):
    print("inside show exam results", course_id, submission_id, )
    # Get course and submission based on their ids
    course = get_object_or_404(Course, id=course_id)
    submission = get_object_or_404(Submission, id=submission_id)

    # Get selected choice ids from submission record
    selected_choice_ids = submission.choices.values_list('id', flat=True)

    # Calculate total score and maximum possible score
    total_score = 0
    max_possible_score = 0
    exam_results = []
    for question in course.question_set.all():
        max_possible_score += question.question_grade
        correct_choice_ids = question.choice_set.filter(is_correct=True).values_list('id', flat=True)
        selected_correct = all(choice_id in selected_choice_ids for choice_id in correct_choice_ids)
        if selected_correct:
            total_score += question.question_grade

        # Retrieve selected choice text
        selected_choices = Choice.objects.filter(id__in=selected_choice_ids)
        selected_choice_texts = [choice.choice_text for choice in selected_choices]

        # Append question details to the exam_results
        exam_results.append((question.question_text, selected_choice_texts, selected_correct))

    # Calculate the percentage grade
    percentage_grade = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0

    # Determine if the learner passed the exam
    passed_exam = percentage_grade > 80
    context = {
        'grade': total_score,
        'percentage_grade': percentage_grade,
        'passed_exam': passed_exam,
        'course': course,
        'exam_results': exam_results,
        'submission_id': submission.id,
        'course_id': course.id
    }

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)

# def show_exam_result(request, course_id, submission_id):
#     print("show exam results: ids ", course_id, submission_id)
#     context = {}
#     course = Course.objects.get(id = course_id)
#     submit = Submission.objects.get(id = submission_id)
#     print(course, submit)
#     selected = Submission.objects.filter(id = submission_id).values_list('choices',flat = True)
#     score = 0
#     for i in submit.choices.all().filter(is_correct=True).values_list('question_id'):
#         score += Question.objects.filter(id=i[0]).first().grade    
#     context['selected'] = selected
#     context['grade'] = score
#     context['course'] = course
#     context['course_id'] = course_id      
#     context['submission_id'] = submission_id 
#     print(submission_id, course_id)
#     return  render(request, 'onlinecourse/exam_result_bootstrap.html', context)
# print("end")