from django.contrib import admin
from .models import Author, Genre, Book, BookInstance,Language,Comment,Issue



admin.site.register(Genre)
admin.site.register(Language)

class BooksInline(admin.TabularInline):
    model = Book
    extra = 1

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = [('first_name', 'last_name'), ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]





@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', "borrower",'imprint', 'due_back', 'status','id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back',"borrower")
        }),
    )

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre','language')
    inlines = [BooksInstanceInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display =('book', 'comment_text', 'created_at','user')

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display =('title', 'text', 'created_at','user')

