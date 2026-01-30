from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect , get_object_or_404
from django.urls import reverse, reverse_lazy
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from datetime import datetime
from account.forms import *
from account.models import Post, Like, Comment, Message, Follow, ConnectionRequest
from jobapp.permission import user_is_employee
from jobapp import forms as jforms
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import pandas as pd

def get_success_url(request):

    """
    Handle Success Url After LogIN

    """
    if 'next' in request.GET and request.GET['next'] != '':
        return request.GET['next']
    else:
        return reverse('jobapp:home')


def employee_registration(request):

    """
    Handle Employee Registration

    """
    form = EmployeeRegistrationForm(request.POST or None)
    student_form = jforms.StudentForm(request.POST or None)
    if form.is_valid() and student_form.is_valid():
        # Save to default database (SQLite)
        form = form.save()
        student = student_form.save(commit=False)
        student.user = form
        student.save()

        # Save to MySQL database
        from django.db import connections
        mysql_conn = connections['mysql_db']
        with mysql_conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO custom_account_user (email, first_name, last_name, role, gender, profile_picture, password, last_login, is_superuser, is_staff, is_active, date_joined)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE email=email
            """, [
                form.email, form.first_name, form.last_name, form.role, form.gender,
                form.profile_picture.path if form.profile_picture else None,
                form.password, form.last_login, form.is_superuser,
                form.is_staff, form.is_active, form.date_joined
            ])

            cursor.execute("""
                INSERT INTO jobapp_student (user_id, mobile, address, profile_pic)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE user_id=user_id
            """, [
                student.user_id, student.mobile, student.address,
                student.profile_pic.path if student.profile_pic else None
            ])

        return redirect('account:login')
    context = {

        'form': form,
        'studentform': student_form
    }

    return render(request,'account/employee-registration.html',context)


def employer_registration(request):

    """
    Handle Employer Registration

    """

    form = EmployerRegistrationForm(request.POST or None)
    teacher_form = jforms.TeacherForm(request.POST, request.FILES)
    if form.is_valid() and teacher_form.is_valid():
        # Save to default database (SQLite)
        form = form.save()
        teacher = Teacher()
        teacher.user = form
        teacher.profile_pic = teacher_form.cleaned_data.get('profile_pic')
        teacher.address = teacher_form.cleaned_data.get('address')
        teacher.mobile = teacher_form.cleaned_data.get('mobile')
        teacher.salary = teacher_form.cleaned_data.get('salary')
        teacher.save()

        # Save to MySQL database
        from django.db import connections
        mysql_conn = connections['mysql_db']
        with mysql_conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO custom_account_user (email, first_name, last_name, role, gender, profile_picture, password, last_login, is_superuser, is_staff, is_active, date_joined)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE email=email
            """, [
                form.email, form.first_name, form.last_name, form.role, form.gender,
                form.profile_picture.path if form.profile_picture else None,
                form.password, form.last_login, form.is_superuser,
                form.is_staff, form.is_active, form.date_joined
            ])

            cursor.execute("""
                INSERT INTO jobapp_teacher (user_id, mobile, address, profile_pic, salary)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE user_id=user_id
            """, [
                teacher.user_id, teacher.mobile, teacher.address,
                teacher.profile_pic.path if teacher.profile_pic else None,
                teacher.salary
            ])

        return redirect('account:login')
    context={

            'form': form,
            'teacherform': teacher_form
        }

    return render(request,'account/employer-registration.html',context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def employee_edit_profile(request, id):

    """
    Handle Employee Profile Update Functionality

    """

    user = get_object_or_404(User, id=id)
    #upload_cv(request, str(id))
    form = EmployeeProfileEditForm(request.POST or None, instance=user)
    #fieldname1=form.data('first_name')
    #fieldname2=form.data('last_name')
    fieldsfname = form.data.get('first_name')
    fieldslname = form.data.get('last_name')
    if form.is_valid():
        form = form.save()
        if 'document' in request.FILES:
            uploaded_file = request.FILES['document']
            fs = FileSystemStorage()
            filename=str(fieldsfname)+' '+str(fieldslname)+'.pdf'
            name = fs.save(filename, uploaded_file)
            url = fs.url(name)
        messages.success(request, 'Your Profile Was Successfully Updated!')

        return redirect(reverse("account:edit-profile", kwargs={
                                    'id': form.id
                                    }))
    context={
        
            'form':form
        }

    return render(request,'account/employee-edit-profile.html',context)



def user_logIn(request):

    """
    Provides users to logIn

    """

    form = UserLoginForm(request.POST or None)
    

    if request.user.is_authenticated:
        return redirect('/')
    
    else:
        if request.method == 'POST':
            if form.is_valid():
                auth.login(request, form.get_user())
                return HttpResponseRedirect(get_success_url(request))
    context = {
        'form': form,
    }

    return render(request,'account/login.html',context)


def user_logOut(request):
    """
    Provide the ability to logout
    """
    auth.logout(request)
    messages.success(request, 'You are Successfully logged out')
    return redirect('account:login')


@login_required
def social_accounts(request):
    """
    Display and manage social accounts
    """
    social_accounts = SocialAccount.objects.filter(user=request.user)
    return render(request, 'account/social_accounts.html', {'social_accounts': social_accounts})


@login_required
def disconnect_social(request, account_id):
    """
    Disconnect a social account
    """
    account = get_object_or_404(SocialAccount, id=account_id, user=request.user)
    account.delete()
    messages.success(request, 'Social account disconnected successfully.')
    return redirect('account:social_accounts')


@login_required
def follow_user(request, user_id):
    """
    Follow a user
    """
    user_to_follow = get_object_or_404(User, id=user_id)
    if user_to_follow != request.user:
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        messages.success(request, f'You are now following {user_to_follow.get_full_name()}.')
    return redirect('account:edit-profile', id=request.user.id)


@login_required
def unfollow_user(request, user_id):
    """
    Unfollow a user
    """
    user_to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    messages.success(request, f'You have unfollowed {user_to_unfollow.get_full_name()}.')
    return redirect('account:edit-profile', id=request.user.id)


@login_required
def send_connection_request(request, user_id):
    """
    Send a connection request
    """
    user_to_connect = get_object_or_404(User, id=user_id)
    if user_to_connect != request.user:
        ConnectionRequest.objects.get_or_create(sender=request.user, receiver=user_to_connect)
        messages.success(request, f'Connection request sent to {user_to_connect.get_full_name()}.')
    return redirect('account:edit-profile', id=request.user.id)


@login_required
def accept_connection_request(request, request_id):
    """
    Accept a connection request
    """
    connection_request = get_object_or_404(ConnectionRequest, id=request_id, receiver=request.user)
    connection_request.status = 'accepted'
    connection_request.save()
    messages.success(request, f'You are now connected with {connection_request.sender.get_full_name()}.')
    return redirect('account:edit-profile', id=request.user.id)


@login_required
def decline_connection_request(request, request_id):
    """
    Decline a connection request
    """
    connection_request = get_object_or_404(ConnectionRequest, id=request_id, receiver=request.user)
    connection_request.status = 'declined'
    connection_request.save()
    messages.success(request, 'Connection request declined.')
    return redirect('account:edit-profile', id=request.user.id)


@login_required
def posts_view(request):
    """
    Display posts feed
    """
    following_users = request.user.following.values_list('following', flat=True)
    posts = Post.objects.filter(author__in=following_users).order_by('-created_at')
    return render(request, 'account/posts.html', {'posts': posts})


@login_required
def create_post(request):
    """
    Create a new post
    """
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        Post.objects.create(author=request.user, content=content, image=image)
        messages.success(request, 'Post created successfully.')
        return redirect('account:posts')
    return redirect('account:posts')


@login_required
def like_post(request, post_id):
    """
    Like or unlike a post
    """
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_liked': liked,
            'likes_count': post.total_likes
        })
    return redirect('account:posts')


