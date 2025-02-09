from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import BlogPost, Comment, Project
from django.db.models import Q
import json
import logging
from django.shortcuts import render, redirect
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from .forms import ContactForm
logger = logging.getLogger(__name__)


# Home page view
# views.py

def home(request):
    projects = Project.objects.all()[:3]
    posts = BlogPost.objects.all().order_by('-created_at')[:3]

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            subject = f"Yeni mesaj: {name} sizə yazdı!"
            message_body = f"Ad: {name}\nE-poçt: {email}\n\nMesaj:\n{message}"

            from_email = settings.EMAIL_HOST_USER  # Sənin Gmail hesabın
            recipient_list = ['astara635@gmail.com']  # Sənin e-poçt ünvanın

            try:
                email_message = EmailMessage(
                    subject,
                    message_body,
                    from_email,
                    recipient_list,
                    headers={'Reply-To': email}  # Burada istifadəçinin emaili reply üçün qoyulur
                )
                email_message.send(fail_silently=False)
                return redirect(reverse('thank_you'))  
            except Exception as e:
                print(f"E-poçt göndərmə xətası: {e}")

    else:
        form = ContactForm()

    context = {
        'projects': projects,
        'posts': posts,
        'form': form,
    }

    return render(request, 'home.html', context)


def thank_you(request):
    return render(request, 'thank_you.html')


# Blog list view
def blog_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        posts = BlogPost.objects.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        ).order_by('-created_at')
    else:
        posts = BlogPost.objects.all().order_by('-created_at')

    return render(request, 'blog_list.html', {'posts': posts})


# Detail view of a specific blog post
@ensure_csrf_cookie
def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'blog_detail.html', {'post': post})


# Like a blog post
@require_POST
def like_post(request, slug):
    try:
        post = get_object_or_404(BlogPost, slug=slug)
        if request.user.is_authenticated:
            if post.is_liked_by_user(request.user):
                post.likes.remove(request.user)
                liked = False
            else:
                post.likes.add(request.user)
                liked = True
            return JsonResponse({'likes_count': post.total_likes(), 'liked': liked})
        else:
            return JsonResponse({'error': 'Authentication required'}, status=403)
    except Exception as e:
        logger.error(f"Error in like_post: {e}")
        return JsonResponse({'error': 'An error occurred'}, status=400)

# Add a comment to a blog post
@require_POST
def add_comment(request, slug):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required', 'requires_auth': True}, status=403)

    try:
        post = get_object_or_404(BlogPost, slug=slug)
        data = json.loads(request.body)
        content = data.get('content', '').strip()

        if not content:
            return JsonResponse({'error': 'Comment content cannot be empty'}, status=400)

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )

        return JsonResponse({
            'success': True,
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%B %d, %Y %H:%M')
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in add_comment: {e}")
        return JsonResponse({'error': 'An error occurred'}, status=400)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return redirect(project.get_github_url())


def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Send email
            send_mail(
                f'Message from {name} ({email})',  # Subject
                message,  # Message
                email,  # From email
                ['elnuraliyev.mail@gmail.com'],  # To email (your email)
                fail_silently=False,
            )

            # Redirect or show a success message
            return redirect('success')  # Redirect to a success page
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})
