from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
# Helper function to guess a MIME type from a file name
from mimetypes import guess_type

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator

# Used to send mail from within Django
from django.core.mail import send_mail

from django.core import serializers

from grumblr.models import *
from grumblr.forms import *

def userlogin(request):
    context={}
    errors=[]
    if request.method=="GET":
        return render(request,'grumblr/login.html',context)
   
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return render(request,'grumblr/main_stream.html',context)
    errors.append("authentication failed")
    context['errors']=errors
    return render(request,'grumblr/login.html',context)

# stream
@login_required
def main_stream(request):
    context = {}
    context['posts'] = Post.get_posts_main_stream(request.user)
    context['user'] = request.user
    context['comment_redirect'] = 'stream'

    return render(request, 'grumblr/main_stream.html', context)

@login_required
def follower_stream(request):
    context = {}
    context['posts'] = Post.get_posts_follower_stream(request.user)
    context['user'] = request.user
    context['comment_redirect'] = 'stream'
    print(request.user.id)
    context['followers'] = UserProfile.objects.get(id=request.user.id).follows.all()

    return render(request, 'grumblr/follower_stream.html', context)

@login_required
def follow(request, following_id):
    followed_user = User.objects.get(id=following_id)
    if (request.user != followed_user): 
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.follows.add(followed_user)
    return redirect(reverse('profile', kwargs={'user_id':following_id}))

@login_required
def unfollow(request, unfollowing_id):
	unfollowed_user = User.objects.get(id=unfollowing_id)
	if (request.user != unfollowed_user): 
		user_profile = UserProfile.objects.get(user=request.user)
		user_profile.follows.remove(unfollowed_user)
	return redirect(reverse('profile', kwargs={'user_id':unfollowing_id}))

@login_required
def profile(request, user_id):
    context = {}
    errors = []
    context['errors'] = errors
    # context['comment_redirect'] = 'profile'

    if len(User.objects.filter(id=user_id)) <= 0:
        errors.append('User does not exist.')

    if errors:
        # context['posts'] = Post.objects.filter(user=request.user).order_by('-date_created').reverse()
        return render(request, 'grumblr/main_stream.html', context)

    user = User.objects.get(id=user_id)
    print(user.id)
    print(request.user.id)
    # posts = Post.objects.filter(user=user).order_by('-date_created').reverse()
    # context['posts'] = posts.order_by('-date_created').reverse()
    context['user'] = user
    context['request_user'] = request.user

    user_profile = UserProfile.objects.get(user=user)
    context['user_profile'] = user_profile

    is_following = request.user.profile.follows.filter(id = user.id).exists()
    context['is_following'] = is_following

    return render(request, 'grumblr/profile.html', context)

