from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUserProfile
from adminsetup.models import Job
from django.core.mail import send_mail
from tut.job_notification_system import notify_high_match_users



@receiver(post_save, sender=Job)
def job_created_notification(sender, instance, created, **kwargs):
    if created:
        notify_high_match_users(instance)






