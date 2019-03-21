from django.db import models
from django.utils import timezone
from datetime import datetime
from django.db.models import Max
from django.utils.html import escape

# Create your models here.
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.OneToOneField(User, related_name="profile",on_delete=models.CASCADE)
	age = models.IntegerField(default=0, blank=True)
	about = models.TextField(max_length=20000, default='', blank=True)
	picture = models.ImageField(upload_to='profile-pictures', default='', blank=True)
	follows = models.ManyToManyField(User, related_name='followees', symmetrical=False)

	def __unicode__(self):
		return self.user


class Post(models.Model):
	user = models.ForeignKey(User, related_name='posts',on_delete=models.CASCADE)
	text = models.TextField(max_length=20000)
	deleted = models.BooleanField(default=False)
	date_created = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.text

	@staticmethod
	def get_posts_user(user, time="1970-01-01T00:00+00:00"):
		return Post.objects.filter(user=user, deleted=False, 
			   date_created__gt=time).distinct().order_by('-date_created').reverse()

	@staticmethod
	def get_posts_main_stream(user, time="1970-01-01T00:00+00:00"):
		return Post.objects.all().filter(deleted=False, 
			   date_created__gt=time).distinct().order_by('-date_created').reverse()

	@staticmethod
	def get_posts_follower_stream(user, time="1970-01-01T00:00+00:00"):
		user_profile = UserProfile.objects.get(user=user)
		following = user_profile.follows.all()
		return Post.objects.filter(user__in=following, deleted=False, 
			   date_created__gt=time).distinct().order_by('-date_created').reverse()

	@staticmethod
	def get_max_time_user(user):
		return Post.objects.filter(user=user).aggregate(Max('date_created'))['date_created__max'] or "1970-01-01T00:00+00:00"

	@staticmethod
	def get_max_time_main_stream(user):
		return Post.objects.all().aggregate(Max('date_created'))['date_created__max'] or "1970-01-01T00:00+00:00"

	@staticmethod
	def get_max_time_follower_stream(user):
		user_profile = UserProfile.objects.get(user=user)
		following = user_profile.follows.all()
		return Post.objects.filter(user__in=following).aggregate(Max('date_created'))['date_created__max'] or "1970-01-01T00:00+00:00"

	@staticmethod
	def get_changes_user(user, time="1970-01-01T00:00+00:00"):
		return Post.objects.filter(user=user, date_created__gt=time).distinct().order_by('-date_created').reverse()

	@staticmethod
	def get_changes_main_stream(user, time="1970-01-01T00:00+00:00"):
		return Post.objects.filter(user=user).filter(date_created__gt=time).distinct().order_by('-date_created').reverse()

	@staticmethod
	def get_changes_follower_stream(user, time="1970-01-01T00:00+00:00"):
		user_profile = UserProfile.objects.get(user=user)
		following = user_profile.follows.all()
		return Post.objects.filter(user__in=following, 
			   date_created__gt=time).distinct().order_by('-date_created').reverse()

	@property
	def html(self):
		time = str(self.date_created).split('.')
		if self.user.profile.picture:
			return "<li class='post_item' id='post_%d'> \
					<div class='form card'> \
					<div class='card-content'> \
					<div class='post-main'>\
					<span class='card-title grey-text text-darken-4 post-content'> %s </span>  \
					<p class='date_created'> %s </p> \
					</div>\
					<div class='card-profile'> \
					<span>\
	      			<img class='responsive-img' src='/profile-picture/%s' alt='No picture'> \
	      			</span>\
					<a href='/profile/%s'> %s %s </a>\
					</div>\
					<span class='comment-btn'>\
					<i class='material-icons activator'>comment</i>\
					</span>\
	        		</div> \
	        		<div class= 'card-reveal'> \
	      			<span class= 'card-title grey-text text-darken-4'>Comment<i class='material-icons right'>close</i></span> \
	      			<textarea class='form-control comment-area' type='text' placeholder='Write something...' name='comment' id='new-comment'> </textarea>\
	        		<button id='comment-btn'>Comment</button><ul style='list-style-type: none' id='comment-list'></ul> \
	   				</div> \
	        		</div> \
	        		</li>" % (self.id, escape(self.text), time[0], escape(self.user.id), escape(self.user.id), escape(self.user.first_name), escape(self.user.last_name))
		else:
			return "<li class='post_item' id='post_%d'> \
					<div class='form card'> \
					<div class='card-content'> \
					<div class='post-main'>\
					<span class='card-title grey-text text-darken-4 post-content'> %s </span>  \
					<p class='date_created'> %s </p> \
					</div>\
					<div class='card-profile'> \
					<span>\
	      			<img class='responsive-img' src='/static/site-resources/default.png' alt='No picture'> \
	      			</span>\
					<a href='/profile/%s'> %s %s </a>\
					</div>\
					<span class='comment-btn'>\
					<i class='material-icons activator'>comment</i>\
					</span>\
	        		</div> \
	        		<div class= 'card-reveal'> \
	      			<span class= 'card-title grey-text text-darken-4'>Comment<i class='material-icons right'>close</i></span> \
	      			<textarea class='form-control comment-area' type='text' placeholder='Write something...' name='comment' id='new-comment'> </textarea>\
	        		<button id='comment-btn'>Comment</button><ul style='list-style-type: none' id='comment-list'></ul> \
	   				</div> \
	        		</div> \
	        		</li>" % (self.id, escape(self.text), time[0], escape(self.user.id), escape(self.user.first_name), escape(self.user.last_name))
	    

	

