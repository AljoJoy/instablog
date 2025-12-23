from tkinter import Image
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    email = models.EmailField()
    profile_pic = models.ImageField(upload_to='images/')
    contact_number = models.CharField(max_length=15, default="")
    password = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

class Blog(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='images/')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)

class Comment(models.Model):
    comment_text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
