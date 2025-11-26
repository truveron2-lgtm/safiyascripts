from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Article, Comment
from .forms import ArticleForm, CommentForm


def article_list(request):
    search_query = request.GET.get('q', '')
    if search_query:
        articles = Article.objects.filter(
            Q(title__icontains=search_query) | Q(short_description__icontains=search_query)
        )
    else:
        articles = Article.objects.all()

    paginator = Paginator(articles, 10)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    context = {'articles': articles, 'search_query': search_query}
    return render(request, 'articles/article_list.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Article, Comment, Subscriber
from .forms import CommentForm

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comments = article.comments.filter(parent__isnull=True).select_related('user')
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            parent_id = request.POST.get('parent_id')
            parent_comment = Comment.objects.filter(id=parent_id).first() if parent_id else None

            # ✅ Create comment
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.parent = parent_comment

            # ✅ Only logged-in users can reply
            if parent_comment and not request.user.is_authenticated:
                messages.error(request, "You must be logged in to reply.")
                return redirect('articles:article_detail', pk=article.pk)

            # ✅ User handling
            if request.user.is_authenticated:
                comment.user = request.user
                comment.name = request.user.username
                comment.email = request.user.email
            else:
                if parent_comment:
                    messages.error(request, "Only logged-in users can reply to comments.")
                    return redirect('articles:article_detail', pk=article.pk)
                comment.name = request.POST.get('name')
                comment.email = request.POST.get('email')

            comment.save()

            # ✅ Optional subscription
            if request.POST.get('subscribe') and comment.email:
                Subscriber.objects.get_or_create(email=comment.email)
                messages.success(request, "Thanks for subscribing!")

            messages.success(request, 
                "Your reply has been posted." if parent_comment else "Your comment has been posted."
            )
            return redirect('articles:article_detail', pk=article.pk)

    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'articles/article_detail.html', context)


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ArticleForm
from .utils import generate_article_audio   # <-- ADD THIS


@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()

            # 🔊 Generate audio automatically
            try:
                generate_article_audio(article)
                messages.success(request, "Article created successfully, and audio generated.")
            except Exception as e:
                messages.warning(request, f"Article saved but audio could not be generated: {e}")

            return redirect('articles:article_detail', pk=article.pk)

    else:
        form = ArticleForm()

    return render(request, 'articles/article_form.html', {
        'form': form,
        'title': 'Create Article'
    })


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ArticleForm
from .models import Article
from .utils import generate_article_audio   # Make sure this exists


@login_required
def article_edit(request, pk):
    """Allow only the article author or admin to edit an article with audio generation."""
    article = get_object_or_404(Article, pk=pk)

    # Only the author or staff can edit
    if request.user != article.author and not request.user.is_staff:
        messages.error(request, "You do not have permission to edit this article.")
        return redirect('articles:article_detail', pk=article.pk)

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()

            # 🔊 Regenerate audio after edit
            try:
                generate_article_audio(article)
                messages.success(request, "Article updated successfully and audio regenerated.")
            except Exception as e:
                messages.warning(request, f"Article updated but audio could not be regenerated: {e}")

            return redirect('articles:article_detail', pk=article.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ArticleForm(instance=article)

    return render(request, 'articles/article_form.html', {
        'form': form,
        'title': 'Edit Article'
    })


@login_required
def article_delete(request, pk):
    """Allow only the article author or admin to delete."""
    article = get_object_or_404(Article, pk=pk)

    # Only the author or staff can delete
    if request.user != article.author and not request.user.is_staff:
        messages.error(request, "You do not have permission to delete this article.")
        return redirect('articles:article_detail', pk=article.pk)

    if request.method == 'POST':
        article.delete()
        messages.success(request, "Article deleted successfully.")
        return redirect('articles:article_list')

    return render(request, 'articles/article_confirm_delete.html', {'article': article})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.user:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You cannot delete this comment.")
    return redirect('articles:article_detail', pk=comment.article.pk)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Subscriber

@login_required
def subscribers_list(request):
    """Display list of newsletter subscribers (staff only)."""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('articles:article_list')

    subscribers = Subscriber.objects.all().order_by('-created_at')

    # Add pagination (20 per page)
    paginator = Paginator(subscribers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'articles/subscribers_list.html', {'subscribers': page_obj})


from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.utils.html import strip_tags
from .models import Article, Comment, Subscriber
from .forms import CommentForm

# -----------------------------
# Public Article List
# -----------------------------
def article_list_public(request):
    """Public-facing article list with search and pagination."""
    search_query = request.GET.get('q', '').strip()
    
    # Only show published articles
    articles = Article.objects.filter(is_published=True)
    
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) | Q(short_description__icontains=search_query)
        )

    # Pagination (6 articles per page)
    paginator = Paginator(articles.order_by('-date_posted'), 6)
    page_number = request.GET.get('page')
    articles_page = paginator.get_page(page_number)

    context = {
        'articles': articles_page,
        'search_query': search_query
    }
    return render(request, 'articles/article_list_public.html', context)


