from django.shortcuts import render
from articles.models import Article  # ✅ Import your Article model

def index(request):
    # Fetch the 3 most recent published articles
    recent_articles = Article.objects.all()[:3]

    # Pass them to your homepage template
    return render(request, 'blog/index.html', {'recent_articles': recent_articles})