@login_required
def delete_post_ajax(request, post_id):
    """ AJAX delete post """
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        post.delete()
        return JsonResponse({'success': True, 'message': 'Post deleted'})
    return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

@login_required
def edit_post_ajax(request, post_id):
    """ AJAX edit post content """
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        if request.method == 'POST':
            content = request.POST.get('content')
            post.content = content
            post.save()
            return JsonResponse({'success': True, 'message': 'Post updated'})
    return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)


@login_required
def comment_post(request, post_id):
    """
    Comment on a post
    """
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment = Comment.objects.create(user=request.user, post=post, content=content)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'comment': {
                        'author_name': request.user.get_full_name() or request.user.email,
                        'content': comment.content,
                        'created_at_formatted': comment.created_at.strftime('%b %d, %H:%M'),
                        'author_profile_pic': request.user.profile_picture.url if request.user.profile_picture else None
                    }
                })
    return redirect('account:posts')


@login_required
def messages_view(request):
    """
    Display messages
    """
    # Get all users the current user has messaged with
    sent_messages = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
    received_messages = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
    user_ids = set(sent_messages) | set(received_messages)

    conversations = []
    for user_id in user_ids:
        other_user = User.objects.get(id=user_id)
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=request.user))
        ).order_by('-created_at').first()

        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=request.user))
        ).order_by('created_at')

        conversations.append({
            'other_user': other_user,
            'last_message': last_message,
            'messages': messages
        })

    conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else datetime.min, reverse=True)

    return render(request, 'account/messages.html', {'conversations': conversations})