class Comment(models.Model):
	user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE) 
	post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE) 
	deleted = models.BooleanField(default=False)
	text = models.TextField(max_length=20000)
	date_created = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.text

	@staticmethod
	def get_comments(post, time="1970-01-01T00:00+00:00"):
		return Comment.objects.filter(post=post, deleted=False, 
			           date_created__gt=time).distinct().order_by('-date_created').reverse()

	@staticmethod
	def get_changes(post, time="1970-01-01T00:00+00:00"):
		return Comment.objects.filter(post=post, date_created__gt=time).distinct().order_by('-date_created').reverse()

	@property
	def html(self):
		time = str(self.date_created).split('.')
		if self.user.profile.picture:
			return "<hr>\
					<li id='comment_%d'>\
					<div class='form card'> \
					<div class='card-content'> \
					<div class='post-main'>\
					<span class='card-title grey-text text-darken-4 post-content'> %s </span>  \
					<p class='date_created'> %s </p> \
					</div>\
					<div class='card-profile'> \
					<span>\
	      			<img class='responsive-img' src='/profile-picture/%s' alt='No picture right now'> \
	      			</span>\
					<a href='/profile/%s'> %s %s </a>\
					</div>\
					</div>\
					</div>\
	         		</li>" % (self.id, escape(self.text), time[0], escape(self.user.id), escape(self.user.id), escape(self.user.first_name), escape(self.user.last_name))
		else:
			return "<hr>\
					<li id='comment_%d'>\
					<div class='form card'> \
					<div class='card-content'> \
					<div class='post-main'>\
					<span class='card-title grey-text text-darken-4 post-content'> %s </span>  \
					<p class='date_created'> %s </p> \
					</div>\
					<div class='card-profile'> \
					<span>\
	      			<img class='responsive-img' src='/static/site-resources/default.png' alt='Nope'> \
	      			</span>\
					<a href='/profile/%s'> %s %s </a>\
					</div>\
					</div>\
					</div>\
	         		</li>" % (self.id, escape(self.text), time[0], escape(self.user.id), escape(self.user.first_name), escape(self.user.last_name))
	

	@staticmethod
	def get_max_time(post):
		return Comment.objects.filter(post=post).aggregate(Max('date_created'))['date_created__max'] or "1970-01-01T00:00+00:00"