from django.db import models
from accounts.models import CustomUserProfile
from adminsetup.models import Job

# Create your models here.

STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    jobseeker = models.ForeignKey(CustomUserProfile, on_delete=models.SET_NULL, null=True)
    resume = models.FileField(upload_to="application/resumes")
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['job', 'jobseeker'], name='unique_application')
        ]