@login_required
def send_message(request, user_id):
    """
    Send a message to a user
    """
    receiver = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        message = Message.objects.create(sender=request.user, receiver=receiver, content=content)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'message': {
                    'sender': message.sender.id,
                    'content': message.content,
                    'created_at': message.created_at.isoformat()
                }
            })
    return redirect('account:messages')


@login_required
def connection_suggestions(request):
    """
    Display connection suggestions
    """
    # Get users not already connected or requested
    connected_users = ConnectionRequest.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)) & Q(status='accepted')
    ).values_list('sender', 'receiver')

    connected_ids = set()
    for sender, receiver in connected_users:
        connected_ids.add(sender)
        connected_ids.add(receiver)

    requested_users = ConnectionRequest.objects.filter(
        sender=request.user, status='pending'
    ).values_list('receiver', flat=True)

    exclude_ids = connected_ids | set(requested_users) | {request.user.id}

    suggestions = User.objects.exclude(id__in=exclude_ids)[:10]  # Limit to 10 suggestions

    return render(request, 'account/connection_suggestions.html', {'suggestions': suggestions})


@login_required
def network(request):
    """
    Display user's network
    """
    # Get connections (accepted requests)
    connections = []
    accepted_requests = ConnectionRequest.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)) & Q(status='accepted')
    )

    for req in accepted_requests:
        if req.sender == request.user:
            connections.append(req.receiver)
        else:
            connections.append(req.sender)

    following = Follow.objects.filter(follower=request.user)
    followers = Follow.objects.filter(following=request.user)

    return render(request, 'account/network.html', {
        'connections': connections,
        'following': following,
        'followers': followers
    })


@login_required
def poll_messages(request, user_id):
    """
    Poll for new messages from a specific user
    """
    since = request.GET.get('since', 0)
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver_id=user_id)) |
        (Q(sender_id=user_id) & Q(receiver=request.user))
    ).filter(created_at__gt=datetime.fromtimestamp(int(since) / 1000.0)).order_by('created_at')

    messages_data = [{
        'sender': msg.sender.id,
        'content': msg.content,
        'created_at': msg.created_at.isoformat()
    } for msg in messages]

    return JsonResponse({'messages': messages_data})


