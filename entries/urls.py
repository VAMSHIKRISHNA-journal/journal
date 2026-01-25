from django.urls import path
from . import views

urlpatterns = [
    # Rack (Books)
    path('', views.BookListView.as_view(), name='dashboard'),
    path('book/new/', views.BookCreateView.as_view(), name='book-create'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('book/<int:pk>/edit/', views.BookUpdateView.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),

    # Journals (Entries)
    path('book/<int:book_id>/new/', views.EntryCreateView.as_view(), name='entry-create'),
    path('entry/<int:pk>/edit/', views.EntryUpdateView.as_view(), name='entry-update'),
    path('entry/<int:pk>/delete/', views.EntryDeleteView.as_view(), name='entry-delete'),

    # Shared / Tracking
    path('shared/<uuid:token>/', views.SharedEntryView.as_view(), name='shared-entry'),
    path('shared/<uuid:token>/ping/', views.entry_read_ping, name='entry-read-ping'),

    path('settings/', views.ProfileUpdateView.as_view(), name='profile-settings'),
    path('signup/', views.signup, name='signup'),
]
