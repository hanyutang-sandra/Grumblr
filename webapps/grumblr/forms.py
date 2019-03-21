from django import forms

from django.contrib.auth.models import User
from grumblr.models import *

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Grumble grumble grumble...', 'class': 'textarea-text-post'})
        }
        error_messages = {
            'text': {
                'required': 'You must write something in your post!'
            }
        }
    
    def clean(self):
        cleaned_data = super(PostForm, self).clean()
        return cleaned_data

class ConfirmEmailForm(forms.Form):
    email = forms.CharField(max_length = 200, widget=forms.EmailInput(attrs={'placeholder': 'example@gmail.com'}))

    def clean(self):
        cleaned_data = super(ConfirmEmailForm, self).clean()
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email__exact=email):
            raise forms.ValidationError('This email does not exist.')
        return email

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')
        widgets = {
            'password': forms.PasswordInput()  
        }

    password2 = forms.CharField(max_length=200, label='Confirm Password', 
                                error_messages={'required': 'Password confirmation is required.'}, 
                                widget=forms.PasswordInput())  

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError('Passwords did not match.')
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError('Username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact=email):
            raise forms.ValidationError('Email is already taken.')
        return email

    def save(self):
        new_user = User.objects.create_user(username=self.cleaned_data.get('username'), \
                                            email=self.cleaned_data.get('email'), \
                                            password=self.cleaned_data.get('password'), \
                                            last_name=self.cleaned_data.get('last_name'), \
                                            first_name=self.cleaned_data.get('first_name'))
        new_user.is_active = False
        new_user.save()
        
        return new_user


class UserProfileForm(forms.Form):
    picture = forms.FileField(label='Profile Picture', required=False)
    first_name = forms.CharField(max_length=20, label='First Name', required=False)
    last_name = forms.CharField(max_length=20, label='Last Name', required=False)
    username = forms.CharField(max_length=20, label='Username', required=False)
    email = forms.CharField(max_length=200, label='Email', required=False)
    about = forms.CharField(max_length=200, label='About', required=False)
    age = forms.IntegerField(label='Age', required=False)


    def clean(self):
        cleaned_data = super(UserProfileForm, self).clean()
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user_exists = User.objects.filter(username__exact=username)
        if user_exists and self.initial['username'] != username:
            raise forms.ValidationError('Username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_exists = User.objects.filter(email__exact=email)
        if email_exists and self.initial['email'] != email:
            raise forms.ValidationError('Email is already taken.')
        return email


    def save(self, user_instance, user_profile_instance):
        if self.cleaned_data.get('last_name'):
            user_instance.last_name = self.cleaned_data.get('last_name')

        if self.cleaned_data.get('first_name'):
            user_instance.first_name = self.cleaned_data.get('first_name')
        
        if self.cleaned_data.get('username'):
            user_instance.username = self.cleaned_data.get('username')
        
        if self.cleaned_data.get('email'):
            user_instance.email = self.cleaned_data.get('email')

        if self.cleaned_data.get('about'):
            user_profile_instance.about = self.cleaned_data.get('about')
        
        if self.cleaned_data.get('picture'):
            user_profile_instance.picture = self.cleaned_data.get('picture')
        
        if self.cleaned_data.get('age'):
            user_profile_instance.age = self.cleaned_data.get('age')

        if self.cleaned_data.get('url'):
            user_profile_instance.url = self.cleaned_data.get('url')

        user_instance.save()
        user_profile_instance.save()
        
        return user_instance