@login_required
def get_notifications(request):
    """
    Get notification counts for header
    """
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False).count()
    pending_requests = ConnectionRequest.objects.filter(receiver=request.user, status='pending').count()
    
    # For now, let's say total_notifications is just pending requests + logic for future likes/comments
    total_notifications = pending_requests 

    return JsonResponse({
        'unread_messages': unread_messages,
        'pending_requests': pending_requests,
        'total_notifications': total_notifications
    })


@login_required
def search_users(request):
    """
    Search for users
    """
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
        ).exclude(id=request.user.id)[:10]
    else:
        users = User.objects.none()

    users_data = [{
        'id': user.id,
        'name': user.get_full_name(),
        'profile_picture': user.profile_picture.url if user.profile_picture else None,
        'role': user.role
    } for user in users]

    return JsonResponse({'users': users_data})


@login_required
def get_profile_data(request):
    """
    Get updated profile data for dynamic header update
    """
    user = request.user
    data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_picture': user.profile_picture.url if user.profile_picture else None,
        'role': user.role
    }
    return JsonResponse(data)


@login_required
def update_profile_ajax(request):
    """
    AJAX profile update
    """
    if request.method == 'POST':
        user = request.user
        form = EmployeeProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully!',
                'profile_picture': user.profile_picture.url if user.profile_picture else None,
                'first_name': user.first_name,
                'last_name': user.last_name
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def follow_unfollow_ajax(request, user_id):
    """
    AJAX follow/unfollow
    """
    user_to_follow = get_object_or_404(User, id=user_id)
    if user_to_follow == request.user:
        return JsonResponse({'success': False, 'message': 'Cannot follow yourself'})

    follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    if not created:
        follow.delete()
        action = 'unfollowed'
    else:
        action = 'followed'

    return JsonResponse({'success': True, 'action': action})


@login_required
def accept_decline_request_ajax(request, request_id, action):
    """
    AJAX accept/decline connection request
    """
    connection_request = get_object_or_404(ConnectionRequest, id=request_id, receiver=request.user)
    if action == 'accept':
        connection_request.status = 'accepted'
        message = 'Connection request accepted'
    elif action == 'decline':
        connection_request.status = 'declined'
        message = 'Connection request declined'
    else:
        return JsonResponse({'success': False, 'message': 'Invalid action'})

    connection_request.save()
    return JsonResponse({'success': True, 'message': message})


@login_required
def test_post_page(request):
    """Simple test page for debugging post creation"""
    return render(request, 'test_post.html')


@login_required
def create_post_ajax(request):
    """
    AJAX create post with detailed error logging
    """
    try:
        if request.method != 'POST':
            return JsonResponse({
                'success': False, 
                'message': 'Invalid request method. Expected POST.'
            }, status=405)
        
        # Log received data for debugging
        print("=" * 50)
        print("POST DATA:", request.POST)
        print("FILES:", request.FILES)
        print("=" * 50)
        
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        post_type = request.POST.get('post_type', 'photo')
        video_url = request.POST.get('video_url', '').strip()
        event_date_str = request.POST.get('event_date', '').strip()
        
        # Validation
        if not content and not image and not video_url:
            return JsonResponse({
                'success': False,
                'message': 'Post must have content, an image, or a video URL.'
            }, status=400)
        
        # Create the post
        post = Post.objects.create(
            author=request.user, 
            content=content, 
            image=image,
            post_type=post_type,
            video_url=video_url if video_url else None
        )
        
        # Handle event date if provided
        if event_date_str and post_type == 'event':
            try:
                from django.utils.dateparse import parse_datetime
                parsed_date = parse_datetime(event_date_str)
                if parsed_date:
                    post.event_date = parsed_date
                    post.save()
                    print(f"Event date saved: {parsed_date}")
            except Exception as e:
                print(f"Error parsing event date: {e}")

        # Prepare response data
        response_data = {
            'success': True,
            'post': {
                'id': post.id,
                'content': post.content,
                'image': post.image.url if post.image else None,
                'post_type': post.post_type,
                'video_url': post.video_url,
                'event_date': post.event_date.strftime('%b %d, %Y %H:%M') if post.event_date else None,
                'author_name': request.user.get_full_name() or request.user.email,
                'author_id': request.user.id,
                'author_profile_pic': request.user.profile_picture.url if request.user.profile_picture else None,
                'created_at_formatted': 'Just now',
                'likes_count': 0,
                'comments_count': 0,
                'is_liked': False
            }
        }
        
        print(f"✓ Post created successfully: ID={post.id}")
        return JsonResponse(response_data)
        
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print("=" * 50)
        print("ERROR CREATING POST:")
        print(error_trace)
        print("=" * 50)
        
        return JsonResponse({
            'success': False,
            'message': f'Server error: {str(e)}',
            'error_details': error_trace if request.user.is_staff else None
        }, status=500)


