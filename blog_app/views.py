from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import User, Blog, Comment
from .forms import EditBlogForm, LoginForm, RegistrationForm, UpdateProfileForm, CreateBlogForm

def index(request):
    return render(request,"index.html")

def register_view(request):
    form = RegistrationForm()

    if request.method == "POST":
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            if password != confirm_password:
                return render(request, "auth/register.html", {"form": form, "error": "Passwords do not match"})

            form.save()
            return redirect("login_view")

    return render(request, "auth/register.html", {"form": form})

def login_view(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = User.objects.filter(username=username, password=password).first()
            if user:
                request.session["is_logged_in"] = True
                request.session["username"] = username
                request.session["user_id"] = user.id
                request.session["profile_pic_url"] = user.profile_pic.url if user.profile_pic else ""
                request.session["is_admin"] = user.is_admin
                if user.is_admin:
                    return redirect("admin_dashboard")
                return redirect("userfeed_view")

            return render(request, "auth/login.html", {"form": form, "error": "Invalid username or password"})

    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    request.session.flush()
    return redirect("login_view")

def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        entered_otp = request.POST.get("otp")
        expected_otp = "1234"
        user_exists = User.objects.filter(email=email).exists()
        if not user_exists:
            return render(request, "auth/forgot_password.html", {"error": "User does not exist"})
        if entered_otp != expected_otp:
            return render(request, "auth/forgot_password.html", {"error": "Invalid OTP"})
        request.session['email'] = email    
        return render(request, "auth/new_password.html")        
    return render(request, "auth/forgot_password.html")

def new_password_view(request):
    if request.method == "POST":
        email = request.session.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if password != confirm_password:
            return render(request, "auth/new_password.html", {"error": "Passwords do not match"})   
        user = User.objects.get(email=email)
        user.password = password
        user.save()
        return redirect("login_view")
    return render(request, "auth/new_password.html")
    
def update_profile_view(request):
    if not request.session.get("is_logged_in"):
        return redirect("login_view")

    user_id = request.session.get("user_id")
    user = User.objects.filter(id=user_id).first()
    if not user:
        request.session.flush()
        return redirect("login_view")

    form = UpdateProfileForm(instance=user)
    if request.method == "POST":
        form = UpdateProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            request.session["profile_pic_url"] = user.profile_pic.url if user.profile_pic else ""
            return redirect("index")

    return render(request, "auth/update_profile.html", {"form": form, "user": user})
    
def userfeed_view(request):    
    if not request.session.get("is_logged_in"):
        return redirect("login_view")

    user_id = request.session.get("user_id")
    user = User.objects.filter(id=user_id).first()
    if not user:
        request.session.flush()
        return redirect("login_view")

    q = (request.GET.get("q") or "").strip()

    other_blogs = (
        Blog.objects.select_related("author")
        .prefetch_related("comment_set__author")
        .exclude(author=user)
        .order_by("-created_at")
    )

    if q:
        other_blogs = other_blogs.filter(title__icontains=q)

    paginator = Paginator(other_blogs, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "feed/userfeed.html", {"page_obj": page_obj, "other_blogs": page_obj, "q": q})

def add_comment(request, blog_id):
    if not request.session.get("is_logged_in"):
        return redirect("login_view")

    if request.method != "POST":
        return redirect("userfeed_view")

    user_id = request.session.get("user_id")
    user = User.objects.filter(id=user_id).first()
    if not user:
        request.session.flush()
        return redirect("login_view")

    blog = Blog.objects.filter(id=blog_id).first()
    if not blog:
        return redirect("userfeed_view")

    comment_text = (request.POST.get("comment_text") or "").strip()
    if comment_text:
        Comment.objects.create(comment_text=comment_text, author=user, blog=blog)

    return redirect("userfeed_view")

def create_new_blog(request):
    if not request.session.get("is_logged_in"):
        return redirect("login_view")

    user_id = request.session.get("user_id")
    user = User.objects.filter(id=user_id).first()
    if not user:
        request.session.flush()
        return redirect("login_view")

    form = CreateBlogForm()
    if request.method == "POST":
        form = CreateBlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = user
            blog.save()
            return redirect("userfeed_view")
    return render(request, "feed/create_new_blog.html", {"form": form})

def view_my_blogs(request):
    if not request.session.get("is_logged_in"):
        return redirect("login_view")

    user_id = request.session.get("user_id")
    user = User.objects.filter(id=user_id).first()
    if not user:
        request.session.flush()
        return redirect("login_view")    
    blogs = Blog.objects.filter(author=user)    
    deleted = request.GET.get("deleted")
    return render(request, "feed/view_my_blogs.html", {"blogs": blogs, "deleted": deleted})

def my_blog_view(request, pk):
    if not request.session.get("is_logged_in"):
        return redirect("login_view")

    blog = Blog.objects.filter(id=pk).first()
    return render(request, "feed/my_blog_view.html", {"blog": blog})

def my_blog_edit(request, pk):
    if not request.session.get("is_logged_in"):
        return redirect("login_view")

    user_id = request.session.get("user_id")
    user = User.objects.filter(id=user_id).first()

    if not user:
        request.session.flush()
        return redirect("login_view")

    blog = Blog.objects.filter(id=pk, author=user).first()
    if not blog:
        return redirect("view_my_blogs")

    if request.method == "POST":
        form = EditBlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect("my_blog_view", pk=pk)

    return render(request, "feed/my_blog_edit.html", {"blog": blog})

def my_blog_delete(request, pk):    
    if not request.session.get("is_logged_in"):
        return redirect("login_view")

    user_id = request.session.get("user_id")
    user = User.objects.filter(id=user_id).first()

    blog = Blog.objects.filter(id=pk, author=user).first()
    if not blog:
        return redirect("view_my_blogs")

    if request.method == "POST":
        blog.delete()
        return redirect("view_my_blogs")

    return redirect("view_my_blogs")

def admin_dashboard(request):
    if not request.session.get("is_logged_in"):
        return redirect("login_view")
    if not request.session.get("is_admin"):
        return redirect("userfeed_view")
    return render(request, "admin/admin_dashboard.html")

def manage_users(request):
    if not request.session.get("is_logged_in"):
        return redirect("login_view")
    
    users = User.objects.all().order_by('-id')
    
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")
        
        if action == "delete" and user_id:
            user = User.objects.filter(id=user_id).first()
            if user and not user.is_admin:
                user.delete()
                return redirect("manage_users")

        if action == "block" and user_id:
            user = User.objects.filter(id=user_id).first()
            if user and not user.is_admin:
                user.is_blocked = True
                user.save()
                return redirect("manage_users")

        if action == "unblock" and user_id:
            user = User.objects.filter(id=user_id).first()
            if user and not user.is_admin:
                user.is_blocked = False
                user.save()
                return redirect("manage_users")                
    
    return render(request, "admin/manage_users.html", {"users": users})

def manage_blogs(request):
    if not request.session.get("is_logged_in"):
        return redirect("login_view")
    
    blogs = Blog.objects.all().order_by('-id')
    if request.method == "POST":
        blog_id = request.POST.get("blog_id")
        action = request.POST.get("action")
        
        if action == "delete":
            blog = Blog.objects.filter(id=blog_id).first()
            if blog:
                blog.delete()
                return redirect("manage_blogs")

        if action == "block":
            blog = Blog.objects.filter(id=blog_id).first()
            if blog:
                blog.is_blocked = True
                blog.save()
                return redirect("manage_blogs")

        if action == "unblock":
            blog = Blog.objects.filter(id=blog_id).first()
            if blog:
                blog.is_blocked = False
                blog.save()
                return redirect("manage_blogs")
    
    return render(request,"admin/manage_blogs.html", {'blogs': blogs})       