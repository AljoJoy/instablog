from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("register/", views.register_view, name="register_view"),
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("forgot_password/", views.forgot_password_view, name="forgot_password_view"),
    path("update_profile/", views.update_profile_view, name="update_profile_view"),
    path("userfeed/", views.userfeed_view, name="userfeed_view"),
    path("create_new_blog/", views.create_new_blog, name="create_new_blog"),
    path("my_blogs/", views.view_my_blogs, name="view_my_blogs"),
    path("my_blog_view/<int:pk>", views.my_blog_view, name="my_blog_view"),
    path("my_blog_edit/<int:pk>", views.my_blog_edit, name="my_blog_edit"),
    path("my_blog_delete/<int:pk>", views.my_blog_delete, name="my_blog_delete"),
    path("add_comment/<int:blog_id>", views.add_comment, name="add_comment"),
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/manage_users/", views.manage_users, name="manage_users"),
    path("admin/manage_blogs/", views.manage_blogs, name="manage_blogs"),
]