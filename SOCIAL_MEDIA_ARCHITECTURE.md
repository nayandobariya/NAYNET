# Social Media Features Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         JOB PORTAL SOCIAL NETWORK                       │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      USER INTERFACE LAYER                        │  │
│  │                                                                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │  │
│  │  │   Posts    │  │  Messages  │  │  Network   │  │  Profile │  │  │
│  │  │   Feed     │  │  (Chat)    │  │  (Follow)  │  │  Page    │  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └──────────┘  │  │
│  │                                                                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │  │
│  │  │ Likes &    │  │  Comments  │  │ Connection │  │  Search  │  │  │
│  │  │ Reactions  │  │  System    │  │  Requests  │  │  Users   │  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └──────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      BUSINESS LOGIC LAYER                        │  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐    │  │
│  │  │              Django Views (account/views.py)            │    │  │
│  │  │                                                         │    │  │
│  │  │  • posts_view()           • messages_view()            │    │  │
│  │  │  • create_post_ajax()     • send_message()             │    │  │
│  │  │  • like_post()            • poll_messages()            │    │  │
│  │  │  • comment_post()         • network()                  │    │  │
│  │  │  • follow_user()          • search_users()             │    │  │
│  │  │  • unfollow_user()        • get_notifications()        │    │  │
│  │  └─────────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                       DATA MODEL LAYER                           │  │
│  │                                                                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │  │
│  │  │    User    │  │    Post    │  │   Follow   │  │  Message │  │  │
│  │  │            │  │            │  │            │  │          │  │  │
│  │  │ • email    │  │ • author   │  │ • follower │  │ • sender │  │  │
│  │  │ • role     │  │ • content  │  │ • following│  │ • receiver│ │  │
│  │  │ • profile  │  │ • image    │  │ • created  │  │ • content│  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └──────────┘  │  │
│  │                                                                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                │  │
│  │  │    Like    │  │  Comment   │  │ Connection │                │  │
│  │  │            │  │            │  │  Request   │                │  │
│  │  │ • user     │  │ • user     │  │ • sender   │                │  │
│  │  │ • post     │  │ • post     │  │ • receiver │                │  │
│  │  │ • created  │  │ • content  │  │ • status   │                │  │
│  │  └────────────┘  └────────────┘  └────────────┘                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      DATABASE LAYER                              │  │
│  │                                                                  │  │
│  │              MySQL Database (naynat)                             │  │
│  │                                                                  │  │
│  │  Tables:                                                         │  │
│  │  • custom_account_user                                           │  │
│  │  • account_post                                                  │  │
│  │  • account_like                                                  │  │
│  │  • account_comment                                               │  │
│  │  • account_follow                                                │  │
│  │  • account_message                                               │  │
│  │  • account_connectionrequest                                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Feature Flow Diagrams

### 1. Creating a Post Flow

```
User
  │
  ├─> Opens Posts Page (GET /account/posts/)
  │     │
  │     └─> Renders posts.html template
  │
  ├─> Types content & uploads image
  │
  ├─> Clicks "Share Post"
  │     │
  │     └─> AJAX POST to /account/posts/create/
  │           │
  │           ├─> create_post_ajax() view
  │           │     │
  │           │     ├─> Creates Post object
  │           │     │
  │           │     └─> Returns JSON response
  │           │
  │           └─> JavaScript adds post to feed
  │
  └─> Post appears in feed instantly
```

### 2. Messaging Flow

```
User A                                    User B
  │                                         │
  ├─> Opens Messages Page                  │
  │     │                                   │
  │     └─> GET /account/messages/          │
  │           │                             │
  │           └─> Loads conversations       │
  │                                         │
  ├─> Selects User B                        │
  │     │                                   │
  │     └─> AJAX GET chat messages          │
  │                                         │
  ├─> Types message                         │
  │                                         │
  ├─> Sends message                         │
  │     │                                   │
  │     └─> AJAX POST /account/messages/send/<user_id>/
  │           │                             │
  │           ├─> Creates Message object    │
  │           │                             │
  │           └─> Returns success           │
  │                                         │
  │                                         ├─> Polling detects new message
  │                                         │     │
  │                                         │     └─> AJAX GET /account/messages/poll/<user_id>/
  │                                         │           │
  │                                         │           └─> Returns new messages
  │                                         │
  │                                         └─> Message appears in chat
```

### 3. Following Flow

```
User A                                    User B
  │                                         │
  ├─> Views User B's profile                │
  │                                         │
  ├─> Clicks "Follow"                       │
  │     │                                   │
  │     └─> AJAX POST /account/follow/<user_id>/
  │           │                             │
  │           ├─> Creates Follow object     │
  │           │   (follower=A, following=B) │
  │           │                             │
  │           └─> Returns success           │
  │                                         │
  ├─> Button changes to "Unfollow"          │
  │                                         │
  ├─> User B's posts appear in A's feed     │
  │                                         │
  │                                         └─> User B's follower count increases
```

### 4. Like & Comment Flow

