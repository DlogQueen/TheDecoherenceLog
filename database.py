import os
from supabase import create_client, Client
import datetime
import hashlib
import time

# SUPABASE CONFIG
SUPABASE_URL = "https://fbllkfwjzsbprfpxmsfa.supabase.co"
SUPABASE_KEY = "sb_publishable_HlaJ3kr_1uPCIuOQfFKhiA_4wUXuTsH" # Use ANON key here

# Initialize Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db(): pass

# --- STORAGE ---
def upload_file(file_obj, bucket="evidence"):
    """Uploads a file object to Supabase Storage and returns public URL"""
    try:
        # Create unique filename: timestamp_filename
        filename = f"{int(time.time())}_{file_obj.name}"
        file_bytes = file_obj.getvalue()
        
        # Upload
        supabase.storage.from_(bucket).upload(filename, file_bytes, {"content-type": file_obj.type})
        
        # Get Public URL
        public_url = supabase.storage.from_(bucket).get_public_url(filename)
        return public_url
    except Exception as e:
        print(f"Upload Error: {e}")
        return None

# --- USER ---
def create_user(username, password, email):
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        data = { "username": username, "password_hash": pwd_hash, "email": email, "role": "user", "bio": "Observer.", "avatar": "" }
        response = supabase.table("users").insert(data).execute()
        return response.data[0]['id'] if response.data else None
    except: return None

def verify_user_credentials(username, password):
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        response = supabase.table("users").select("*").eq("username", username).eq("password_hash", pwd_hash).execute()
        return response.data[0] if response.data else None
    except: return None

def get_user_by_id(uid):
    try:
        response = supabase.table("users").select("*").eq("id", uid).execute()
        return response.data[0] if response.data else None
    except: return None

def update_profile(uid, bio, avatar_path_or_file):
    # Check if avatar is a file object (Upload it) or a string (URL)
    avatar_url = avatar_path_or_file
    if hasattr(avatar_path_or_file, 'getvalue'): 
        avatar_url = upload_file(avatar_path_or_file, "evidence") # Reusing evidence bucket for avatars for simplicity
        
    try: supabase.table("users").update({"bio": bio, "avatar": avatar_url}).eq("id", uid).execute()
    except: pass

# --- POSTS ---
def get_all_posts():
    try:
        response = supabase.table("posts").select("*").eq("status", "active").order("created_at", desc=True).execute()
        return response.data
    except: return []

def get_posts_by_user(user_id):
    """Retrieves all posts for a specific user."""
    try:
        response = supabase.table("posts").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data
    except:
        return []

# --- SEARCH ---
def search_posts(query):
    """Searches for posts containing the query in status_text or tags."""
    try:
        # Using or_ filter with ilike for case-insensitive search
        response = supabase.table("posts").select("*").or_(f"status_text.ilike.%{query}%,tags.ilike.%{query}%").eq("status", "active").execute()
        return response.data
    except Exception as e:
        print(f"Post search error: {e}")
        return []

def search_users(query):
    """Searches for users by username."""
    try:
        response = supabase.table("users").select("id, username, avatar").ilike("username", f"%{query}%").execute()
        return response.data
    except Exception as e:
        print(f"User search error: {e}")
        return []

# --- NOTIFICATIONS ---
def create_notification(user_id, notification_type, text, link):
    """Creates a notification for a user."""
    try:
        data = {
            "user_id": user_id,
            "type": notification_type,
            "text": text,
            "link": link,
            "read": False
        }
        supabase.table("notifications").insert(data).execute()
    except Exception as e:
        print(f"Notification creation error: {e}")

def get_notifications(user_id):
    """Gets all notifications for a user."""
    try:
        response = supabase.table("notifications").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error getting notifications: {e}")
        return []

def mark_notifications_as_read(user_id):
    """Marks all notifications for a user as read."""
    try:
        supabase.table("notifications").update({"read": True}).eq("user_id", user_id).execute()
    except Exception as e:
        print(f"Error marking notifications as read: {e}")

def create_post(user_id, username, status, media_file, tags):
    # Upload media if exists
    media_url = ""
    if media_file:
        media_url = upload_file(media_file, "evidence")
        
    try:
        data = {
            "user_id": user_id, "username": username, "status_text": status,
            "media_path": media_url, "media_type": "image", "tags": tags,
            "protons": 0, "electrons": 0, "status": "active"
        }
        supabase.table("posts").insert(data).execute()
        return True
    except: return False

def add_vote(user_id, post_id, vote_type):
    try:
        supabase.table("votes").insert({"user_id": user_id, "post_id": post_id, "vote_type": vote_type}).execute()
        post = supabase.table("posts").select("protons").eq("id", post_id).execute().data[0]
        supabase.table("posts").update({"protons": post['protons'] + 1}).eq("id", post_id).execute()
    except: pass

# --- COMMENTS ---
def create_comment(post_id, user_id, username, content):
    """Creates a new comment on a post."""
    try:
        data = {
            "post_id": post_id,
            "user_id": user_id,
            "username": username,
            "content": content
        }
        supabase.table("comments").insert(data).execute()
        
        # Create notification for post author
        post_author_id = supabase.table('posts').select('user_id').eq('id', post_id).execute().data[0]['user_id']
        if post_author_id != user_id:
            create_notification(post_author_id, "new_comment", f"@{username} commented on your post.", f"/post/{post_id}")
        return True
    except Exception as e:
        print(f"Comment creation error: {e}")
        return False

