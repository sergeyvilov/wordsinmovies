from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db import transaction
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .forms import UserForm, ProfileForm, SignupForm, ChangePswdForm
from datetime import timedelta
from django.utils import timezone

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('wordsinmovies_main:index'))

def logged_in(request):
    messages.success(request, "You are logged in.")
    # today = date.today().strftime("%Y-%m-%d")
    last_connection = request.user.profile.last_connection
    #last_connection=str(last_connection)
    #if previous query quota was set more than 24 hours ago, renew the quota
    if last_connection <= timezone.now() - timedelta(days=1):
        request.user.profile.n_requests = 100
        request.user.profile.last_connection = timezone.now()
        request.user.profile.save()
    return HttpResponseRedirect(reverse('wordsinmovies_main:index'))

def register(request):
    """Register a new user."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('wordsinmovies_main:index'))
    if request.method != 'POST':
        form = SignupForm()
    else:
        # send activation link to e-mail
        form = SignupForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username=user.email
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your WordsInMovies account'
            message = render_to_string('users/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message,  settings.EMAIL_FROM_ADDRESS, to=[to_email],
            )
            email.send()
            messages.warning(request, 'Please check your email to complete the registration.')
            return HttpResponseRedirect(reverse('wordsinmovies_main:index'))

    return render(request, 'users/register.html', {'form':form})

#when the user clicks on the activation link in e-mail
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Thank you for your email confirmation. We invite your to fill in your profile.', extra_tags='alert')
        return HttpResponseRedirect(reverse('users:profile'))
    else:
        messages.error(request, 'Activation link is invalid.')
        return HttpResponseRedirect(reverse('wordsinmovies_main:index'))

@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.username=user.email
            user.save()
            profile_form.save()
            messages.success(request, 'Your profile has been successfully updated!')
            return HttpResponseRedirect(reverse('users:profile'))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

#send password renewal link to e-mail
def forgot_my_pswd(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('wordsinmovies_main:index'))
    form = UserForm()
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
                user = User.objects.filter(email=user_form.cleaned_data.get('email'))
                if user:
                    user = user[0]
                    current_site = get_current_site(request)
                    mail_subject = 'Reset your WordsInMovies password'
                    message = render_to_string('users/reset_pswd_email.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'uid':urlsafe_base64_encode(force_bytes(user.id)),
                            'token':account_activation_token.make_token(user),
                    })
                    to_email = user_form.cleaned_data.get('email')
                    email = EmailMessage(
                            mail_subject, message, to=[to_email]
                    )
                    email.send()
                    messages.success(request, 'A link has been sent to your e-mail address.')
                    return HttpResponseRedirect(reverse('wordsinmovies_main:index'))
                else:
                    messages.error(request, 'This e-mail adress is not registered.')

    return render(request, 'users/forgot_my_pswd.html', {'form':form})

#when the user clicks on password renewal link in e-mail
def reset_pswd(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        login(request, user)
        return HttpResponseRedirect(reverse('users:change_pswd'))
    else:
        messages.error(request, 'Activation link is invalid.')
        return HttpResponseRedirect(reverse('wordsinmovies_main:index'))

@login_required
def change_pswd(request):
    if request.method != 'POST':
        form = ChangePswdForm(instance=request.user)
    else:
        # Process completed form.
        form = ChangePswdForm(data=request.POST, instance=request.user)
        if form.is_valid():
            user=form.save()
            login(request, user)
            messages.success(request, 'Your password has been successfully changed.')
            return HttpResponseRedirect(reverse('wordsinmovies_main:index'))
    return render(request, 'users/change_pswd.html', {'form':form})


@login_required
def delete_profile(request):
    user_id = request.user.id
    logout(request)
    User.objects.filter(id=user_id).delete()
    messages.success(request, 'Your account was successfully deleted.')
    return HttpResponseRedirect(reverse('wordsinmovies_main:index'))
