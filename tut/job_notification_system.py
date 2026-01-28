from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity




def clean_skills(skill_list):
    return " ".join(
        skill.name.strip().lower()
        for skill in skill_list
    )

def notify_high_match_users(job):

    from accounts.models import CustomUserProfile
    from adminsetup.models import Job

    profiles = CustomUserProfile.objects.prefetch_related('skills')
    all_jobs = Job.objects.prefetch_related('skills')

    job_texts = [clean_skills(j.skills.all())for j in all_jobs]


    tfidf = TfidfVectorizer()

    job_matrix = tfidf.fit_transform(job_texts)

    job_list = list(all_jobs)
    job_index = job_list.index(job)
    job_vector = job_matrix[job_index]


    best_profile = []
    best_score = 0


    for profile in profiles:

        score = score_job_for_user(job , profile , tfidf , job_vector)

        #print(profile.customuser.username, round(score, 2))

        if score > best_score:

            best_score = score

            best_profile = [profile]

        elif score == best_score and score > 0:

            best_profile.append(profile)

            
    for top_profile in best_profile:

        from_email = settings.DEFAULT_FROM_EMAIL

        current_site = "127.0.0.1:8000"

        mail_subject = f'New Job That Matches You: {job.title}'

        email_template = "tut/emails/job_notification.html"

        message = render_to_string(email_template , {
            "user":top_profile.customuser.username,
            "domain":current_site,
            "job":job,
        })

        to_email = top_profile.customuser.email
        mail = EmailMessage(subject=mail_subject , body=message , from_email=from_email , to=[to_email])
        mail.content_subtype = "html"
        mail.send()


    


def score_job_for_user(job, profile, tfidf, job_vector):
    
    user_skills = profile.skills.all()
    user_experience = profile.total_years_of_experience


    has_skills = user_skills.exists()
    has_experience = user_experience > 0

    if not has_skills and not has_experience:
        return 0
    
    if has_skills:

        user_text = clean_skills(user_skills)
        user_vector = tfidf.transform([user_text])
        skill_score = cosine_similarity(user_vector , job_vector)[0][0]
    
    else:

        skill_score = 0

    job_exp = job.total_years_of_experience_required

    if has_experience:
        exp_gap = job_exp - user_experience

        if exp_gap > 3:
            return 0
        
        if job_exp == 0:
            exp_score = 0.5
        else:
            exp_score = min(user_experience / job_exp, 1)
    else:
        exp_score = 0


    if has_skills and has_experience:
        final_score = (0.7 * skill_score) + (0.3 * exp_score)
    elif has_skills:
        final_score = skill_score
    else:
        final_score = exp_score

    return final_score











