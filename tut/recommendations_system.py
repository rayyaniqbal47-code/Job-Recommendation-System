from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from adminsetup.models import Job
from accounts.models import CustomUserProfile


def clean_skills(skill_list):
    
    cleaned_skills = []

    for skill in skill_list:

        cleaned_skills.append(skill.name.strip().lower())

    return ",".join(cleaned_skills)

tfidf = TfidfVectorizer()



def build_job_matrix():

    jobs = Job.objects.filter(is_active=True).prefetch_related('skills')

    job_skill_texts = []
    job_ids = []

    for job in jobs:

        skill_text = clean_skills(job.skills.all())
        job_skill_texts.append(skill_text)
        job_ids.append(job.id)

    
    job_matrix = tfidf.fit_transform(job_skill_texts)

    return job_matrix , job_ids


def recommend_jobs(profile):

    job_matrix , job_ids = build_job_matrix()

    user_skills = profile.skills.all()
    user_skills_text = clean_skills(user_skills)
    user_experience = profile.total_years_of_experience


    has_skills = user_skills.exists()
    has_experience = user_experience > 0

    if not has_skills and not has_experience:
        return {
            "jobs":[],
            "message": "Please add skills and experience to your profile for better recommendations.",
        }


    results = []

    if has_skills:

        user_vector = tfidf.transform([user_skills_text])

        skill_similarity = cosine_similarity(user_vector , job_matrix)[0]
    
    else:

        skill_similarity = [0] * len(job_ids)


    for index , job_id in enumerate(job_ids):

        job = Job.objects.get(id=job_id)
        job_exp = job.total_years_of_experience_required


        if has_experience:

            exp_gap = job_exp - user_experience

            if exp_gap > 3:
                continue

            if exp_gap == 0:
                exp_score = 0.5
            else:
                exp_score = min(user_experience / job_exp , 1)
        else:
            exp_score = 0

        if has_skills and has_experience:

            final_score = (0.7 * skill_similarity[index]) + (0.3 * exp_score)
        
        elif has_skills:

            final_score = skill_similarity[index]
        
        elif has_experience:

            final_score = exp_score

        if final_score <= 0:
            continue

        results.append({
            "job": job,
            "skill_score": skill_similarity[index],
            "experience_score": exp_score,
            "final_score": final_score,
        })


    sorted_results = sorted(results , key=lambda x: x["final_score"], reverse=True)[:5]

    return {
        'jobs': sorted_results,
        "message":None
    }



'''
    return [
        {
            "job": item["job"],
            "final_score": item["final_score"],
            "skill_score": item["skill_score"],
            "experience_score": item["experience_score"]
        }
        for item in sorted_results[:5]
    ]
'''








'''

def recommend_jobs(profile):
    

    user_skills_text = clean_skills(profile.skills.all())
    user_experience = profile.total_years_of_experience

    user_vector = tfidf.transform([user_skills_text])

    skill_similarity = cosine_similarity(user_vector , job_matrix)[0]

    results = []


    for index , skill_score in enumerate(skill_similarity):

        job = Job.objects.get(id=job_ids[index])
        job_exp = job.total_years_of_experience_required


        exp_gap = job_exp - user_experience

        if exp_gap > 3:
            continue

        if exp_gap == 0:
            exp_score = 0.5
        else:
            exp_score = min(user_experience / job_exp , 1)

        final_score = (0.7 * skill_score) + (0.3 * exp_score)

        results.append({
            "job": job,
            "skill_score": skill_score,
            "experience_score": exp_score,
            "final_score": final_score,
        })


    sorted_results = sorted(results , key=lambda x: x["final_score"], reverse=True)

    return [
        {
            "job": item["job"],
            "final_score": item["final_score"],
            "skill_score": item["skill_score"],
            "experience_score": item["experience_score"]
        }
        for item in sorted_results[:5]
    ]



















/////////////////



def job_skills_text(job):
    return " ".join([skill.name.lower() for skill in job.skills.all()])

def user_skills_text(user_profile):
    return " ".join([skill.name.lower() for skill in user_profile.skills.all()])

def experience_similarity(user_exp, job_exp):
    max_exp = max(user_exp, job_exp, 1)
    diff = abs(user_exp - job_exp)
    sim = 1 - (diff / max_exp)
    return max(sim, 0)

def recommend_jobs(user_profile, send_email=False):
    user_text = user_skills_text(user_profile).strip()
    jobs = Job.objects.filter(is_active=True)

    # --- Skill scores ---
    if user_text:
        job_texts = [job_skills_text(job) for job in jobs]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([user_text] + job_texts)
        user_vec = tfidf_matrix[0]
        job_vecs = tfidf_matrix[1:]
        skill_scores = cosine_similarity(user_vec, job_vecs).flatten()
    else:
        skill_scores = [0] * len(jobs)

    # --- Experience scores ---
    if user_profile.total_years_of_experience > 0:
        exp_scores = [
            experience_similarity(user_profile.total_years_of_experience, job.total_years_of_experience_required)
            for job in jobs
        ]
    else:
        exp_scores = [0] * len(jobs)

    # --- Determine weights ---
    has_skills = bool(user_text)
    has_exp = user_profile.total_years_of_experience > 0

    if has_skills and has_exp:
        skill_weight, exp_weight = 0.7, 0.3
        reason_type = "Both skills and experience"
    elif has_skills:
        skill_weight, exp_weight = 1.0, 0.0
        reason_type = "Skills match"
    elif has_exp:
        skill_weight, exp_weight = 0.0, 1.0
        reason_type = "Experience match"
    else:
        skill_weight, exp_weight = 0.5, 0.5
        reason_type = "No skills or experience"

    # --- Combine scores ---
    results = []
    for i, job in enumerate(jobs):
        final_score = (skill_weight * skill_scores[i]) + (exp_weight * exp_scores[i])
        results.append({
            "job": job,
            "final_score": final_score,
            "skill_score": skill_scores[i],
            "experience_score": exp_scores[i],
            "reason": reason_type
        })

    # --- Find highest score ---
    if not results:
        return []

    max_score = max(results, key=lambda x: x["final_score"])["final_score"]
    top_jobs = [r for r in results if r["final_score"] == max_score]

  

    return top_jobs

'''