import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import CommentForm, IssueForm, RenewBookForm
from .chart_data import *
from .models import Book, Author, BookInstance, Genre, Language, Comment, Issue


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits',0)
    request.session['num_visits'] = num_visits + 1
    num_genres=Genre.objects.count()

    keyword="星期二"
    num_books_with_keyword = Book.objects.filter(title__icontains=keyword).count()

    num_user = User.objects.count()

    user = request.user  # 確保這行代碼存在，從請求中獲取用戶
    last_login = "尚未登入"
    last_login2 = "尚未登入"
    
    if user.is_authenticated:
        last_login = user.last_login.isoformat()
        last_login2=user.last_login
        last_login2=datetime.datetime.strptime(last_login, "%Y-%m-%dT%H:%M:%S.%f%z")


    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
        'num_genres': num_genres,
        'num_books_with_keyword':num_books_with_keyword,
        'num_user': num_user,
        'chart_data':Doughnut(Book.objects.all()),
        'bar_data':Barchart(BookInstance.objects.all()),
        'last_login':last_login,
        'last_login2':last_login2,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'
    paginate_by = 5
    #queryset = Book.objects.filter(title__icontains='war')[:5]
    template_name = 'book_list.html'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        #context['some_data'] = 'This is just some data'
        return context
    
class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'book_detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        comments = Comment.objects.filter(book=book)
        context['comments'] = comments
        context['form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.book = self.object
            comment.user = request.user
            comment.save()
            return redirect('book-detail', pk=self.object.pk)
        context['form'] = form
        return self.render_to_response(context)
    
class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'author_list'
    template_name = 'author_list.html'

class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'author_detail.html'
    def get_context_data(self, **kwargs):
        # 获取基类的上下文数据
        context = super().get_context_data(**kwargs)
        
        # 获取作者的书籍
        author = self.get_object()
        books = Book.objects.filter(author=author)
        
        # 将书籍添加到上下文中
        context['books'] = books
        return context
    '''
    def book_detail_view(request, primary_key):
        author = author.objects.get(pk=primary_key)
        book=book.objects.get(pk=primary_key)
        return render(request, 'book_detail.html', context={'author': author,"book":book})'''
    

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
        
@login_required    
@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            #return HttpResponseRedirect(reverse('all-borrowed') )
            return HttpResponseRedirect(reverse('all_borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'book_renew_librarian.html', {'form': form, 'bookinst':book_inst})


class AuthorCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}
    template_name ='author_form.html'
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']
    template_name ='author_form.html'
    permission_required = 'catalog.can_mark_returned'

class AuthorDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    template_name ='author_confirm_delete.html'
    permission_required = 'catalog.can_mark_returned'

class BorrowListView(PermissionRequiredMixin,LoginRequiredMixin,generic.ListView):
    model = BookInstance
    template_name ='all_book_borrowed.html'
    permission_required = 'catalog.can_mark_returned'
    

class BookCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model = Book
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}
    template_name ='book_form.html'
    permission_required = 'catalog.can_mark_returned'

class BookUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    model = Book
    fields = '__all__'
    template_name ='book_form.html'
    permission_required = 'catalog.can_mark_returned'

class BookDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    template_name ='book_confirm_delete.html'
    permission_required = 'catalog.can_mark_returned'

def search_books(request):
    query = request.GET.get('query')
    if query:
        books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()
        query=""
    return render(request, 'search.html', {'books': books, 'query': query})

def report_issue(request):
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)  
            issue.user = request.user  
            issue.save()  
            return redirect('index')
    else:
        form = IssueForm()
    return render(request, 'Issue_report.html', {'form': form})

class IssueListView(PermissionRequiredMixin,LoginRequiredMixin,generic.ListView):
    model = Issue
    template_name ='Issue_list.html'
    permission_required = 'catalog.can_mark_returned'

def donate(request):
    return render(request, 'donate.html')