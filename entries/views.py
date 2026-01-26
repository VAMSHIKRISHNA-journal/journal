from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from .forms import CustomSignupForm
from django.contrib.auth import login
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse
from twilio.rest import Client
from .models import Book, Entry, Profile, ReadEvent

# --- BOOK VIEWS (The Rack) ---

class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'entries/book_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)

class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    template_name = 'entries/book_form.html'
    fields = ['title', 'description', 'cover_color']
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    template_name = 'entries/book_form.html'
    fields = ['title', 'description', 'cover_color']
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)

class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = 'entries/book_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)

# --- ENTRY VIEWS (Inside Books) ---

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'entries/book_detail.html'
    context_object_name = 'book'

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)

class EntryCreateView(LoginRequiredMixin, CreateView):
    model = Entry
    template_name = 'entries/entry_form.html'
    fields = ['title', 'content']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = get_object_or_404(Book, id=self.kwargs.get('book_id'), user=self.request.user)
        return context

    def form_valid(self, form):
        print("DEBUG: form_valid triggered! User is:", self.request.user.username)
        book = get_object_or_404(Book, id=self.kwargs.get('book_id'), user=self.request.user)
        form.instance.book = book
        form.instance.user = self.request.user
        # Save the instance first so we have the ID and tokens
        self.object = form.save()
        
        profile = self.request.user.profile
        
        # Generate absolute URL for sharing
        share_url = self.request.build_absolute_uri(
            reverse('shared-entry', kwargs={'token': self.object.share_token})
        )
        
        email_sent = False
        sms_sent = False

        # 1. Send SMS Notification
        if profile.notify_phone and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                message = client.messages.create(
                    body=f"📖 New Journal Entry! \nTitle: {self.object.title}\nRead here: {share_url}",
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=profile.notify_phone
                )
                sms_sent = True
            except Exception as e:
                print(f"SMS Notification failed: {e}")
        elif profile.notify_phone:
            print("SMS Notification skipped: Twilio credentials not configured.")

        # 2. Send Email Notification
        print(f"DEBUG: Checking profile notification email: {profile.notify_email}")
        if profile.notify_email:
            print("DEBUG: Profile email found. Attempting to send...")
            try:
                subject = f"📖 New Journal Entry: {self.object.title}"
                message_content = f"Hey,\n\n{self.request.user.username} just published a new entry in their 'Living Rack' library.\n\nRead it here: {share_url}"
                
                from_display = f'"{self.request.user.username} via The Living Rack" <{settings.EMAIL_HOST_USER}>'
                
                # Only add Reply-To if the user has an email set
                reply_to_list = [self.request.user.email] if self.request.user.email else None
                
                email = EmailMessage(
                    subject=subject,
                    body=message_content,
                    from_email=from_display,
                    to=[profile.notify_email],
                    reply_to=reply_to_list
                )
                print(f"DEBUG: Attempting to send to {profile.notify_email} with reply_to {reply_to_list}")
                num_sent = email.send(fail_silently=True)
                print(f"DEBUG: Email dispatch attempted. Status: {num_sent}")
                
                if num_sent:
                    email_sent = True
                    messages.success(self.request, f"Notification sent successfully to {profile.notify_email}!")
                else:
                    messages.warning(self.request, f"Email notification to {profile.notify_email} might have failed. Please check your settings.")
            except Exception as e:
                messages.error(self.request, f"Failed to send email notification: {str(e)}")
                print(f"Email Notification failed: {e}")
            
        if not profile.notify_email and not profile.notify_phone:
            messages.info(self.request, "Entry saved. No notification recipients configured in Settings.")

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.kwargs.get('book_id')})

class EntryUpdateView(LoginRequiredMixin, UpdateView):
    model = Entry
    template_name = 'entries/entry_form.html'
    fields = ['title', 'content']

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.object.book
        return context

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.book.id})

class EntryDeleteView(LoginRequiredMixin, DeleteView):
    model = Entry
    template_name = 'entries/entry_confirm_delete.html'

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.object.book
        return context

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.book.id})

# --- TRACKING & PUBLIC VIEWS ---

class SharedEntryView(DetailView):
    model = Entry
    template_name = 'entries/shared_entry.html'
    context_object_name = 'entry'

    def get_object(self, queryset=None):
        return get_object_or_404(Entry, share_token=self.kwargs.get('token'))

def entry_read_ping(request, token):
    if request.method == 'POST':
        entry = get_object_or_404(Entry, share_token=token)
        duration = int(request.POST.get('duration', 0))
        
        event, created = ReadEvent.objects.get_or_create(
            entry=entry, 
            is_notified=False,
            defaults={'duration_seconds': duration}
        )
        if not created:
            event.duration_seconds += duration
        
        event.save()

        # If they've read for more than 10 seconds and we haven't notified yet, send the "Read" alert
        if event.duration_seconds > 10 and not event.is_notified:
            event.is_notified = True
            event.save()
            
            author = entry.user
            # Notify Author via Email/SMS
            msg = f"✨ Someone just read your journal '{entry.title}' for {event.duration_seconds} seconds!"
            
            # Send Email to Author
            if author.email:
                from_display = f'"The Living Rack Alerts" <{settings.EMAIL_HOST_USER}>'
                email = EmailMessage(
                    subject="✨ Journal Read Alert!",
                    body=msg,
                    from_email=from_display,
                    to=[author.email],
                )
                email.send(fail_silently=True)
            
            # Send SMS to Author (if settings configured)
            if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
                # Priority: author's notify_phone, then fall back to global notification number
                target_phone = author.profile.notify_phone or settings.NOTIFICATION_PHONE_NUMBER
                if target_phone:
                    try:
                        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                        client.messages.create(
                            body=msg,
                            from_=settings.TWILIO_PHONE_NUMBER,
                            to=target_phone
                        )
                    except Exception as e:
                        print(f"Ping SMS failed: {e}")

        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'invalid'}, status=400)

# --- PROFILE / SETTINGS ---

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'entries/settings.html'
    fields = ['notify_email', 'notify_phone']
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        return self.request.user.profile

# --- AUTH ---

def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomSignupForm()
    return render(request, 'registration/signup.html', {'form': form})
