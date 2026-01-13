from django.shortcuts import render , redirect , get_object_or_404
from applications.models import Application
from jobseeker.models import JobBookmark
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .recommendations_system import recommend_jobs
from django.contrib.auth.decorators import login_required , user_passes_test
from accounts.views import check_jobseeker_perms
from accounts.models import CustomUserProfile
from adminsetup.models import Job
from django.db.models import Q

# Create your views here.

def home(request):
    jobs = Job.objects.filter(is_active=True)
    context = {
        'jobs':jobs,
    }
    return render(request , 'tut/home.html' , context)


def job_detail(request, job_slug):
    job = get_object_or_404(Job, is_active=True, job_slug=job_slug)

    application = None
    if request.user.is_authenticated and hasattr(request.user, 'customuserprofile'):
        jobseeker = request.user.customuserprofile
        application = Application.objects.filter(job=job, jobseeker=jobseeker).first()

    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = JobBookmark.objects.filter(
            user=request.user, 
            job=job
        ).exists()
    

    context = {
        'job': job,
        'application': application,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'tut/job_detail.html', context)


from django.core.paginator import Paginator

def jobs_list(request):
    jobs_list = Job.objects.filter(is_active=True).order_by('-posted_at')
    
    paginator = Paginator(jobs_list, 1)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)  
    
    context = {
        'jobs': jobs,
    }
    return render(request, 'tut/jobs_list.html', context)




@login_required
@user_passes_test(check_jobseeker_perms)
def recommended_jobs_view(request):
    try:
        user_profile = CustomUserProfile.objects.get(customuser=request.user)
    except CustomUserProfile.DoesNotExist:
        return redirect('edit_jobseekerprofile')

    recommended_jobs = recommend_jobs(user_profile)

    context = {
        "recommended_jobs": recommended_jobs["jobs"],
        "message": recommended_jobs['message'],
    }

    return render(request, "tut/recommended_jobs.html", context)
 


def job_search(request):
    keyword = request.GET.get('keyword', '').strip()      
    location = request.GET.get('location', '').strip()  

    jobs = Job.objects.all()

    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(company_name__icontains=keyword) |
            Q(skills__name__icontains=keyword)  
        ).distinct()

    if location:
        jobs = jobs.filter(
            Q(city__icontains=location) |
            Q(state__icontains=location)
        )

    context = {
        'jobs': jobs
    }

    return render(request, 'tut/search_results.html', context)



