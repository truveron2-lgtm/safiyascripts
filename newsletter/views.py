from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

from .models import Newsletter, NewsletterSection
from .forms import NewsletterForm, NewsletterSectionForm
from articles.models import Subscriber
from .utils import generate_unsubscribe_url

import threading
import time

# Thread-safe progress data
SEND_LOCK = threading.Lock()
SEND_PROGRESS = {}   # map newsletter_id -> progress (0-100)
SEND_RUNNING = {}    # map newsletter_id -> bool (is sending)

from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
import os, mimetypes, time

def _send_newsletter_job(newsletter_id):
    """Send newsletter with inline images and update SEND_PROGRESS."""
    newsletter = Newsletter.objects.filter(id=newsletter_id).first()
    if not newsletter:
        return

    # Only send to active subscribers
    subscribers = list(Subscriber.objects.filter(is_active=True))
    total = len(subscribers)
    if total == 0:
        with SEND_LOCK:
            SEND_PROGRESS[newsletter_id] = 100
            SEND_RUNNING[newsletter_id] = False
        return

    with SEND_LOCK:
        SEND_PROGRESS[newsletter_id] = 0
        SEND_RUNNING[newsletter_id] = True

    # SMTP connection
    connection = get_connection(
        host='smtp.hostinger.com',
        port=465,
        username='info@safiyascripts.com',
        password='Safiya2025@',
        use_ssl=True
    )

    for i, sub in enumerate(subscribers, start=1):
        try:
            html_content = render_to_string('newsletter/newsletter_email.html', {
                'newsletter': newsletter,
                'subscriber': sub,
                'unsubscribe_url': generate_unsubscribe_url(sub, request=None)
            })
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=f"{newsletter.title} - Volume {newsletter.volume} ({newsletter.month})",
                body=text_content,
                from_email='SafiyaScripts <info@safiyascripts.com>',
                to=[sub.email],
                connection=connection
            )
            email.attach_alternative(html_content, "text/html")

            # Attach inline images
            for section in newsletter.sections.all():
                if section.image:
                    image_path = section.image.path
                    if os.path.exists(image_path):
                        mime_type, _ = mimetypes.guess_type(image_path)
                        if not mime_type:
                            mime_type = "image/jpeg"
                        with open(image_path, "rb") as f:
                            img = MIMEImage(f.read(), _subtype=mime_type.split("/")[-1])
                        cid = f"img_{section.id}"
                        img.add_header("Content-ID", f"<{cid}>")
                        img.add_header("Content-Disposition", "inline", filename=os.path.basename(image_path))
                        email.attach(img)

            email.send(fail_silently=False)

        except Exception as e:
            print(f"Error sending to {sub.email}: {e}")

        # Update progress
        with SEND_LOCK:
            SEND_PROGRESS[newsletter_id] = int((i / total) * 100)

        time.sleep(0.1)

    with SEND_LOCK:
        SEND_PROGRESS[newsletter_id] = 100
        SEND_RUNNING[newsletter_id] = False

# ---------------------------
# 1. CREATE NEWSLETTER
# ---------------------------
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import NewsletterForm
from .models import Newsletter

@login_required
def create_newsletter(request):
    """
    Handles create + preview.
    - If user clicks 'Preview' we render the template with preview_html (not saved).
    - If user clicks 'Save' we persist and redirect.
    """
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            # If user pressed the preview button (name="preview")
            if 'preview' in request.POST:
                # get the HTML entered and send to template for preview
                preview_html = form.cleaned_data.get('main_content', '')
                # also keep other fields to show in preview
                preview_title = form.cleaned_data.get('title', '')
                preview_volume = form.cleaned_data.get('volume', '')
                return render(request, 'newsletter/create_newsletter.html', {
                    'form': form,
                    'preview_html': preview_html,
                    'preview_title': preview_title,
                    'preview_volume': preview_volume,
                })
            # Otherwise save and continue (existing behavior)
            newsletter = form.save(commit=False)
            newsletter.created_by = request.user
            newsletter.save()
            messages.success(request, "Newsletter created! Now add sections.")
            return redirect('newsletter:add_sections', newsletter_id=newsletter.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = NewsletterForm()

    return render(request, 'newsletter/create_newsletter.html', {'form': form})


# ---------------------------
# 2. ADD SECTIONS
# ---------------------------
@login_required
def add_sections(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if request.method == "POST":
        form = NewsletterSectionForm(request.POST, request.FILES)
        if form.is_valid():
            section = form.save(commit=False)
            section.newsletter = newsletter
            section.save()
            messages.success(request, "Section added successfully.")
            return redirect('newsletter:add_sections', newsletter_id=newsletter.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = NewsletterSectionForm()

    sections = newsletter.sections.all()

    return render(request, 'newsletter/add_sections.html', {
        'newsletter': newsletter,
        'form': form,
        'sections': sections
    })


# ---------------------------
# 3. PREVIEW NEWSLETTER
# ---------------------------
@login_required
def preview_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    sections = newsletter.sections.all()
    return render(request, 'newsletter/preview_newsletter.html', {
        'newsletter': newsletter,
        'sections': sections
    })


# ---------------------------
# 4. SEND NEWSLETTER (render progress page)
# ---------------------------
@login_required
def send_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    with SEND_LOCK:
        if newsletter_id not in SEND_PROGRESS:
            SEND_PROGRESS[newsletter_id] = 0
        if newsletter_id not in SEND_RUNNING:
            SEND_RUNNING[newsletter_id] = False

    return render(request, "newsletter/send_newsletter.html", {
        "newsletter": newsletter,
        "total": Subscriber.objects.count()
    })


# ---------------------------
# 5. START BACKGROUND SEND (AJAX POST)
# ---------------------------
@login_required
def start_send_background(request, newsletter_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    with SEND_LOCK:
        running = SEND_RUNNING.get(newsletter_id, False)
        if running:
            return JsonResponse({"status": "already_running"})

        SEND_RUNNING[newsletter_id] = True
        SEND_PROGRESS[newsletter_id] = 0

    thread = threading.Thread(target=_send_newsletter_job, args=(newsletter_id,), daemon=True)
    thread.start()

    return JsonResponse({"status": "started"})


# ---------------------------
# 6. PROGRESS POLL
# ---------------------------
@login_required
def sending_progress(request, newsletter_id):
    with SEND_LOCK:
        progress = SEND_PROGRESS.get(newsletter_id, 0)
        running = SEND_RUNNING.get(newsletter_id, False)
    return JsonResponse({"progress": progress, "running": running})


# ---------------------------
# 7. SENT CONFIRMATION PAGE
# ---------------------------
@login_required
def sent_confirmation(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    return render(request, 'newsletter/send_finished.html', {'newsletter': newsletter})


# newsletter/views.py
# newsletter/views.py
from django.shortcuts import render, get_object_or_404
from articles.models import Subscriber
from .utils import verify_unsubscribe_token

def unsubscribe_newsletter(request, uidb64):
    """
    Unsubscribe a subscriber after confirming.
    - GET: show confirmation page
    - POST: mark subscriber as inactive
    """
    subscriber_id = verify_unsubscribe_token(uidb64)
    subscriber = None
    confirmed = False  # tracks if user has confirmed

    if subscriber_id:
        subscriber = get_object_or_404(Subscriber, id=subscriber_id)
        
        if request.method == "POST":
            # User confirmed unsubscription
            subscriber.is_active = False
            subscriber.save()
            confirmed = True

    return render(request, 'newsletter/unsubscribe_confirmation.html', {
        'subscriber': subscriber,
        'confirmed': confirmed
    })
