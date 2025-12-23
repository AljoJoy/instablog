from django.forms import ModelForm
from .models import User, Blog

class RegistrationForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_pic', 'contact_number', 'password']

class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class UpdateProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_pic', 'contact_number']

class CreateBlogForm(ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', 'image']

class EditBlogForm(ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', 'image']        
