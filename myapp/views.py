from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, logout
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import BlogPost, Comment, Project
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
import logging
import json
from django.shortcuts import render, redirect
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib import messages
from .forms import ContactForm, CustomAuthenticationForm, CustomUserCreationForm

logger = logging.getLogger(__name__)


# Home page view
# views.py


def home(request):
    projects = Project.objects.all()[:3]
    posts = BlogPost.objects.all().order_by("-created_at")[:3]

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            subject = f"Yeni mesaj: {name} sizə yazdı!"
            message_body = f"Ad: {name}\nE-poçt: {email}\n\nMesaj:\n{message}"

            from_email = settings.EMAIL_HOST_USER  # Sənin Gmail hesabın
            recipient_list = ["astara635@gmail.com"]  # Sənin e-poçt ünvanın

            try:
                email_message = EmailMessage(
                    subject,
                    message_body,
                    from_email,
                    recipient_list,
                    headers={
                        "Reply-To": email
                    },  # Burada istifadəçinin emaili reply üçün qoyulur
                )
                email_message.send(fail_silently=False)
                return redirect(reverse("thank_you"))
            except Exception as e:
                print(f"E-poçt göndərmə xətası: {e}")

    else:
        form = ContactForm()

    context = {
        "projects": projects,
        "posts": posts,
        "form": form,
    }

    return render(request, "home.html", context)


def thank_you(request):
    return render(request, "thank_you.html")


# Blog list view
def blog_list(request):
    search_query = request.GET.get("search", "")
    if search_query:
        posts = BlogPost.objects.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        ).order_by("-created_at")
    else:
        posts = BlogPost.objects.all().order_by("-created_at")

    return render(request, "blog_list.html", {"posts": posts})


# Detail view of a specific blog post@ensure_csrf_cookie
def blog_detail(request, slug):
    post = BlogPost.objects.get(slug=slug)
    comments = post.comments.all().order_by(
        "-created_at"
    )  # Order comments by creation date (newest first)
    return render(request, "blog_detail.html", {"post": post, "comments": comments})


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, "Qeydiyyat uğurla tamamlandı. Daxil ola bilərsiniz!"
            )
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Uğurla daxil oldunuz!")
            next_url = request.GET.get(
                "next"
            )  # Check if 'next' is in the URL query string
            if not next_url:  # If there's no 'next' parameter, use the referer URL
                next_url = request.META.get(
                    "HTTP_REFERER", "/"
                )  # Default to homepage if no referer
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


@login_required
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
            return JsonResponse({"likes_count": post.total_likes(), "liked": liked})
        else:
            return JsonResponse({"error": "Authentication required"}, status=403)
    except Exception as e:
        logger.error(f"Error in like_post: {e}")
        return JsonResponse({"error": "An error occurred"}, status=400)


@require_POST
@login_required
def add_comment(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)

    # JSON və ya form-data qəbul et
    content = request.POST.get("content", "").strip()
    if not content:
        try:
            data = json.loads(request.body)
            content = data.get("content", "").strip()
        except json.JSONDecodeError:
            pass

    if content:
        comment = Comment.objects.create(
            post=post, author=request.user, content=content
        )

        # Burada AJAX sorğusunu birbaşa JSON cavabla qaytar
        if (
            request.headers.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
            or request.content_type == "application/json"
        ):
            return JsonResponse(
                {
                    "success": True,
                    "comment_id": comment.id,
                    "author": comment.author.username,
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat(),  # ISO format
                }
            )

    # Əgər AJAX deyilsə, normal olaraq səhifəyə yönləndir
    return redirect("blog_detail", slug=slug)


def logout_view(request):
    logout(request)
    messages.success(request, "Uğurla çıxış etdiniz.")
    return redirect("blog_list")


def profile_view(request):
    return render(request, "profile.html")


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        # Hesabın silinməsi
        user.delete()
        # Hesab silindikdən sonra istifadəçini çıxış etdiririk
        logout(request)
        return redirect("blog_list")  # 'home' URL-ə yönləndiririk
    return render(request, "confirm_delete.html")  # Silmə təsdiqi üçün ayrıca səhifə


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return redirect(project.get_github_url())


def project_list(request):
    projects = Project.objects.all()
    return render(request, "project_list.html", {"projects": projects})


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            # Send email
            send_mail(
                f"Message from {name} ({email})",  # Subject
                message,  # Message
                email,  # From email
                ["elnuraliyev.mail@gmail.com"],  # To email (your email)
                fail_silently=False,
            )

            # Redirect or show a success message
            return redirect("success")  # Redirect to a success page
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})


@login_required
def password_change(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(
                request, user
            )  # İstifadəçinin sessiyasını yenilə ki, çıxmasın
            messages.success(
                request, "Şifrə uğurla dəyişdirildi. Zəhmət olmasa yenidən daxil olun."
            )
            return redirect("login")  # Login səhifəsinə yönləndir
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "registration/password_change.html", {"form": form})


@login_required
def password_change_done(request):
    return render(request, "registration/password_change_done.html")


@csrf_exempt  # Optional: If CSRF token doesn't work with AJAX request
def edit_comment(request, comment_id):
    if request.method == "POST":
        # Load the JSON data from the request body
        data = json.loads(request.body)
        new_content = data.get("content", None)

        if new_content:
            comment = Comment.objects.get(id=comment_id)
            if request.user == comment.author:
                # Update the comment's content
                comment.content = new_content
                comment.save()
                return JsonResponse(
                    {
                        "success": True,
                        "new_content": comment.content,
                    }
                )
            return JsonResponse(
                {"error": "You do not have permission to edit this comment."},
                status=403,
            )
        else:
            return JsonResponse({"error": "Content is required."}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=400)


# Delete comment view
def delete_comment(request, comment_id):
    if request.method == "POST":
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.author:
            comment.delete()
            return JsonResponse({"success": True})
        return JsonResponse(
            {"error": "You do not have permission to delete this comment."}, status=403
        )
    return JsonResponse({"error": "Invalid request."}, status=400)