@login_required
def get_posts_ajax(request):
    """
    AJAX get posts feed (followed users + own posts)
    """
    page = int(request.GET.get('page', 1))
    page_size = 10
    start = (page - 1) * page_size
    end = start + page_size

    following_ids = list(request.user.following.values_list('following_id', flat=True))
    following_ids.append(request.user.id) # Include self
    
    posts_qs = Post.objects.filter(author_id__in=following_ids).order_by('-created_at')
    total_count = posts_qs.count()
    posts = posts_qs[start:end]

    posts_data = []
    for post in posts:
        posts_data.append({
            'id': post.id,
            'content': post.content,
            'image': post.image.url if post.image else None,
            'post_type': post.post_type,
            'video_url': post.video_url,
            'event_date': post.event_date.strftime('%b %d, %Y %H:%M') if post.event_date else None,
            'author_name': post.author.get_full_name() or post.author.username,
            'author_id': post.author.id,
            'author_profile_pic': post.author.profile_picture.url if post.author.profile_picture else None,
            'created_at_formatted': post.created_at.strftime('%b %d, %I:%M %p'),
            'likes_count': post.total_likes,
            'comments_count': post.total_comments,
            'is_liked': Like.objects.filter(user=request.user, post=post).exists()
        })

    return JsonResponse({
        'posts': posts_data,
        'has_more': end < total_count
    })


@login_required
def get_connection_suggestions_ajax(request):
    """
    AJAX get connection suggestions
    """
    # Get users not already connected or requested
    connected_users = ConnectionRequest.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)) & Q(status='accepted')
    ).values_list('sender', 'receiver')

    connected_ids = set()
    for sender, receiver in connected_users:
        connected_ids.add(sender)
        connected_ids.add(receiver)

    requested_users = ConnectionRequest.objects.filter(
        sender=request.user, status='pending'
    ).values_list('receiver', flat=True)

    exclude_ids = connected_ids | set(requested_users) | {request.user.id}

    suggestions = User.objects.exclude(id__in=exclude_ids)[:10]

    suggestions_data = [{
        'id': user.id,
        'name': user.get_full_name(),
        'profile_picture': user.profile_picture.url if user.profile_picture else None,
        'role': user.role
    } for user in suggestions]

    return JsonResponse({'suggestions': suggestions_data})


@login_required
def get_network_ajax(request):
    """
    AJAX get network data
    """
    # Connections
    connections = []
    accepted_requests = ConnectionRequest.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)) & Q(status='accepted')
    )

    for req in accepted_requests:
        if req.sender == request.user:
            connections.append({
                'id': req.receiver.id,
                'name': req.receiver.get_full_name(),
                'profile_picture': req.receiver.profile_picture.url if req.receiver.profile_picture else None,
                'role': req.receiver.role
            })
        else:
            connections.append({
                'id': req.sender.id,
                'name': req.sender.get_full_name(),
                'profile_picture': req.sender.profile_picture.url if req.sender.profile_picture else None,
                'role': req.sender.role
            })

    # Following
    following = []
    for follow in Follow.objects.filter(follower=request.user):
        following.append({
            'id': follow.following.id,
            'name': follow.following.get_full_name(),
            'profile_picture': follow.following.profile_picture.url if follow.following.profile_picture else None,
            'role': follow.following.role
        })

    # Followers
    followers = []
    for follow in Follow.objects.filter(following=request.user):
        followers.append({
            'id': follow.follower.id,
            'name': follow.follower.get_full_name(),
            'profile_picture': follow.follower.profile_picture.url if follow.follower.profile_picture else None,
            'role': follow.follower.role
        })

    return JsonResponse({
        'connections': connections,
        'following': following,
        'followers': followers
    })




