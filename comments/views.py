from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from articles.models import Comment, Article
from .forms import AdminReplyForm

# Only staff can access
def staff_required(user):
    return user.is_staff

@login_required
@user_passes_test(staff_required)
def new_comments_list(request):
    # Show only top-level comments with no reply yet
    new_comments = Comment.objects.filter(parent__isnull=True).exclude(replies__isnull=False).select_related('article', 'user')

    # Pagination (optional)
    from django.core.paginator import Paginator
    paginator = Paginator(new_comments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Admin reply handling
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)
        form = AdminReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.article = comment.article
            reply.parent = comment
            reply.user = request.user
            reply.name = request.user.username
            reply.email = request.user.email
            reply.save()
            messages.success(request, f"Replied to comment by {comment.name}.")
            return redirect('comments:new_comments_list')
    else:
        form = AdminReplyForm()

    context = {
        'comments': page_obj,
        'form': form,
    }
    return render(request, 'comments/new_comments_list.html', context)
