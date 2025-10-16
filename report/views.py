from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from articles.models import Article, Subscriber
from books.models import Book
from stats.models import Visitor
from account.models import Profile

User = get_user_model()

def report_dashboard(request):
    # Get selected filter (default to all)
    filter_type = request.GET.get('filter', 'all').lower()

    # Base counts
    total_users = User.objects.count()
    total_articles = Article.objects.count()
    total_books = Book.objects.count()
    total_subscribers = Subscriber.objects.count()
    total_visitors = Visitor.objects.count()

    # Annotate visitors with page view count
    visitors = Visitor.objects.annotate(views_count=Count('page_views')).order_by('-created_at')
    total_views = visitors.aggregate(total=Sum('views_count'))['total'] or 0

    # Other data
    users = User.objects.all()
    subscribers = Subscriber.objects.all()
    articles = Article.objects.order_by('-date_posted')
    books = Book.objects.order_by('-published_at')

    # Prepare context data per filter
    if filter_type == 'users':
        context_data = {
            'title': 'Users',
            'headers': ['Username', 'Email', 'Date Joined'],
            'rows': [[u.username, u.email, u.date_joined.strftime('%b %d, %Y')] for u in users],
        }

    elif filter_type == 'articles':
        context_data = {
            'title': 'Articles',
            'headers': ['Title', 'Author', 'Date Posted'],
            'rows': [[a.title, str(a.author), a.date_posted.strftime('%b %d, %Y')] for a in articles[:10]],
        }

    elif filter_type == 'books':
        context_data = {
            'title': 'Books',
            'headers': ['Title', 'Published At'],
            'rows': [[b.title, b.published_at.strftime('%b %d, %Y')] for b in books[:10]],
        }

    elif filter_type == 'subscribers':
        context_data = {
            'title': 'Subscribers',
            'headers': ['Email', 'Date Subscribed'],
            'rows': [[s.email, s.created_at.strftime('%b %d, %Y')] for s in subscribers],
        }

    elif filter_type == 'visitors':
        context_data = {
            'title': 'Visitors',
            'headers': ['IP Address', 'Country', 'Views', 'Date'],
            'rows': [[v.ip_address, v.country or 'Unknown', v.views_count, v.created_at.strftime('%b %d, %Y')] for v in visitors],
            'total_views': total_views,
        }

    else:
        # Overview summary
        context_data = {
            'title': 'Overview',
            'headers': ['Category', 'Total'],
            'rows': [
                ['Users', total_users],
                ['Articles', total_articles],
                ['Books', total_books],
                ['Subscribers', total_subscribers],
                ['Visitors', total_visitors],
                ['Total Views', total_views],
            ],
        }

    # Chart data
    if filter_type == 'all':
        chart_labels = ['Users', 'Articles', 'Books', 'Subscribers', 'Visitors']
        chart_data = [total_users, total_articles, total_books, total_subscribers, total_views]
    elif filter_type == 'users':
        chart_labels, chart_data = ['Users'], [total_users]
    elif filter_type == 'articles':
        chart_labels, chart_data = ['Articles'], [total_articles]
    elif filter_type == 'books':
        chart_labels, chart_data = ['Books'], [total_books]
    elif filter_type == 'subscribers':
        chart_labels, chart_data = ['Subscribers'], [total_subscribers]
    elif filter_type == 'visitors':
        chart_labels, chart_data = ['Visitors'], [total_views]
    else:
        chart_labels, chart_data = [], []

    context = {
        'filter_type': filter_type,
        'total_users': total_users,
        'total_articles': total_articles,
        'total_books': total_books,
        'total_subscribers': total_subscribers,
        'total_visitors': total_visitors,
        'total_views': total_views,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'context_data': context_data,
        'articles': articles[:10],
        'books': books[:10],
        'visitors': visitors[:10],
    }

    return render(request, 'report/dashboard.html', context)
