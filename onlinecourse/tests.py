from django.test import TestCase
from django.urls import reverse
from .models import Course, Submission, Question, Choice

class ExamResultViewTest(TestCase):
    def setUp(self):
        # Create a test course
        self.course = Course.objects.create(name='course')

        # Create a test submission for the course
        self.submission = Submission.objects.create(course=self.course)

        # Create test questions and choices
        self.question1 = Question.objects.create(course=self.course, question_text='What is 1+1?', question_grade=2)
        self.choice1_1 = Choice.objects.create(question=self.question1, choice_text='1', is_correct=False)
        self.choice1_2 = Choice.objects.create(question=self.question1, choice_text='2', is_correct=True)

    def test_exam_result_view(self):
        url = reverse('onlinecourse:show_exam_result', args=[self.course.id, self.submission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Exam results')
        self.assertContains(response, 'What is 1+1?')
        # Add more assertions based on your expected content

# Add more test cases
