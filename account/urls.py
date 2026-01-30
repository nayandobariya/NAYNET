from django.urls import path, include
from account import views

from django.conf.urls.static import static
app_name = "account"

urlpatterns = [

    path('employee/register/', views.employee_registration, name='employee-registration'),
    path('employer/register/', views.employer_registration, name='employer-registration'),
    path('profile/edit/<int:id>/', views.employee_edit_profile, name='edit-profile'),
    path('social/accounts/', views.social_accounts, name='social_accounts'),
    path('social/disconnect/<int:account_id>/', views.disconnect_social, name='disconnect_social'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('send-invite/<int:user_id>/', views.send_connection_request, name='send_connection_request'),
    path('accept-invite/<int:request_id>/', views.accept_connection_request, name='accept_connection_request'),
    path('decline-invite/<int:request_id>/', views.decline_connection_request, name='decline_connection_request'),
    path('social/home/', views.social_home, name='social-home'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('settings/', views.settings_view, name='settings'),
    
    # Standardized Posts URLs
    path('posts/', views.posts_view, name='posts'),
    path('posts/feed/', views.get_posts_ajax, name='get_posts_ajax'),
    path('posts/create/', views.create_post_ajax, name='create_post_ajax'),
    path('posts/<int:post_id>/like/', views.like_post, name='like_post'),
    path('posts/<int:post_id>/delete/', views.delete_post_ajax, name='delete_post_ajax'),
    path('posts/<int:post_id>/edit/', views.edit_post_ajax, name='edit_post_ajax'),
    path('posts/<int:post_id>/comments/', views.get_post_comments_ajax, name='get_post_comments'),
    path('posts/<int:post_id>/comments/create/', views.comment_post, name='create_comment_ajax'),
    
    # Standardized Messages URLs
    path('messages/', views.messages_view, name='messages'),
    path('messages/conversations/', views.get_conversations_ajax, name='conversations_ajax'),
    path('messages/chat/<int:user_id>/', views.get_chat_data_ajax, name='chat_data_ajax'),
    path('messages/chat/<int:user_id>/messages/', views.get_chat_messages_ajax, name='chat_messages_ajax'),
    path('messages/send/<int:user_id>/', views.send_message, name='send_message_ajax'),
    path('messages/online-users/', views.get_online_users_ajax, name='online_users_ajax'),
    path('messages/clear/<int:user_id>/', views.clear_chat_ajax, name='clear_chat_ajax'),
    path('messages/poll/<int:user_id>/', views.poll_messages, name='poll_messages'),
    
    path('search/people/', views.search_users, name='search_people_ajax'),
    path('notifications/count/', views.get_notifications, name='notifications_count'),
    path('notifications/list/', views.get_notifications_list, name='get_notifications'),
    path('recent-activity/', views.recent_activity, name='recent_activity'),
    path('search-people/', views.search_users, name='search_people_fixed'),
    
    path('login/', views.user_logIn, name='login'),
    path('logout/', views.user_logOut, name='logout'),
    
    # Network URLs
    path('network/', views.network, name='network'),
    path('network/ajax/', views.get_network_ajax, name='get_network_ajax'),
    path('connection-suggestions/ajax/', views.get_connection_suggestions_ajax, name='get_connection_suggestions_ajax'),
    path('follow-unfollow/<int:user_id>/', views.follow_unfollow_ajax, name='follow_unfollow_ajax'),
    path('accept-decline/<int:request_id>/<str:action>/', views.accept_decline_request_ajax, name='accept_decline_request_ajax'),
    
    # Individual Profile view (if needed)
    path('profile/<int:id>/', views.employee_edit_profile, name='edit-profile'),
    path('update-profile-picture/ajax/', views.update_profile_picture_ajax, name='update_profile_picture_ajax'),
    path('update-profile/ajax/', views.update_profile_ajax, name='update_profile_ajax'),
    
    # Test page for debugging
    path('test-post/', views.test_post_page, name='test_post'),
]