def get_comments_for_post(post_id):
    """Retrieves all comments for a specific post."""
    try:
        response = supabase.table("comments").select("*").eq("post_id", post_id).order("created_at", desc=False).execute()
        return response.data
    except Exception as e:
        print(f"Error getting comments: {e}")
        return []

# --- GROUPS ---
def create_group(name, description, creator_id):
    """Creates a new group."""
    try:
        group_data = {"name": name, "description": description, "creator_id": creator_id}
        group = supabase.table("groups").insert(group_data).execute().data[0]
        # Automatically add creator as the first member
        supabase.table("group_members").insert({"group_id": group['id'], "user_id": creator_id, "role": "admin"}).execute()
        return group
    except Exception as e:
        print(f"Group creation error: {e}")
        return None

def get_all_groups():
    """Retrieves all groups."""
    try:
        return supabase.table("groups").select("*").execute().data
    except Exception as e:
        print(f"Error getting all groups: {e}")
        return []

def get_group_by_id(group_id):
    """Retrieves a single group by its ID."""
    try:
        return supabase.table("groups").select("*").eq("id", group_id).execute().data[0]
    except: return None

def join_group(group_id, user_id):
    """Adds a user to a group."""
    try:
        supabase.table("group_members").insert({"group_id": group_id, "user_id": user_id, "role": "member"}).execute()
        return True
    except: return False

def get_group_members(group_id):
    """Retrieves all members of a group."""
    try:
        return supabase.table("group_members").select("user_id").eq("group_id", group_id).execute().data
    except: return []

def create_group_post(group_id, user_id, username, content):
    """Creates a post within a group."""
    try:
        supabase.table("group_posts").insert({"group_id": group_id, "user_id": user_id, "username": username, "content": content}).execute()
        return True
    except: return False

def get_group_posts(group_id):
    """Retrieves all posts for a specific group."""
    try:
        return supabase.table("group_posts").select("*").eq("group_id", group_id).order("created_at", desc=True).execute().data
    except: return []

def get_user_groups(user_id):
    """Retrieves all groups a user is a member of."""
    try:
        group_ids = [gm['group_id'] for gm in supabase.table("group_members").select("group_id").eq("user_id", user_id).execute().data]
        if not group_ids:
            return []
        return supabase.table("groups").select("*").in_("id", group_ids).execute().data
    except: return []

# --- USER SETTINGS / PRIVACY ---
def get_user_settings(user_id):
    """Returns privacy settings for a user (creates row if missing)."""
    row = supabase.table("user_settings").select("*").eq("user_id", user_id).execute().data
    if not row:
        defaults = {
            "user_id": user_id,
            "profile_public": True,
            "show_activity": True,
            "allow_dms": True,
            "email_notif": False
        }
        supabase.table("user_settings").insert(defaults).execute()
        return defaults
    return row[0]

def update_user_setting(user_id, key, value):
    """Update a single privacy toggle."""
    supabase.table("user_settings").update({key: value}).eq("user_id", user_id).execute()

def update_user_background(user_id, file_obj):
    """Save uploaded background jpg as /assets/user_bg_<id>.jpg and return path."""
    path = f"assets/user_bg_{user_id}.jpg"
    with open(path, "wb") as f:
        f.write(file_obj.getbuffer())
    return path

def get_user_background_b64(user_id):
    """Return base-64 of user's custom bg (empty string if none)."""
    try:
        with open(f"assets/user_bg_{user_id}.jpg", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

# --- FRIENDS & MESSAGES (Simplified) ---
def send_friend_request(f, t):
    # Block if recipient disabled DMs
    settings = get_user_settings(t)
    if not settings.get("allow_dms", True):
        return False # report failure
    try: 
        supabase.table("friends").insert({"user_a": f, "user_b": t, "status": "pending"}).execute()
        sender_username = get_user_by_id(f)['username']
        create_notification(t, "friend_request", f"@{sender_username} sent you a friend request.", "/profile")
        return True
    except: return False

def accept_friend(rid):
    try: supabase.table("friends").update({"status": "accepted"}).eq("id", rid).execute()
    except: pass

def get_friends(uid):
    try:
        res = supabase.table("friends").select("*").eq("status", "accepted").execute()
        friends = []
        for r in res.data:
            tid = r['user_b'] if r['user_a'] == uid else r['user_a']
            u = get_user_by_id(tid)
            if u: friends.append(u)
        return friends
    except: return []

def get_pending_requests(uid):
    try:
        res = supabase.table("friends").select("id, user_a").eq("user_b", uid).eq("status", "pending").execute()
        reqs = []
        for r in res.data:
            u = get_user_by_id(r['user_a'])
            if u: reqs.append({"id": r['id'], "username": u['username']})
        return reqs
    except: return []

def send_message(s, r, c):
    # Block if recipient disabled DMs
    settings = get_user_settings(r)
    if not settings.get("allow_dms", True):
        return  # silently drop
    try: 
        supabase.table("messages").insert({"sender_id": s, "receiver_id": r, "content": c}).execute()
        sender_username = get_user_by_id(s)['username']
        create_notification(r, "new_message", f"@{sender_username} sent you a message.", "/messenger")
    except: pass

def get_messages(u1, u2):
    try:
        res = supabase.table("messages").select("*").order("timestamp", desc=False).execute()
        msgs = [m for m in res.data if (m['sender_id']==u1 and m['receiver_id']==u2) or (m['sender_id']==u2 and m['receiver_id']==u1)]
        return msgs
    except: return []

def check_for_entanglements(pid, tags): return []
def get_reported_posts(): return get_all_posts()
def update_post_status(pid, stat):
    try: supabase.table("posts").update({"status": stat}).eq("id", pid).execute()
    except: pass