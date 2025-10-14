from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count
from articles.models import Article, Subscriber
from books.models import Book

User = get_user_model()

def report_dashboard(request):
    # Summary stats
    total_users = User.objects.count()
    total_articles = Article.objects.count()
    total_books = Book.objects.count()
    total_subscribers = Subscriber.objects.count()

    # Group users by role (adjust if 'role' is in profile)
    try:
        users_by_role = User.objects.values('role').annotate(count=Count('id'))
    except Exception:
        users_by_role = User.objects.values('profile__role').annotate(count=Count('id'))

    # Recent activity (adjust date field if needed)
    recent_articles = Article.objects.order_by('-date_posted')[:5]
    recent_books = Book.objects.order_by('-published_at')[:5]

    context = {
        'total_users': total_users,
        'total_articles': total_articles,
        'total_books': total_books,
        'total_subscribers': total_subscribers,
        'users_by_role': users_by_role,
        'recent_articles': recent_articles,
        'recent_books': recent_books,
    }
    return render(request, 'report/dashboard.html', context)
