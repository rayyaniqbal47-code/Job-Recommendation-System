from django.db import models
from accounts.models import CustomUserProfile
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from adminsetup.models import Job

# Create your models here.

class Experience(models.Model):
    profile = models.ForeignKey(CustomUserProfile, on_delete=models.CASCADE , null=True, blank=True)
    company_name = models.CharField(max_length=255 , blank=True, null=True)
    role = models.CharField(max_length=255 , blank=True, null=True)
    years = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.role} at {self.company_name}"



class Education(models.Model):
    DEGREE_CHOICES = [
        ("High School", "High School"),
        ("Associate", "Associate Degree"),
        ("Bachelor", "Bachelor's Degree"),
        ("Master", "Master's Degree"),
        ("PhD", "PhD"),
    ]

    profile = models.ForeignKey(CustomUserProfile, on_delete=models.CASCADE , null=True, blank=True)
    institution_name = models.CharField(max_length=255 , null=True, blank=True)
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES , null=True, blank=True)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.degree}"
    

    def clean(self):
        if self.end_year and self.start_year > self.end_year:
            raise ValidationError({
                "start_year": "Start year cannot be greater than end year.",
                "end_year": "End year cannot be less than start year."
            })


class JobBookmark(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bookmarked_jobs")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="bookmarked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'job'], name='unique_user_job_bookmark')
        ]

    def __str__(self):
        return f"{self.user.email} bookmarked {self.job.title}"