@login_required
def profile_picture(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    if user_profile.picture:
        content_type = guess_type(user_profile.picture.name)
        return HttpResponse(user_profile.picture, content_type=content_type)
    return render(request,'grumblr/main_stream.html',{})

@login_required
@transaction.atomic
def edit_profile(request):
    context = {}
    user = request.user
    user_profile = UserProfile.objects.get(user=user)

    context['user'] = user
    context['request_user'] = request.user
    context['user_profile'] = user_profile

    context['picture-src'] = ''

    initial_user = {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'email': user.email,
                    'about': user_profile.about,
                    'age': user_profile.age,
                    'picture':user_profile.picture,
                }

    if request.method == 'GET':
        context['form'] = UserProfileForm(initial=initial_user)
        return render(request, 'grumblr/edit-profile.html', context)

    form = UserProfileForm(request.POST, request.FILES, initial=initial_user)
    context['form'] = form

    if not form.is_valid():
        raise Http404
        print(errors)
        return render(request, 'grumblr/edit-profile.html', context)

    form.save(user_instance=request.user, user_profile_instance=user_profile)
    update_session_auth_hash(request, user)

    return render(request,'grumblr/profile.html',context)

@login_required
@transaction.atomic
def add_post(request):
    if not 'post' in request.POST or not request.POST['post']:
        raise Http404
    else:
        new_post = Post(user=request.user, text=request.POST['post'])
        new_post.save()

    return HttpResponse("")  # Empty response on success.

@login_required
def delete_post(request, post_id):
    try:
        post_to_delete = Post.objects.get(id=post_id)
        post_to_delete.deleted = True  # Just mark items as deleted.
        post_to_delete.save()
    except ObjectDoesNotExist:
        return HttpResponse("The post did not exist")

    return HttpResponse("")  # Empty response on success.


@transaction.atomic
def register(request):
    context = {}
    errors = []
    context['errors'] = errors

    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'grumblr/register.html', context)


    form = RegistrationForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'grumblr/register.html', context)

    # Creates the new user from the valid form data
    new_user = form.save()

    token = default_token_generator.make_token(new_user)

    email_body = """
    Welcome to Grumblr! Please click the link below to verify your email 
    address and complete the registration of your account:

    http://%s%s
    """ % (request.get_host(), reverse('confirm-registration', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message=email_body,
              from_email="hanyut@andrew.cmu.edu",
              recipient_list=[new_user.email])

    return render(request, 'grumblr/confirmation.html', context)

@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    if not default_token_generator.check_token(user, token):
        raise Http404

    user.is_active = True
    user.save()

    user_profile = UserProfile(user=user)
    user_profile.save()

    return render(request, 'grumblr/confirmed.html', {})

@login_required
@transaction.atomic
def comment(request, redirect_name, user_id, post_id):
    context = {}
    errors = []
    if not 'comment' in request.POST or not request.POST['comment']:
        errors.append('You must post something...')
    else:
        post = Post.objects.get(id=post_id)
        new_comment = Comment(user=request.user, post=post, text=request.POST['comment'])
        new_comment.save()
        
    if (redirect_name == 'profile'):
        return redirect(reverse('profile', kwargs={'user_id':user_id}))
    else:
       return redirect(reverse(redirect_name))

# Returns all recent additions in the database, as JSON
@login_required
def get_profile_posts(request, user_id, time="1970-01-01T00:00+00:00"):
    user = User.objects.get(id=user_id)
    max_time = Post.get_max_time_user(user=user)
    posts = Post.get_posts_user(user=user, time=time)
    context = {"max_time": max_time, "posts": posts}
    return render(request, 'posts.json', context, content_type='application/json')

@login_required
def get_main_stream_posts(request, time="1970-01-01T00:00+00:00"):
    # user = User.objects.get(id=user_id)
    max_time = Post.get_max_time_main_stream(user=request.user)
    posts = Post.get_posts_main_stream(user=request.user, time=time)
    context = {"max_time": max_time, "posts": posts}
    print(max_time)
    return render(request, 'posts.json', context, content_type='application/json')

@login_required
def get_follower_stream_posts(request, time="1970-01-01T00:00+00:00"):
    max_time = Post.get_max_time_follower_stream(user=request.user)
    posts = Post.get_posts_follower_stream(user=request.user, time=time)
    context = {"max_time": max_time, "posts": posts}
    return render(request, 'posts.json', context, content_type='application/json')

# Returns all recent changes to the database, as JSON
@login_required
def get_profile_changes(request, user_id, time="1970-01-01T00:00+00:00"):
    user = User.objects.get(id=user_id)
    max_time = Post.get_max_time_user(user=user)
    posts = Post.get_changes_user(user=user, time=time)
    context = {"max_time": max_time, "posts": posts}
    return render(request, 'posts.json', context, content_type='application/json')

@login_required
def get_main_stream_changes(request, time="1970-01-01T00:00+00:00"):
    max_time = Post.get_max_time_main_stream(user=request.user)
    posts = Post.get_changes_main_stream(user=request.user, time=time)
    context = {"max_time": max_time, "posts": posts}
    return render(request, 'posts.json', context, content_type='application/json')

@login_required
def get_follower_stream_changes(request, time="1970-01-01T00:00+00:00"):
    max_time = Post.get_max_time_follower_stream(user=request.user)
    posts = Post.get_changes_follower_stream(user=request.user, time=time)
    context = {"max_time": max_time, "posts": posts}
    return render(request, 'posts.json', context, content_type='application/json')

@login_required
def get_comments(request, post_id, time="1970-01-01T00:00+00:00"):
    post = Post.objects.get(id=post_id)
    max_time = Comment.get_max_time(post=post)
    comments = Comment.get_comments(post=post)
    context = {"max_time": max_time, "comments": comments}

    return render(request, 'comments.json', context, content_type='application/json')

@login_required
def get_comment_changes(request, post_id, time="1970-01-01T00:00+00:00"):
    post = Post.objects.get(id=post_id)
    max_time = Comment.get_max_time(post=post)
    comments = Comment.get_changes(post=post, time=time)
    context = {"max_time": max_time, "comments": comments}

    return render(request, 'comments.json', context, content_type='application/json')

@login_required
def add_comment(request, post_id):
    if not 'comment' in request.POST or not request.POST['comment']:
        raise Http404
    else:
        post = Post.objects.get(id=post_id)
        new_comment = Comment(user=request.user, post=post, text=request.POST['comment'])
        new_comment.save()
        max_time = new_comment.date_created
        comments = Comment.get_comments(post)
        context = {"max_time":max_time, "comments": comments}
    
    return render(request, 'comments.json', context, content_type='application/json')
