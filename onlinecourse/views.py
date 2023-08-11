from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Course, Enrollment, Submission, Choice, Question
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
from django.http import JsonResponse #for get_quiz_question

# Logger Instace 
logger = logging.getLogger(__name__)


# VIEWS: 

# HTLM exam questions request 
def get_quiz_questions(request, course_id):
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



def registration_request(request):
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


def login_request(request):
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


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))



# <HINT> Create a submit view to create an exam submission record for a course enrollment,
# you may implement it based on following logic:
         # Get user and course object, then get the associated enrollment object created when the user enrolled the course
         # Create a submission object referring to the enrollment
         # Collect the selected choices from exam form
         # Add each selected choice object to the submission object
         # Redirect to show_exam_result with the submission id
def submit(request, course_id):
    # Get user and course objects
    user = request.user
    course = get_object_or_404(Course, id=course_id)

    # Get associated enrollment object created when user enrolled course
    enrollment = get_object_or_404(Enrollment, user=user, course=course)

    if request.method == 'POST':
        # Create submission object referring to enrollment
        submission = Submission.objects.create(enrollment=enrollment)

        # Collect selected choices from exam form
        for question in course.lesson_set.all().values_list('question', flat=True):
            choice_id = request.POST.get(f'choice_{question.id}')
            if choice_id:
                # Add each selected choice object to submission object
                choice = get_object_or_404(Choice, id=choice_id)
                submission.choices.add(choice)

        # Redirect exam results page with submission ID
        return redirect('exam_results_bootstrap', submission_id=submission.id)

    else:
        # If form is not submitted, render exam submission page
        questions = course.get_all_questions()
        context = {
            'course': course,
            'questions': questions,
        }
        return render(request, 'submit_exam.html', context)


#A example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
    submitted_anwsers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_anwsers.append(choice_id)
    return submitted_anwsers


# <HINT> Create an exam result view to check if learner passed exam and show their question results and result for each question,
# you may implement it based on the following logic:
        # Get course and submission based on their ids
        # Get the selected choice ids from the submission record
        # For each selected choice, check if it is a correct answer or not
        # Calculate the total score
def show_exam_result(request, course_id, submission_id):
    #course/submission based on their ids
    course = get_object_or_404(Course, id=course_id)
    submission = get_object_or_404(Submission, id=submission_id)

    # Get selected choice ids from submission record
    selected_choice_ids = submission.choices.values_list('id', flat=True)

    # For each selected choice, check if it is a correct answer or not
    total_score = 0
    results = []
    for question in course.question_set.all():
        selected_choices = []
        correct_choices = []
        for choice in question.choice_set.all():
            if choice.id in selected_choice_ids:
                selected_choices.append(choice)
                if choice.is_correct:
                    correct_choices.append(choice)

        # Calculate score for question
        question_score = 0
        if set(selected_choices) == set(correct_choices):
            question_score = question.question_grade
            total_score += question_score

        # Prepare question result data
        result_data = {
            'question_text': question.question_text,
            'selected_choices': selected_choices,
            'correct_choices': correct_choices,
            'question_score': question_score,
        }
        results.append(result_data)

    #Check if learner passed exam
    passing_score = course.passing_score
    passed_exam = total_score >= passing_score

    context = {
        'course': course,
        'submission': submission,
        'results': results,
        'total_score': total_score,
        'passed_exam': passed_exam,
    }

    return render(request, 'exam_result.html', context)


