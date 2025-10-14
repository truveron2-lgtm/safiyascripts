from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from .forms import UserRegisterForm, ProfileUpdateForm
from .models import Profile


@never_cache
def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('account:dashboard')  # Prevent logged-in users from seeing login page

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            request.session.set_expiry(3600)  # Session expires in 1 hour (you can adjust)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('account:dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'account/login.html')


@never_cache
@login_required(login_url='account:login')
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('account:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()

    return render(request, 'account/register.html', {'form': form})


@never_cache
@login_required(login_url='account:login')
def dashboard_view(request):
    """Secure dashboard visible only to authenticated users."""
    response = render(request, 'account/dashboard.html')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    return response


@never_cache
@login_required(login_url='account:login')
def profile_view(request):
    """User profile update view."""
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('account:dashboard')
    else:
        form = ProfileUpdateForm(instance=profile)

    response = render(request, 'account/profile.html', {'form': form})
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    return response


@never_cache
@login_required(login_url='account:login')
def logout_view(request):
    """Logout and clear session/cache properly."""
    logout(request)

    # Disable browser caching after logout (prevents back-button access)
    response = redirect('account:login')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    messages.info(request, 'You have been logged out successfully.')
    return response


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import Profile
from .forms import ProfileUpdateForm, UserRegisterForm

@login_required
def user_list(request):
    # Optional: only admins can view
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to view this page.")
        return redirect('account:dashboard')

    users = User.objects.all().order_by('-date_joined')
    paginator = Paginator(users, 10)  # 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'account/user_list.html', {'page_obj': page_obj})


@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f"{user.username}'s details updated successfully!")
            return redirect('account:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserRegisterForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, 'account/edit_user.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_obj': user
    })


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'User "{user.username}" deleted successfully!')
        return redirect('account:user_list')

    return render(request, 'account/delete_user_confirm.html', {'user_obj': user})
