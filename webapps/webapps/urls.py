

from django.conf.urls import url, include
from django.urls import re_path, path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
import grumblr.views

urlpatterns = [
    re_path(r'^$', grumblr.views.main_stream, name='stream'),
    re_path(r'^follower-stream$', grumblr.views.follower_stream, name='follower-stream'),
    re_path(r'^profile/(?P<user_id>\d+)$', grumblr.views.profile, name='profile'),

    # Route for built-in authentication with our own custom login page
    re_path(r'^login$', grumblr.views.userlogin, name='login'),


    # Reset password
    re_path(r'^reset$', auth_views.PasswordResetView.as_view(), {'template_name':'grumblr/password_reset_form.html',
                                           'from_email':'qianhuis@andrew.cmu.edu',
                                           'post_reset_redirect':'/reset/done'},
                                           name='password_reset'),
    re_path(r'^reset/done$', auth_views.PasswordResetDoneView.as_view(), {'template_name':'grumblr/password_reset_done.html'}, name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.PasswordResetConfirmView.as_view(), 
        {'template_name':'grumblr/password_reset_confirm.html', 'post_reset_redirect':'/done'}, 
        name='password_reset_confirm'),
    re_path(r'^done$', auth_views.PasswordResetCompleteView.as_view(), {'template_name':'grumblr/password_reset_complete.html'}, name='reset_complete'),



    re_path(r'^profile-picture/(?P<user_id>\d+)$', grumblr.views.profile_picture, name='profile-picture'),
    # Route to logout a user and send them back to the login page
    re_path(r'^logout$', auth_views.logout_then_login, name='logout'),
    re_path(r'^register$', grumblr.views.register, name='register'),
    re_path(r'^add-post$', grumblr.views.add_post, name='add-post'),
    re_path(r'^delete-post/(?P<post_id>\d+)$', grumblr.views.delete_post, name='delete-post'),
    re_path(r'^edit-profile$', grumblr.views.edit_profile, name='edit-profile'),

    re_path(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', grumblr.views.confirm_registration, name='confirm-registration'),
    re_path(r'^follow/(?P<following_id>\d+)$', grumblr.views.follow, name='follow'),
    re_path(r'^unfollow/(?P<unfollowing_id>\d+)$', grumblr.views.unfollow, name='unfollow'),
    #url(r'^comment/(?P<redirect_name>\w+)/(?P<user_id>\d+)/(?P<post_id>\d+)$', grumblr.views.comment, name='comment'),

    re_path(r'^get-profile-posts/(?P<user_id>\d+)$', grumblr.views.get_profile_posts, name='get-profile-posts'),
    re_path(r'^get-global-stream-posts$', grumblr.views.get_main_stream_posts, name='get-global-stream-posts'),
    re_path(r'^get-follower-stream-posts$', grumblr.views.get_follower_stream_posts, name='get-follower-stream-posts'),
    re_path(r'^get-profile-posts/(?P<user_id>\d+)/(?P<time>.+)$', grumblr.views.get_profile_posts, name='get-profile-posts'),
    #re_path(r'^get-global-stream-posts/(?P<time>.+)$', grumblr.views.get_main_stream_posts, name='get-global-stream-posts'),
    re_path(r'^get-follower-stream-posts/(?P<time>.+)$', grumblr.views.get_follower_stream_posts, name='get-follower-stream-posts'),
    
    # url(r'^get-posts/(?P<username>[A-Za-z]\w*)/(?P<post_id>\d+)$', grumblr.views.get_posts, name='get-posts-username-post-id'),
    # url(r'^get-posts/(?P<username>[A-Za-z]\w*)$', grumblr.views.get_posts, name='get-posts-username'),

    re_path(r'^get-profile-changes/(?P<user_id>\d+)/$', grumblr.views.get_profile_changes, name='get-profile-changes'),
    re_path(r'^get-global-stream-changes$', grumblr.views.get_main_stream_changes, name='get-global-stream-changes'),
    re_path(r'^get-follower-stream-changes$', grumblr.views.get_follower_stream_changes, name='get-follower-stream-changes'),
    re_path(r'^get-profile-changes/(?P<user_id>\d+)/(?P<time>.+)$', grumblr.views.get_profile_changes, name='get-profile-changes'),
    re_path(r'^get-global-stream-changes/(?P<time>.+)$', grumblr.views.get_main_stream_changes, name='get-global-stream-changes'),
    re_path(r'^get-follower-stream-changes/(?P<time>.+)$', grumblr.views.get_follower_stream_changes, name='get-follower-stream-changes'),
    
    # url(r'^get-changes/(?P<post_id>\d+)$', grumblr.views.get_changes, name='get-changes-post-id'),

    # url(r'^get-comments$', grumblr.views.get_comments),
    re_path(r'^get-comments/(?P<post_id>\d+)$', grumblr.views.get_comments),
    re_path(r'^get-comments/(?P<post_id>\d+)/(?P<time>.+)$', grumblr.views.get_comments),
    re_path(r'^get-comment-changes/(?P<post_id>\d+)/$', grumblr.views.get_comment_changes),
    re_path(r'^get-comment-changes/(?P<post_id>\d+)/(?P<time>.+)$', grumblr.views.get_comment_changes),
    re_path(r'^add-comment/(?P<post_id>\d+)$', grumblr.views.add_comment),
]