# -----------------------------
# Public Article Detail
# -----------------------------
def article_detail_public(request, pk):
    """Public-facing article detail with audio, comments, replies, and subscription check."""
    article = get_object_or_404(Article, pk=pk, is_published=True)
    comments = article.comments.filter(parent__isnull=True).select_related('user')
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            name = comment_form.cleaned_data.get('name', '').strip()
            email = comment_form.cleaned_data.get('email', '').strip()
            parent_id = request.POST.get('parent_id')

            # 🚫 Prevent impersonation
            forbidden_names = ['safiyascripts', 'safiyascript']
            if name.lower() in forbidden_names:
                messages.error(
                    request,
                    "Sorry, you cannot use the name 'SafiyaScripts' or any similar variation when posting a comment."
                )
                return redirect('articles:article_detail_public', pk=article.pk)

            # 💬 Handle replies
            parent_comment = None
            if parent_id:
                if not request.user.is_authenticated:
                    messages.error(
                        request,
                        "Only logged-in users can reply to comments. Please log in first."
                    )
                    return redirect('account:login')
                parent_comment = Comment.objects.filter(id=parent_id).first()
            # Top-level comment
            else:
                parent_comment = None

            # 📧 Subscription check for top-level comments
            if not parent_comment and not Subscriber.objects.filter(email=email).exists():
                subscribe_url = reverse('articles:subscribe')
                messages.warning(
                    request,
                    f"You must <a href='{subscribe_url}' class='alert-link text-danger'>subscribe here</a> before commenting."
                )
                return redirect('articles:article_detail_public', pk=article.pk)

            # 💾 Save comment
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.parent = parent_comment

            if request.user.is_authenticated:
                comment.user = request.user
                comment.name = request.user.username
                comment.email = request.user.email
            else:
                comment.name = strip_tags(name)
                comment.email = email

            comment.save()
            messages.success(request, "Your comment has been posted successfully.")
            return redirect('articles:article_detail_public', pk=article.pk)

    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'articles/article_detail_public.html', context)


# -----------------------------
# Optional: Article Audio Regeneration (Admin)
# -----------------------------
from django.contrib.auth.decorators import login_required
from .utils import generate_article_audio

@login_required
def regenerate_audio(request, pk):
    """Allow admin/staff to regenerate article audio."""
    article = get_object_or_404(Article, pk=pk)

    if not request.user.is_staff:
        messages.error(request, "You do not have permission to regenerate audio.")
        return redirect('articles:article_detail_public', pk=article.pk)

    try:
        audio_file = generate_article_audio(article)  # Should return a FileField-compatible object
        article.audio = audio_file
        article.save()
        messages.success(request, "Audio regenerated successfully.")
    except Exception as e:
        messages.error(request, f"Error generating audio: {e}")

    return redirect('articles:article_detail_public', pk=article.pk)
    
from .forms import SubscriptionForm

def subscribe(request):
    """Public subscription form for visitors."""
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subscriber, created = Subscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, "Thank you for subscribing!")
            else:
                messages.info(request, "You’re already subscribed.")
            return redirect('articles:article_list_public')
    else:
        form = SubscriptionForm()
    return render(request, 'articles/subscribe.html', {'form': form})

def article_summary_home(request):
    """Show the three most recent articles for the homepage."""
    recent_articles = Article.objects.all()[:3]
    context = {'recent_articles': recent_articles}
    return render(request, 'articles/article_summary_home.html', context)


@login_required
def admin_reply_comment(request, pk):
    """Allow admin to reply to a comment directly from the admin article detail view."""
    article = get_object_or_404(Article, pk=pk)

    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        content = request.POST.get('content', '').strip()

        if not parent_id or not content:
            messages.error(request, "Invalid reply. Please write something.")
            return redirect('articles:article_detail', pk=article.pk)

        parent_comment = Comment.objects.filter(id=parent_id).first()
        if not parent_comment:
            messages.error(request, "Parent comment not found.")
            return redirect('articles:article_detail', pk=article.pk)

        # ✅ Create reply comment
        Comment.objects.create(
            article=article,
            user=request.user,
            name=request.user.username,
            email=request.user.email,
            content=content,
            parent=parent_comment,
        )

        messages.success(request, "Reply posted successfully.")
        return redirect('articles:article_detail', pk=article.pk)

    return redirect('articles:article_detail', pk=article.pk)

