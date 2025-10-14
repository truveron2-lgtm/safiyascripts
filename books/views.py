from django.shortcuts import render, redirect
from .models import Book
from .forms import BookForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

def book_list(request):
    books = Book.objects.all().order_by('-published_at')
    return render(request, 'books/book_list.html', {'books': books})
@never_cache
@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {'form': form})
