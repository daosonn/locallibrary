from django.shortcuts import render, get_object_or_404
from django.views import generic
from catalog import constants
from catalog.constants import LOAN_STATUS_LOOKUP
from catalog.models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin


def index(request):
    """View function for the home page of site."""
    
    # Generate counts of some of the main objects
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_instances_available = BookInstance.objects.filter(status=LOAN_STATUS_LOOKUP['available']).count()
    num_authors = Author.objects.count()
    
    # Visit count
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits + 1,
    }

    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model               = Book
    paginate_by         = constants.BOOK_LIST_VIEW_PAGINATE
    context_object_name = 'book_list'
    template_name       = 'catalog/book_list.html'


class BookDetailView(generic.DetailView):
    model         = Book
    template_name = 'catalog/book_detail.html'

    def get_context_data(self, **kwargs):
        """Bổ sung thêm danh sách copies và các label trạng thái"""
        context = super().get_context_data(**kwargs)
        book    = self.get_object()
        context['copies']          = book.bookinstance_set.all()
        context['STATUS_AVAILABLE']   = constants.STATUS_AVAILABLE
        context['STATUS_MAINTENANCE'] = constants.STATUS_MAINTENANCE
        context['status_labels']   = dict(constants.LOAN_STATUS)
        return context

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Liệt kê sách user hiện tại đang mượn."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'  
    paginate_by = constants.MY_BORROWED_PAGINATE_BY


    def get_queryset(self):
        return (BookInstance.objects
                .filter(borrower=self.request.user)                         
                .filter(status__exact=constants.STATUS_ON_LOAN)
                .order_by('due_back'))                                      