from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import ContactMessage
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from django.contrib.auth.decorators import login_required




from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ContactForm

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()

            # Clear any previous messages before adding new one
            storage = messages.get_messages(request)
            storage.used = True  

            messages.success(request, "Your request has been submitted successfully! We’ll get back to you soon.")
            return redirect('contact:contact')
    else:
        form = ContactForm()

    return render(request, "contact/contact.html", {"form": form})

@login_required
def contact_list(request):
    query = request.GET.get('q', '')
    contacts = ContactMessage.objects.all().order_by('-submitted_at')

    if query:
        contacts = contacts.filter(Q(name__icontains=query) | Q(email__icontains=query))

    context = {
        'contacts': contacts,
        'query': query,
    }
    return render(request, 'contact/contact_list.html', context)

@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(ContactMessage, pk=pk)
    return render(request, 'contact/contact_detail.html', {'contact': contact})

@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(ContactMessage, pk=pk)
    contact.delete()
    messages.success(request, 'Message deleted successfully.')
    return redirect('contact:contact_list')
