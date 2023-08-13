
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

def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, id=course_id)
    
    if request.method != 'POST':
        context = {'error_message': "Invalid request method."}
        return render(request, 'error_page.html', context, status=HttpResponseServerError.status_code)
    
    # Fetch the associated enrollment for the user-course pair
    enrollment = get_object_or_404(Enrollment, user=user, course=course)

    # Extract IDs of selected choices from the POST data
    selected_choice_ids = [int(value) for key, value in request.POST.items() if key.startswith('choice_')]

    # Create a new submission and link the selected choices
    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(Choice.objects.filter(id__in=selected_choice_ids))

    # Redirect to exam results view
    return HttpResponseRedirect(reverse("onlinecourse:show_exam_result", args=(course.id, submission.id)))


def display_grade_as_score_out_of_hundred(percentage_grade):
    """Convert the percentage grade to a string format out of 100."""
    return f"{round(percentage_grade)}/100"


def get_exam_results(course, selected_choice_ids):
    """Calculate exam results, total score and the max possible score for a course."""
    exam_results = []
    total_score = 0
    max_possible_score = 0

    for question in course.question_set.all():
        max_possible_score += question.question_grade

        selected_choices = question.choice_set.filter(id__in=selected_choice_ids)
        correct_choices = question.choice_set.filter(is_correct=True)

        # Check if all selected choices match the correct choices for a question
        if set(selected_choices) == set(correct_choices):
            total_score += question.question_grade

        # Categorize selected choices based on their correctness
        correctly_selected = [choice.choice_text for choice in selected_choices if choice in correct_choices]
        incorrectly_selected = [choice.choice_text for choice in selected_choices if choice not in correct_choices]
        not_selected_but_correct = [choice.choice_text for choice in correct_choices if choice not in selected_choices]
        not_needed_answer_texts = [choice.choice_text for choice in question.choice_set.all() if choice not in correct_choices and choice not in incorrectly_selected]

        exam_results.append((question.question_text, correctly_selected, incorrectly_selected, not_selected_but_correct, not_needed_answer_texts, question.choice_set.all()))

    return exam_results, total_score, max_possible_score


def show_exam_result(request, course_id, submission_id):
    """Fetch and display the exam results for a specific submission."""
    course = get_object_or_404(Course, id=course_id)
    submission = get_object_or_404(Submission, id=submission_id)
    selected_choice_ids = submission.choices.values_list('id', flat=True)

    exam_results, total_score, max_possible_score = get_exam_results(course, selected_choice_ids)
    
    # Calculate the percentage grade and determine if the user passed the exam
    percentage_grade = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
    score_out_of_hundred = display_grade_as_score_out_of_hundred(percentage_grade)
    passed_exam = percentage_grade > 80

    # Construct context data for rendering
    context = {
        'grade': total_score,
        'percentage_grade': percentage_grade,
        'score_out_of_hundred': score_out_of_hundred,
        'passed_exam': passed_exam,
        'course': course,
        'exam_results': exam_results,
        'submission_id': submission.id,
        'course_id': course.id
    }

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
