from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Course, Submission, Enrollment

class ExamResultViewTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Create a course
        self.course = Course.objects.create(name='Test Course', description='A test course')

        # Create an enrollment
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)

        # Create a submission
        self.submission = Submission.objects.create(course=self.course, enrollment=self.enrollment)

    def test_show_exam_result(self):
        url = reverse('onlinecourse:show_exam_result', args=[self.course.id, self.submission.id])
        response = self.client.get(url)
        
        # Check that the response has a 200 status code
        self.assertEqual(response.status_code, 200)

        # Check that the submission_id is available in the context
        self.assertIn('submission_id', response.context)

        # Check that the submission_id in the context matches the one we created
        self.assertEqual(response.context['submission_id'], self.submission.id)
