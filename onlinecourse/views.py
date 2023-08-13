from .models import Course, Enrollment, Submission, Choice, Question
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponseServerError, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.views import generic
import logging

# Logger Instance 
logger = logging.getLogger(__name__)


# Views for the online course application
def get_quiz_questions(request, course_id):
    """Fetch all quiz questions for a specific course."""
    course = get_object_or_404(Course, pk=course_id)
    data = [{
        'question_text': question.question_text,
        'choices': [{'id': choice.id, 'text': choice.choice_text} for choice in question.choice_set.all()]
    } for question in Question.objects.filter(course=course)]
    return JsonResponse(data, safe=False)


def get_exam_results(course, selected_choice_ids):
    """Calculate exam results, total score, and the max possible score for a course."""
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


def registration_request(request):
    """Register a new user or display registration form."""
    if request.method == 'POST':
        username = request.POST['username']
        try:
            User.objects.get(username=username)
            return render(request, 'onlinecourse/user_registration_bootstrap.html', {'message': "User already exists."})
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                first_name=request.POST['firstname'],
                last_name=request.POST['lastname'],
                password=request.POST['psw']
            )
            login(request, user)
            return redirect("onlinecourse:index")
    return render(request, 'onlinecourse/user_registration_bootstrap.html')


def login_request(request):
    """Authenticate and log a user in, or display login form."""
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['psw'])
        if user:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            return render(request, 'onlinecourse/user_login_bootstrap.html', {'message': "Invalid username or password."})
    return render(request, 'onlinecourse/user_login_bootstrap.html')


def logout_request(request):
    """Log the user out."""
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    """Check if a user is enrolled in a course."""
    return Enrollment.objects.filter(user=user, course=course).exists()


class CourseListView(generic.ListView):
    """Display a list of courses."""
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'
    def get_queryset(self):
        courses = Course.objects.order_by('-total_enrollment')[:10]
        if self.request.user.is_authenticated:
            for course in courses:
                course.is_enrolled = check_if_enrolled(self.request.user, course)
        return courses 


class CourseDetailView(generic.DetailView):
    """Display detailed view for a course."""
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    """Enroll a user in a course."""
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    if user.is_authenticated and not check_if_enrolled(user, course):
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()
    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


def submit(request, course_id):
    """Submit exam answers and record choices."""
    if request.method != 'POST':
        return render(request, 'error_page.html', {'error_message': "Invalid request method."}, status=HttpResponseServerError.status_code)

    user, course = request.user, get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, user=user, course=course)

    selected_choice_ids = [int(value) for key, value in request.POST.items() if key.startswith('choice_')]
    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(Choice.objects.filter(id__in=selected_choice_ids))

    return HttpResponseRedirect(reverse("onlinecourse:show_exam_result", args=(course.id, submission.id)))


def show_exam_result(request, course_id, submission_id):
    """Display the results of a user's exam submission."""
    course = get_object_or_404(Course, id=course_id)
    submission = get_object_or_404(Submission, id=submission_id)
    
    exam_results, total_score, max_possible_score = get_exam_results(course, submission.choices.values_list('id', flat=True))
    
    percentage_grade = (total_score / max_possible_score) * 100 if max_possible_score else 0

    context = {
        'grade': total_score,
        'percentage_grade': percentage_grade,
        'score_out_of_hundred': f"{round(percentage_grade)}/100",
        'passed_exam': percentage_grade > 80,
        'course': course,
        'exam_results': exam_results,
        'submission_id': submission.id,
        'course_id': course.id
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
