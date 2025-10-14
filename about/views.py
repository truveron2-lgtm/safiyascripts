from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AboutPage
from .forms import AboutPageForm

# Public view
def about_public(request):
    about = AboutPage.objects.first()
    return render(request, 'about/about_public.html', {'about': about})

# Admin / management views
@login_required
def about_edit(request):
    about, created = AboutPage.objects.get_or_create(id=1)
    if request.method == 'POST':
        form = AboutPageForm(request.POST, instance=about)
        if form.is_valid():
            form.save()
            messages.success(request, "About Us content saved successfully.")
            return redirect('about:about_edit')
    else:
        form = AboutPageForm(instance=about)
    return render(request, 'about/about_edit.html', {'form': form})