@login_required
def social_home(request):
    """  Social Home - Redirect to Posts Feed """
    return redirect('account:posts')

@login_required
def notifications_view(request):
    """ Display notifications page """
    # For now, just render the template. We'll add logic for different types of notifications.
    return render(request, 'account/notifications.html')

@login_required
def settings_view(request):
    """ Display social settings page """
    return render(request, 'account/settings.html')

@login_required
def get_conversations_ajax(request):
    """ AJAX call to get all conversations for the user """
    sent_messages = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
    received_messages = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
    user_ids = set(sent_messages) | set(received_messages)

    conversations_data = []
    for user_id in user_ids:
        other_user = User.objects.get(id=user_id)
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=request.user))
        ).order_by('-created_at').first()

        unread_count = Message.objects.filter(
            sender=other_user, receiver=request.user, is_read=False
        ).count()

        conversations_data.append({
            'user_id': other_user.id,
            'name': other_user.get_full_name(),
            'avatar': other_user.profile_picture.url if other_user.profile_picture else None,
            'last_message': last_message.content if last_message else "",
            'last_message_time': last_message.created_at.strftime('%H:%M') if last_message else "",
            'unread_count': unread_count,
            'is_online': False # Placeholder for online status
        })

    # Sort conversations by last message time
    conversations_data.sort(key=lambda x: x['last_message_time'], reverse=True)

    return JsonResponse({
        'conversations': conversations_data,
        'unread_count': sum(c['unread_count'] for c in conversations_data),
        'active_count': len(conversations_data)
    })

@login_required
def get_chat_data_ajax(request, user_id):
    """ AJAX call to get basic data for a chat recipient """
    other_user = get_object_or_404(User, id=user_id)
    return JsonResponse({
        'name': other_user.get_full_name(),
        'avatar': other_user.profile_picture.url if other_user.profile_picture else None,
        'is_online': False # Placeholder
    })

@login_required
def get_chat_messages_ajax(request, user_id):
    """ AJAX call to get all messages with a specific user """
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('created_at')

    # Mark as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'is_sender': msg.sender == request.user,
            'avatar': msg.sender.profile_picture.url if msg.sender.profile_picture else None,
            'created_at_formatted': msg.created_at.strftime('%H:%M')
        })

    return JsonResponse({'messages': messages_data})

@login_required
def clear_chat_ajax(request, user_id):
    """ AJAX call to clear conversation with a user """
    other_user = get_object_or_404(User, id=user_id)
    Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).delete()
    return JsonResponse({'success': True})

@login_required
def get_online_users_ajax(request):
    """ AJAX call to get online users (recent visits) """
    # Simple heuristic: users who visited in the last 15 minutes
    from datetime import timedelta
    from django.utils import timezone
    from jobapp.models import UserVisit
    
    recent_time = timezone.now() - timedelta(minutes=15)
    online_user_ids = UserVisit.objects.filter(timestamp__gt=recent_time).values_list('user_id', flat=True).distinct()
    online_users = User.objects.filter(id__in=online_user_ids).exclude(id=request.user.id)[:10]

    users_data = []
    for user in online_users:
        users_data.append({
            'id': user.id,
            'name': user.get_full_name(),
            'avatar': user.profile_picture.url if user.profile_picture else None,
            'role': user.role
        })

    return JsonResponse({'users': users_data})

