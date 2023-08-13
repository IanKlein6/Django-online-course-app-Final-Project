from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Instructor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username

class Learner(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    OCCUPATION_CHOICES = [
        ('student', 'Student'),
        ('developer', 'Developer'),
        ('data_scientist', 'Data Scientist'),
        ('dba', 'Database Admin')
    ]
    occupation = models.CharField(max_length=20, choices=OCCUPATION_CHOICES, default='student')
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.user.username}, {self.occupation}"

class Course(models.Model):
    name = models.CharField(max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    passing_score = models.IntegerField(default=0)

    def __str__(self):
        return f"Name: {self.name}, Description: {self.description}"

class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

class Enrollment(models.Model):
    COURSE_MODES = [
        ('audit', 'Audit'),
        ('honor', 'Honor'),
        ('BETA', 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default='audit')
    rating = models.FloatField(default=5.0)

class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=100, default='Default Title, Please add a New One')
    question_text = models.TextField(max_length=1000, default='Default Question Text, Please add a New One')
    question_grade = models.PositiveBigIntegerField()

    def is_get_score(self, selected_ids):
        all_answers = self.choice_set.filter(is_correct=True).count()
        selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
        return all_answers == selected_correct

class Choice(models.Model):
    choice_text = models.CharField(max_length=200, default="choice_text")
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
