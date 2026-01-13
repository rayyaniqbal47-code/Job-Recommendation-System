from django.shortcuts import render , redirect , get_object_or_404
from accounts.forms import CustomUserForm
from accounts.models import CustomUser , CustomUserProfile
from django.contrib import messages
from django.contrib import auth
from accounts.utils import detectuser , send_verification_email
from django.contrib.auth.decorators import login_required , user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordChangeForm
from jobseeker.models import Job , JobBookmark 
from applications.models import Application


# Create your views here.


# restrict the jobseeker from accessing the admin page

def check_jobseeker_perms(user):

    if user.is_staff or user.is_superadmin:
        raise PermissionDenied
    
    if user.is_job_seeker:
        return True
    else:
        return PermissionDenied


# restrict the admin from accessing the jobseeker page

def check_admin_perms(user):
    if user.is_staff and user.is_superadmin:
        return True
    else:
        raise PermissionDenied
    


def registration(request):

    if request.user.is_authenticated:
        return redirect('myAccount')

    elif request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():

            # create the user using create_user method

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            user.is_job_seeker = True
            user.save()
            messages.success(request , 'account register successfully')

            # send verification email

            mail_subject = 'please activate your account'

            email_template = 'accounts/emails/accounts_verification_email.html'

            send_verification_email(request , user , mail_subject , email_template)

            return redirect('registration')

    else:
        form = CustomUserForm()
    context = {
        'form':form,
    }
    return render(request , 'accounts/registration.html' , context)

def activate(request , uidb64 , token):
        # activate the user by setting the is_active status to true
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except(TypeError , ValueError , OverflowError , CustomUser.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user , token):
        user.is_active = True
        user.save()
        messages.success(request , 'congrats your account is activated')
        return redirect('myAccount')
    else:
        messages.error(request , 'invalid link')
        return redirect('myAccount')
 

def forgot_password(request):

    if request.method == 'POST':

        email = request.POST['email']

        if CustomUser.objects.filter(email=email).exists():

            user = CustomUser.objects.get(email__exact=email)

            # send reset password email

            mail_subject = 'reset your password'

            email_template = 'accounts/emails/reset_password_email.html'

            send_verification_email(request , user , mail_subject , email_template)

            messages.success(request , 'reset password link has been sent to your email address')

            return redirect('login')
        else:
            messages.error(request , 'account does not exist')
            return redirect('forgot_password')
        

    return render(request , 'accounts/forgot_password.html')


def reset_password_validate(request , uidb64 , token):

    # validate the user by decoding the token and user pk

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except(ValueError , TypeError , OverflowError , CustomUser.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user , token):
        request.session['uid'] = uid
        messages.info(request , 'please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request , 'this link has been expired')
        return redirect('myAccount')
    

def reset_password(request):

    if request.method == 'POST':

        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password')

        uid = request.session.get('uid')
        if not uid:
            messages.error(request, 'Session expired. Please use the reset link again.')
            return redirect('forgot_password')

        try:
            user = CustomUser.objects.get(pk=uid)
            user.set_password(password)
            user.is_active = True
            user.save()
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found. Please try again.')
            return redirect('forgot_password')

        

        # Clear uid from session for security
        request.session.pop('uid', None)

        messages.success(request, 'Your password has been reset successfully.')
        return redirect('login')

    return render(request, 'accounts/reset_password.html')


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user , data=request.POST)
        if form.is_valid():
            form.save()
            logout(request)
            return redirect('login')
    else:
        form = PasswordChangeForm(user=request.user)
    
    context = {
        'form':form,
    }
    return render(request, 'accounts/password_change.html' , context)



def login(request):

    if request.user.is_authenticated:
        return redirect('myAccount')

    if request.method == 'POST':

        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(request, username=email, password=password)
        if user is not None:

            auth.login(request , user)
            messages.success(request , 'login success')

            return redirect('myAccount')
        else:
            messages.success(request , 'invalid credentials')
            return redirect('login')
            
    return render(request , 'accounts/login.html')


@login_required
def logout(request):

    if request.method == 'POST':

        auth.logout(request)
        messages.success(request , 'logout success')

        return redirect('login')

@login_required
def myAccount(request):

    user = request.user
    redirecturl = detectuser(user=user)

    return redirect(redirecturl)


@login_required
@user_passes_test(check_admin_perms)
def admin_dashboard(request):


    applications = Application.objects.all()[:3]

    applications_accepted = Application.objects.filter(status='accepted').count()

    applications_rejected = Application.objects.filter(status='rejected').count()


    context = {
        'applications_counts': applications.count(),
        'applications':applications,
        'applications_accepted':applications_accepted,
        'applications_rejected':applications_rejected,
    }
    return render(request , 'accounts/admin_dashboard.html' , context)


@login_required
@user_passes_test(check_jobseeker_perms)
def jobseeker_dashboard(request):

    profile = get_object_or_404(CustomUserProfile , customuser=request.user)

    applications = Application.objects.filter(jobseeker=profile)[:3]

    applications_counts = applications.count()

    bookmarks = JobBookmark.objects.filter(user=request.user)

    context = {
        'applications_counts': applications_counts,
        'bookmarks':bookmarks.count(),
        'applications':applications
    }

    return render(request , 'accounts/jobseeker_dashboard.html' , context)


