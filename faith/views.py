from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FaithText
from .forms import FaithTextForm

# Public view
def faith_public(request):
    text = FaithText.objects.filter(active=True).first()
    return render(request, 'faith/faith_public.html', {'text': text})

# Admin views
@login_required
def faith_add(request):
    if request.method == 'POST':
        form = FaithTextForm(request.POST)
        if form.is_valid():
            faith = form.save(commit=False)
            faith.author = request.user
            if faith.active:
                # Deactivate all other texts
                FaithText.objects.update(active=False)
            faith.save()
            messages.success(request, "Faith text added successfully.")
            return redirect('faith:faith_list')
    else:
        form = FaithTextForm()
    return render(request, 'faith/faith_form.html', {'form': form, 'title': 'Add Faith Text'})

@login_required
def faith_list(request):
    texts = FaithText.objects.all()
    return render(request, 'faith/faith_list.html', {'texts': texts})

@login_required
def faith_delete(request, pk):
    text = get_object_or_404(FaithText, pk=pk)
    if request.method == 'POST':
        text.delete()
        messages.success(request, "Faith text deleted successfully.")
        return redirect('faith:faith_list')
    return render(request, 'faith/faith_confirm_delete.html', {'text': text})

@login_required
def faith_edit(request, pk):
    faith = get_object_or_404(FaithText, pk=pk)
    if request.method == 'POST':
        form = FaithTextForm(request.POST, instance=faith)
        if form.is_valid():
            if form.cleaned_data['active']:
                FaithText.objects.update(active=False)  # deactivate others
            form.save()
            messages.success(request, "Faith text updated successfully.")
            return redirect('faith:faith_list')
    else:
        form = FaithTextForm(instance=faith)
    return render(request, 'faith/faith_form.html', {'form': form, 'title': 'Edit Faith Text'})
