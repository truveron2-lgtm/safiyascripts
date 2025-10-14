from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Visitor, PageView
from django.db.models import Count

@staff_member_required
def stats_dashboard(request):
    total_visitors = Visitor.objects.count()
    total_page_views = PageView.objects.count()
    
    # Visitors by country
    visitors_by_country = Visitor.objects.values('country').annotate(count=Count('id')).order_by('-count')
    
    # Most visited pages
    most_visited_pages = PageView.objects.values('page_name').annotate(count=Count('id')).order_by('-count')[:10]

    context = {
        'total_visitors': total_visitors,
        'total_page_views': total_page_views,
        'visitors_by_country': visitors_by_country,
        'most_visited_pages': most_visited_pages,
    }
    return render(request, 'stats/dashboard.html', context)