```
User
  │
  ├─> Sees a post in feed
  │
  ├─> Clicks "Like" button
  │     │
  │     └─> AJAX POST /account/posts/<post_id>/like/
  │           │
  │           ├─> Creates/Deletes Like object
  │           │
  │           └─> Returns updated like count
  │                 │
  │                 └─> Updates UI instantly
  │
  ├─> Clicks "Comment" button
  │     │
  │     └─> Expands comment section
  │           │
  │           └─> AJAX GET /account/posts/<post_id>/comments/
  │                 │
  │                 └─> Loads all comments
  │
  ├─> Types comment
  │
  └─> Submits comment
        │
        └─> AJAX POST /account/posts/<post_id>/comments/create/
              │
              ├─> Creates Comment object
              │
              └─> Returns new comment
                    │
                    └─> Adds comment to list
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                 │
│                                                             │
│  • HTML5 (Templates)                                        │
│  • CSS3 (Modern styling with animations)                   │
│  • JavaScript (Vanilla JS for AJAX)                        │
│  • Bootstrap Icons / Font Awesome                           │
│  • AJAX for real-time updates                              │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND                                  │
│                                                             │
│  • Django 3.0+ (Web Framework)                              │
│  • Python 3.x                                               │
│  • Django ORM (Database abstraction)                        │
│  • Django Allauth (Authentication)                          │
│  • Django Channels (WebSocket support - optional)           │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE                                 │
│                                                             │
│  • MySQL (Primary database)                                 │
│  • SQLite (Fallback/Development)                            │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

### Posts API
```
GET    /account/posts/                    - View posts page
GET    /account/posts/feed/                - Get posts (AJAX)
POST   /account/posts/create/              - Create post (AJAX)
POST   /account/posts/<id>/like/           - Like/Unlike post
GET    /account/posts/<id>/comments/       - Get comments
POST   /account/posts/<id>/comments/create/ - Add comment
```

### Messages API
```
GET    /account/messages/                  - View messages page
GET    /account/messages/conversations/    - Get all conversations
GET    /account/messages/chat/<user_id>/   - Get chat data
GET    /account/messages/chat/<user_id>/messages/ - Get messages
POST   /account/messages/send/<user_id>/   - Send message
GET    /account/messages/poll/<user_id>/   - Poll new messages
GET    /account/messages/online-users/     - Get online users
POST   /account/messages/clear/<user_id>/  - Clear chat
```

### Network API
```
GET    /account/network/                   - View network page
GET    /account/network/ajax/              - Get network data
POST   /account/follow/<user_id>/          - Follow user
POST   /account/unfollow/<user_id>/        - Unfollow user
POST   /account/send-invite/<user_id>/     - Send connection request
POST   /account/accept-invite/<req_id>/    - Accept request
POST   /account/decline-invite/<req_id>/   - Decline request
GET    /account/connection-suggestions/ajax/ - Get suggestions
```

### Other APIs
```
GET    /account/search/people/             - Search users
GET    /account/notifications/             - View notifications
GET    /account/notifications/count/       - Get notification counts
```

## Data Relationships

```
User ──┬─── has many ───> Posts
       │
       ├─── has many ───> Likes
       │
       ├─── has many ───> Comments
       │
       ├─── has many ───> Messages (sent)
       │
       ├─── has many ───> Messages (received)
       │
       ├─── has many ───> Followers (Follow)
       │
       ├─── has many ───> Following (Follow)
       │
       └─── has many ───> Connection Requests

Post ──┬─── has many ───> Likes
       │
       └─── has many ───> Comments

Follow ─── connects ───> User (follower) to User (following)

Message ─── connects ───> User (sender) to User (receiver)

ConnectionRequest ─── connects ───> User (sender) to User (receiver)
```

## Security Measures

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
│                                                             │
│  1. Authentication                                          │
│     • @login_required decorators                            │
│     • Django Allauth integration                            │
│     • Session management                                    │
│                                                             │
│  2. Authorization                                           │
│     • User-specific data filtering                          │
│     • Permission checks in views                            │
│     • Role-based access (employee/employer)                 │
│                                                             │
│  3. CSRF Protection                                         │
│     • CSRF tokens in all forms                              │
│     • X-CSRFToken header in AJAX requests                   │
│                                                             │
│  4. XSS Prevention                                          │
│     • Django template auto-escaping                         │
│     • Content sanitization                                  │
│                                                             │
│  5. SQL Injection Prevention                                │
│     • Django ORM parameterized queries                      │
│     • No raw SQL queries                                    │
└─────────────────────────────────────────────────────────────┘
```

## Performance Optimizations

```
┌─────────────────────────────────────────────────────────────┐
│                    PERFORMANCE                              │
│                                                             │
│  1. Database                                                │
│     • Foreign key indexes                                   │
│     • Query optimization with select_related()             │
│     • Pagination for large datasets                         │
│                                                             │
│  2. Frontend                                                │
│     • AJAX for dynamic loading                              │
│     • Lazy loading of images                                │
│     • Debounced search inputs                               │
│     • Minimal DOM manipulation                              │
│                                                             │
│  3. Caching (Recommended)                                   │
│     • Redis for session storage                             │
│     • Cache frequently accessed data                        │
│     • Template fragment caching                             │
│                                                             │
│  4. Real-time Updates                                       │
│     • Polling (current: 5s for messages, 30s for notifs)   │
│     • WebSocket upgrade (recommended for production)        │
└─────────────────────────────────────────────────────────────┘
```

---

**This architecture provides a scalable, secure, and performant social networking platform integrated with your job portal!**
