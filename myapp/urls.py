from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Ana səhifə
    path("", views.home, name="home"),
    # Təşəkkür səhifəsi
    path("thank-you/", views.thank_you, name="thank_you"),
    # Blog səhifəsi
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("blog/<slug:slug>/like/", views.like_post, name="like_post"),
    path("blog/<slug:slug>/comment/", views.add_comment, name="add_comment"),
    # Layihələr səhifəsi
    path("projects/", views.project_list, name="project_list"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("accounts/signup/", views.signup, name="signup"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", views.logout_view, name="logout"),
    path("accounts/profile/", views.profile_view, name="profile"),
    path("password/change/", views.password_change, name="password_change"),
    path("password/change/done/", views.password_change_done, name="password_change_done"),
    path("delete_account/", views.delete_account, name="delete_account"),
    path("edit_comment/<int:comment_id>/", views.edit_comment, name="edit_comment"),
    path("delete_comment/<int:comment_id>/", views.delete_comment, name="delete_comment"),
]