@login_required
def get_post_comments_ajax(request, post_id):
    """ AJAX call to get comments for a post """
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('created_at')
    
    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'author_name': comment.user.get_full_name(),
            'author_profile_pic': comment.user.profile_picture.url if comment.user.profile_picture else None,
            'content': comment.content,
            'created_at_formatted': comment.created_at.strftime('%b %d, %H:%M')
        })
    
    return JsonResponse({'comments': comments_data})


@login_required
def get_notifications_list(request):
    """
    Get list of notifications for the notifications page
    """
    from datetime import timedelta
    
    notifications = []
    
    # 1. Connection Requests
    pending_requests = ConnectionRequest.objects.filter(receiver=request.user, status='pending').order_by('-created_at')
    for req in pending_requests:
        notifications.append({
            'type': 'connection_request',
            'id': req.id,
            'message': f"{req.sender.get_full_name()} sent you a connection request.",
            'created_at': req.created_at.strftime('%b %d, %H:%M'),
            'timestamp': req.created_at.timestamp(),
            'is_read': False, # Requests are effectively unread until acted upon
            'link': reverse('account:network')
        })

    # 2. Unread Messages (Grouped by sender)
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False).values('sender').distinct()
    for item in unread_messages:
        sender_id = item['sender']
        try:
            sender = User.objects.get(id=sender_id)
            count = Message.objects.filter(receiver=request.user, sender=sender, is_read=False).count()
            last_msg = Message.objects.filter(receiver=request.user, sender=sender, is_read=False).order_by('-created_at').first()
            
            notifications.append({
                'type': 'message',
                'id': last_msg.id,
                'message': f"You have {count} unread message(s) from {sender.get_full_name()}.",
                'created_at': last_msg.created_at.strftime('%b %d, %H:%M'),
                'timestamp': last_msg.created_at.timestamp(),
                'is_read': False,
                'link': reverse('account:messages')
            })
        except User.DoesNotExist:
            continue
        
    # 3. Recent Likes (Last 7 days)
    recent = datetime.now() - timedelta(days=7)
    recent_likes = Like.objects.filter(post__author=request.user, created_at__gt=recent).exclude(user=request.user).order_by('-created_at')
    for like in recent_likes:
        notifications.append({
            'type': 'like',
            'id': like.id,
            'message': f"{like.user.get_full_name()} liked your post.",
            'created_at': like.created_at.strftime('%b %d, %H:%M'),
            'timestamp': like.created_at.timestamp(),
            'is_read': True, # We don't track read status for likes yet
            'link': reverse('account:posts') 
        })
        
    # 4. Recent Comments
    recent_comments = Comment.objects.filter(post__author=request.user, created_at__gt=recent).exclude(user=request.user).order_by('-created_at')
    for comment in recent_comments:
        notifications.append({
            'type': 'comment',
            'id': comment.id,
            'message': f"{comment.user.get_full_name()} commented on your post: \"{comment.content[:30]}...\"",
            'created_at': comment.created_at.strftime('%b %d, %H:%M'),
            'timestamp': comment.created_at.timestamp(),
            'is_read': True,
            'link': reverse('account:posts')
        })

    # Sort all by timestamp descending
    notifications.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return JsonResponse({'notifications': notifications})


@login_required
def recent_activity(request):
    """
    Get recent activity for sidebar
    """
    recent_activities = []
    
    # Get recent posts by people user follows
    following_users = request.user.following.values_list('following', flat=True)
    recent_posts = Post.objects.filter(author__in=following_users).order_by('-created_at')[:5]
    
    for post in recent_posts:
        recent_activities.append({
            'user_profile_pic': post.author.profile_picture.url if post.author.profile_picture else None,
            'text': f"{post.author.get_full_name()} shared a post: \"{post.content[:40]}...\"",
            'time': post.created_at.strftime('%H:%M')
        })
        
    return JsonResponse({'activities': recent_activities})


@login_required
def update_profile_picture_ajax(request):
    """
    AJAX profile picture update
    """
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Profile picture updated successfully!',
                'profile_picture': user.profile_picture.url if user.profile_picture else None,
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


