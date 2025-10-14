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


from .models import Article, Comment, Subscriber

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comments = article.comments.filter(parent__isnull=True).select_related('user')
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            parent_id = request.POST.get('parent_id')
            parent_comment = Comment.objects.filter(id=parent_id).first() if parent_id else None

            # ✅ Create comment object
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.parent = parent_comment

            # ✅ Allow only logged-in users to reply
            if parent_comment and not request.user.is_authenticated:
                messages.error(request, "You must be logged in to reply to a comment.")
                return redirect('articles:article_detail', pk=article.pk)

            # ✅ Logged-in user info
            if request.user.is_authenticated:
                comment.user = request.user
                comment.name = request.user.username
                comment.email = request.user.email
            else:
                # Non-logged visitors can only post top-level comments
                if parent_comment:
                    messages.error(request, "Only logged-in users can reply to comments.")
                    return redirect('articles:article_detail', pk=article.pk)
                comment.name = request.POST.get('name')
                comment.email = request.POST.get('email')

            comment.save()

            # ✅ Optional subscription
            if request.POST.get('subscribe') and comment.email:
                Subscriber.objects.get_or_create(email=comment.email)
                messages.success(request, "Thank you for subscribing to our newsletter!")

            messages.success(
                request,
                "Your reply has been posted." if parent_comment else "Your comment has been posted."
            )
            return redirect('articles:article_detail', pk=article.pk)

    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'articles/article_detail.html', context)


@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('articles:article_detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'articles/article_form.html', {'form': form, 'title': 'Create Article'})


@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk, author=request.user)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('articles:article_detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'articles/article_form.html', {'form': form, 'title': 'Edit Article'})


@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk, author=request.user)
    if request.method == 'POST':
        article.delete()
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
from .models import Article, Comment, Subscriber
from .forms import CommentForm


def article_list_public(request):
    """Public-facing article list."""
    search_query = request.GET.get('q', '')
    if search_query:
        articles = Article.objects.filter(
            Q(title__icontains=search_query) | Q(short_description__icontains=search_query)
        )
    else:
        articles = Article.objects.all()

    paginator = Paginator(articles, 6)  # show 6 per page
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    return render(request, 'articles/article_list_public.html', {
        'articles': articles,
        'search_query': search_query
    })


from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from django.utils.html import strip_tags
from .models import Article, Comment, Subscriber
from .forms import CommentForm


def article_detail_public(request, pk):
    """Public-facing article detail and comment submission."""
    article = get_object_or_404(Article, pk=pk)
    comments = article.comments.filter(parent__isnull=True).select_related('user')
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            name = comment_form.cleaned_data.get('name', '').strip()
            email = comment_form.cleaned_data.get('email', '').strip()
            parent_id = request.POST.get('parent_id')

            # 🚫 Block impersonation of "SafiyaScripts" or similar
            forbidden_names = ['safiyascripts', 'safiyascript']
            if name.lower() in forbidden_names:
                messages.error(
                    request,
                    "Sorry, you cannot use the name 'SafiyaScripts' or any similar variation when posting a comment."
                )
                return redirect('articles:article_detail_public', pk=article.pk)

            # 💬 Handle replies (only logged-in users can reply)
            if parent_id:
                if not request.user.is_authenticated:
                    messages.error(
                        request,
                        "Only logged-in users can reply to comments. Please log in to continue."
                    )
                    return redirect('account:login')
                parent_comment = Comment.objects.filter(id=parent_id).first()
            else:
                parent_comment = None

            # 📧 Check subscription (only for top-level comments)
            if not parent_id and not Subscriber.objects.filter(email=email).exists():
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

            # Auto-fill for logged-in users
            if request.user.is_authenticated:
                comment.name = request.user.username
                comment.email = request.user.email
                comment.user = request.user
            else:
                comment.name = strip_tags(name)
                comment.email = email

            comment.save()
            messages.success(request, "Your comment has been posted successfully.")
            return redirect('articles:article_detail_public', pk=article.pk)

    return render(request, 'articles/article_detail_public.html', {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
    })
    
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
