from django.shortcuts import render, redirect, get_object_or_404
from .models import Book
from .forms import BookForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

def book_list(request):
    books = Book.objects.all().order_by('-published_at')
    return render(request, 'books/book_list.html', {'books': books})

@never_cache
@login_required
def book_table_list(request):
    """Show book table with edit and delete options for logged-in users."""
    books = Book.objects.all().order_by('-published_at')
    return render(request, 'books/add_book.html', {
        'form': BookForm(),
        'books': books,
    })

@never_cache
@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('book_table_list')
    else:
        form = BookForm()
    books = Book.objects.all().order_by('-published_at')
    return render(request, 'books/add_book.html', {'form': form, 'books': books})

@login_required
def edit_book(request, pk):
    """Allow editing a book."""
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, request.FILES or None, instance=book)
    if form.is_valid():
        form.save()
        return redirect('book_table_list')
    books = Book.objects.all().order_by('-published_at')
    return render(request, 'books/add_book.html', {'form': form, 'books': books, 'edit_mode': True, 'book': book})

@login_required
def delete_book(request, pk):
    """Allow deletion of a book."""
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect('book_table_list')
