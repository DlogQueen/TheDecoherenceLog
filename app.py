import streamlit as st
import time, random, os
from utils import load_css, render_glass_card, get_logo_html, render_void_intro, observer_ai, render_terminal_boot
import auth, database

st.set_page_config(page_title="DECOHERENCE LOG", page_icon="assets/logo.png", layout="wide", initial_sidebar_state="expanded")
database.init_db()
load_css()

if 'initialized' not in st.session_state: st.session_state['initialized'] = False
if 'page' not in st.session_state: st.session_state['page'] = 'feed'
if 'dm_target' not in st.session_state: st.session_state['dm_target'] = None

def sidebar_nav():
    with st.sidebar:
        st.image("assets/logo.png", width=120)
        st.markdown("""<div style="margin-bottom: 20px; font-size: 0.8em; color: #00f2ff; font-family: 'Share Tech Mono';">TRACKING THE GLITCHES<br>IN OUR REALITY</div>""", unsafe_allow_html=True)
        
        with st.form("search_form"):
            query = st.text_input("Search the Void...", key="search_input", label_visibility="collapsed", placeholder="Search the Void...")
            if st.form_submit_button("SEARCH"):
                st.session_state['page'] = 'search'
                st.session_state['search_query'] = query
                st.rerun()

        st.markdown("### 📡 NEURAL LINK")
        user = auth.get_current_user()
        unread_notifications = [n for n in database.get_notifications(user['id']) if not n['read']]

        if st.button("GLOBAL FEED", use_container_width=True): st.session_state['page'] = 'feed'; st.rerun()
        if st.button("MY PROFILE", use_container_width=True): st.session_state['page'] = 'profile'; st.rerun()
        if st.button("MESSENGER", use_container_width=True): st.session_state['page'] = 'messenger'; st.rerun()
        if st.button(f"NOTIFICATIONS ({len(unread_notifications)})", use_container_width=True): st.session_state['page'] = 'notifications'; st.rerun()
        if st.button("THE FOLD (AI)", use_container_width=True): st.session_state['page'] = 'fold'; st.rerun()
        if st.button("GROUPS", use_container_width=True): st.session_state['page'] = 'groups'; st.rerun()
        st.markdown("---")
        st.markdown("### 💎 SUPPORT RESEARCH")
        st.link_button("PAYPAL", "https://www.paypal.me/QuantumQueenDLog")
        st.link_button("VENMO", "https://account.venmo.com/u/kosmicqueen13")
        st.link_button("CASHAPP", "https://cash.app/$echosandwhispers")
        st.markdown("---")
        if st.button("LOGOUT", use_container_width=True): auth.logout_user(); st.rerun()
    render_footer()

def render_footer():
    st.markdown("---")
    st.markdown("""<div style="text-align: center; font-size: 0.7em; color: #444;">© 2026 THE DECOHERENCE LOG. ALL RIGHTS RESERVED.</div>""", unsafe_allow_html=True)

def app_bar():
    c1, c2 = st.columns([3, 1])
    with c1: st.markdown(f"""<div style="display: flex; align-items: center;">{get_logo_html(40)}<span style="margin-left:10px; color:#00f2ff; font-weight:bold;">DECOHERENCE LOG</span></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"<div style='text-align:right; color:#666;'>User: {auth.get_current_user().get('username')}</div>", unsafe_allow_html=True)
    st.markdown("---")

def feed_view():
    app_bar()
    c1, c2 = st.columns([3, 1])
    with c1: st.markdown('<h2 class="neon-cyan">GLOBAL ECHO CHAMBER</h2>', unsafe_allow_html=True)
    with c2: 
        if st.button("LOG NEW BREACH +", type="primary"): st.session_state['page'] = 'post'; st.rerun()
    
    posts = database.get_all_posts()
    for post in posts:
        with st.container():
            col_av, col_txt = st.columns([1, 10])
            with col_av: 
                user_info = database.get_user_by_id(post['user_id'])
                avatar = user_info.get('avatar') if user_info else None
                if avatar: st.image(avatar, width=40)
                else: st.markdown("👽")
            with col_txt:
                st.markdown(f"<span style='color:#00f2ff; font-weight:bold;'>@{post['username']}</span> <span style='color:#666; font-size:0.8em;'>{post['created_at']}</span>", unsafe_allow_html=True)
                st.write(post['status_text'])
                if post.get('media_path'): st.image(post['media_path'])
                if st.button(f"👁️ ACKNOWLEDGE ({post['protons']})", key=f"ack_{post['id']}"):
                    database.add_vote(auth.get_current_user()['id'], post['id'], "proton")
                    st.toast("VALIDATED."); st.rerun()

                st.markdown("---")
                comments = database.get_comments_for_post(post['id'])
                for comment in comments:
                    st.markdown(f"""
                        <div style='margin-left: 20px; border-left: 2px solid #333; padding-left: 10px; margin-top: 5px;'>
                            <span style='color:#00f2ff; font-weight:normal; font-size:0.9em;'>@{comment['username']}:</span> 
                            <span style='color:#ccc; font-size:0.9em;'>{comment['content']}</span>
                        </div>
                    """, unsafe_allow_html=True)

                with st.form(key=f"comment_form_{post['id']}", clear_on_submit=True):
                    comment_text = st.text_input("Add to the echo...", label_visibility="collapsed", placeholder="Add to the echo...")
                    submit_button = st.form_submit_button("TRANSMIT")

                    if submit_button and comment_text:
                        user = auth.get_current_user()
                        database.create_comment(post['id'], user['id'], user['username'], comment_text)
                        st.rerun()
    sidebar_nav()

def profile_view():
    app_bar()
    user = auth.get_current_user()
    db_user = database.get_user_by_id(user['id'])
    # Inject personal background (only for owner)
    personal_bg = database.get_user_background_b64(user['id'])
    if personal_bg:
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{personal_bg}") !important;
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="neon-cyan">IDENTITY ARCHIVE</h2>', unsafe_allow_html=True)
    settings = database.get_user_settings(user['id'])
    # If profile is private and viewer is not the owner, block
    if not settings["profile_public"] and auth.get_current_user()['id'] != user['id']:
        st.error("This user has cloaked their profile.")
        sidebar_nav(); return

    tab1, tab2, tab3, tab4 = st.tabs(["PROFILE", "FRIENDS", "EDIT", "🔒 PRIVACY"])
    
    with tab1:
        c1, c2 = st.columns([1, 3])
        with c1: 
            if db_user.get('avatar'): st.image(db_user['avatar'])
            else: st.image("https://via.placeholder.com/150/00f2ff/000000?text=AGENT")
        with c2:
            st.title(db_user['username'])
            st.info(db_user.get('bio', 'No bio transmission.'))
            st.markdown(f"**Clearance:** {db_user['role']}")

        if settings["show_activity"]:
            st.markdown("---")
            st.subheader("USER'S LOGS")
            user_posts = database.get_posts_by_user(user['id'])
            if not user_posts:
                st.caption("No breaches logged.")
            for post in user_posts:
                with st.container():
                    st.markdown(f"<span style='color:#666; font-size:0.8em;'>{post['created_at']}</span>", unsafe_allow_html=True)
                    st.write(post['status_text'])
                    if post.get('media_path'): st.image(post['media_path'])
                    st.markdown("---")
        else:
            st.info("Activity feed is hidden by quantum shield.")
            
    with tab2:
        st.subheader("FRIEND REQUESTS")
        reqs = database.get_pending_requests(user['id'])
        if not reqs: st.caption("No incoming signals.")
        for r in reqs:
            c1, c2 = st.columns([3, 1])
            with c1: st.write(f"Signal from **{r['username']}**")
            with c2: 
                if st.button("ACCEPT", key=f"acc_{r['id']}"): database.accept_friend(r['id']); st.rerun()
        
        st.subheader("ALLIES")
        friends = database.get_friends(user['id'])
        for f in friends:
            if st.button(f"MESSAGE {f['username']}", key=f"msg_{f['id']}"):
                st.session_state['dm_target'] = f
                st.session_state['page'] = 'messenger'
                st.rerun()
        
        st.subheader("ADD ALLY")
        target = st.text_input("Enter Codename to Connect")
        if st.button("SEND REQUEST"):
            st.info("Searching frequency...")
            
    with tab3:
        new_bio = st.text_area("Update Bio", db_user.get('bio', ''))
        avatar_file = st.file_uploader("Upload Avatar (JPG/PNG)", type=['jpg', 'png'])
        bg_file = st.file_uploader("Upload Personal Background (JPG)", type=['jpg'], help="Replaces background only on your profile.")
        if st.button("SAVE IDENTITY"):
            if avatar_file:
                database.update_profile(user['id'], new_bio, avatar_file)
            if bg_file:
                database.update_user_background(user['id'], bg_file)
                st.success("Background uploaded — reload profile to see.")
            if not avatar_file and not bg_file:
                database.update_profile(user['id'], new_bio, db_user.get('avatar', ''))
            st.success("PROFILE UPDATED."); time.sleep(1); st.rerun()

    # ---------- PRIVACY TAB ----------
    settings = database.get_user_settings(user['id'])
    with st.tab("🔒 PRIVACY"):
        st.markdown("### QUANTUM SHIELDS")
        col1, col2 = st.columns(2)
        with col1:
            pub = st.checkbox("Profile visible to public", value=settings["profile_public"])
            act = st.checkbox("Show activity feed", value=settings["show_activity"])
        with col2:
            dms = st.checkbox("Allow direct messages", value=settings["allow_dms"])
            mail = st.checkbox("Email notifications", value=settings["email_notif"])
        if st.button("SAVE PRIVACY"):
            database.update_user_setting(user['id'], "profile_public", pub)
            database.update_user_setting(user['id'], "show_activity", act)
            database.update_user_setting(user['id'], "allow_dms", dms)
            database.update_user_setting(user['id'], "email_notif", mail)
            st.success("Privacy matrix updated.")
            time.sleep(1); st.rerun()

    sidebar_nav()

def messenger_view():
    app_bar()
    target = st.session_state.get('dm_target')
    if not target:
        st.error("SELECT A TARGET FROM FRIENDS LIST FIRST.")
        if st.button("BACK TO PROFILE"): st.session_state['page'] = 'profile'; st.rerun()
        sidebar_nav(); return

    st.markdown(f'<h2 class="neon-cyan">ENCRYPTED CHANNEL: {target["username"]}</h2>', unsafe_allow_html=True)
    msgs = database.get_messages(auth.get_current_user()['id'], target['id'])
    for m in msgs:
        align = "right" if m['sender_id'] == auth.get_current_user()['id'] else "left"
        color = "#004444" if align == "right" else "#222"
        st.markdown(f"<div style='text-align:{align};'><span style='background:{color}; padding:8px; border-radius:5px; display:inline-block;'>{m['content']}</span></div>", unsafe_allow_html=True)
        
    with st.form("dm_form", clear_on_submit=True):
        txt = st.text_input("Transmission...")
        if st.form_submit_button("SEND") and txt:
            database.send_message(auth.get_current_user()['id'], target['id'], txt)
            st.rerun()
    sidebar_nav()

def post_view():
    st.markdown('<h2 class="neon-cyan">LOG NEW BREACH</h2>', unsafe_allow_html=True)
    with st.form("breach"):
        stat = st.text_area("STATUS")
        media = st.file_uploader("EVIDENCE", type=['jpg', 'png'])
        tags = st.text_input("TAGS")
        if st.form_submit_button("POST"):
            if stat:
                user = auth.get_current_user()
                # Pass FILE OBJECT to database function
                database.create_post(user['id'], user['username'], stat, media, tags)
                st.success("POSTED"); time.sleep(1); st.session_state['page']='feed'; st.rerun()
            else: st.error("TEXT REQUIRED")
    sidebar_nav()

def fold_view():
    st.markdown('<h2 class="neon-cyan">THE FOLD (AI)</h2>', unsafe_allow_html=True)
    render_glass_card("<h3>THE OBSERVER AI</h3>")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages: st.chat_message(m["role"]).markdown(m["content"])
    if p := st.chat_input("Query..."):
        st.chat_message("user").markdown(p); st.session_state.messages.append({"role": "user", "content": p})
        r = observer_ai.get_response(p)
        st.chat_message("assistant").markdown(r); st.session_state.messages.append({"role": "assistant", "content": r})
    sidebar_nav()

def admin_view():
    app_bar(); st.markdown('<h2 class="warning-red">ARCHITECT DASHBOARD</h2>', unsafe_allow_html=True)
    if st.button("EXIT"): st.session_state['page'] = 'feed'; st.rerun()
    for post in database.get_reported_posts():
        st.error(f"POST #{post['id']} by {post['username']}: {post['status_text']}")
        if st.button("EXTERMINATE", key=f"del_{post['id']}"): database.update_post_status(post['id'], "deleted"); st.rerun()
    sidebar_nav()

def notifications_view():
    app_bar()
    st.markdown('<h2 class="neon-cyan">NOTIFICATIONS</h2>', unsafe_allow_html=True)
    user = auth.get_current_user()

    notifications = database.get_notifications(user['id'])
    if not notifications:
        st.caption("No new alerts in the system.")
    
    for notif in notifications:
        col1, col2 = st.columns([4,1])
        with col1:
            st.markdown(f"<div style='border-left: 2px solid #00f2ff; padding-left: 10px; margin-top: 5px; opacity: {'1' if not notif['read'] else '0.5'};'>" +
                        f"<span style='color:#ccc;'>{notif['text']}</span><br>" +
                        f"<span style='font-size: 0.8em; color: #666;'>{notif['created_at']}</span>" +
                        "</div>", unsafe_allow_html=True)
        with col2:
            if not notif['read']:
                st.markdown("<span style='color: #00f2ff; font-size: 0.8em;'>UNREAD</span>", unsafe_allow_html=True)

    if any(not n['read'] for n in notifications):
        database.mark_notifications_as_read(user['id'])
    
    sidebar_nav()

def search_view():
    query = st.session_state.get('search_query', '')
    app_bar()
    st.markdown(f'<h2 class="neon-cyan">SEARCH RESULTS FOR: "{query}"</h2>', unsafe_allow_html=True)

    if not query:
        st.warning("Please enter a search query in the sidebar.")
        sidebar_nav()
        return

    # Search for posts and users
    posts = database.search_posts(query)
    users = database.search_users(query)

    tab1, tab2 = st.tabs([f"POSTS ({len(posts)})", f"USERS ({len(users)})"])

    with tab1:
        st.subheader("Matching Posts")
        if not posts:
            st.caption("No matching breaches found in the log.")
        for post in posts:
            with st.container():
                st.markdown(f"**@{post['username']}** - <span style='color:#666; font-size:0.8em;'>{post['created_at']}</span>", unsafe_allow_html=True)
                st.write(post['status_text'])
                if post.get('media_path'): st.image(post['media_path'])
                st.markdown("---")
    
    with tab2:
        st.subheader("Matching Agents")
        if not users:
            st.caption("No matching agents found.")
        for user in users:
            c1, c2, c3 = st.columns([1,3,1])
            with c1:
                if user.get('avatar'): st.image(user['avatar'], width=60)
                else: st.markdown("👤")
            with c2:
                st.markdown(f"**@{user['username']}**")
            with c3:
                # Could add a "View Profile" or "Add Friend" button here later
                pass
    
    sidebar_nav()

def groups_view():
    app_bar()
    st.markdown('<h2 class="neon-cyan">GROUPS & COMMUNITIES</h2>', unsafe_allow_html=True)
    user = auth.get_current_user()

    st.subheader("Create a New Group")
    with st.form("new_group_form", clear_on_submit=True):
        group_name = st.text_input("Group Name")
        group_desc = st.text_area("Description")
        if st.form_submit_button("CREATE GROUP"):
            if group_name:
                database.create_group(group_name, group_desc, user['id'])
                st.success(f"Group '{group_name}' created!")
                st.rerun()
            else:
                st.error("Group name is required.")

    st.markdown("---")
    st.subheader("Browse Groups")
    all_groups = database.get_all_groups()
    if not all_groups:
        st.caption("No groups have been formed yet. Be the first!")

    for group in all_groups:
        with st.container():
            c1, c2 = st.columns([3,1])
            with c1:
                st.markdown(f"**{group['name']}**")
                st.caption(group['description'])
            with c2:
                if st.button("VIEW", key=f"view_group_{group['id']}", use_container_width=True):
                    st.session_state['page'] = 'group_page'
                    st.session_state['current_group_id'] = group['id']
                    st.rerun()

def group_page_view():
    app_bar()
    group_id = st.session_state.get('current_group_id')
    if not group_id:
        st.error("No group selected.")
        return

    group = database.get_group_by_id(group_id)
    user = auth.get_current_user()
    members = database.get_group_members(group_id)
    member_ids = [m['user_id'] for m in members]

    st.markdown(f'<h2 class="neon-cyan">{group["name"]}</h2>', unsafe_allow_html=True)
    st.caption(group['description'])

    if user['id'] not in member_ids:
        if st.button("JOIN GROUP"):
            database.join_group(group_id, user['id'])
            st.rerun()
    else:
        st.success("You are a member of this group.")

    tab1, tab2 = st.tabs(["POSTS", f"MEMBERS ({len(member_ids)})" ])

    with tab1:
        st.subheader("Group Feed")
        with st.form("new_group_post_form", clear_on_submit=True):
            post_content = st.text_area("Post to the group")
            if st.form_submit_button("SUBMIT POST"):
                if post_content:
                    database.create_group_post(group_id, user['id'], user['username'], post_content)
                    st.rerun()
        
        st.markdown("---")
        group_posts = database.get_group_posts(group_id)
        for post in group_posts:
            st.markdown(f"**@{post['username']}** - <span style='color:#666; font-size:0.8em;'>{post['created_at']}</span>", unsafe_allow_html=True)
            st.write(post['content'])
            st.markdown("---")

    with tab2:
        st.subheader("Members")
        for member_id in member_ids:
            member_user = database.get_user_by_id(member_id['user_id'])
            if member_user:
                st.markdown(f"- @{member_user['username']}")

    sidebar_nav()


def fold_layer_view():
    render_void_intro()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("INITIALIZE SYSTEM_", use_container_width=True):
            with st.spinner("DECRYPTING REALITY..."):
                time.sleep(1.5); st.session_state['initialized'] = True; st.rerun()
    render_footer()

def login_view():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        render_glass_card("""<h2 class="neon-cyan" style="text-align: center;">SECURITY CLEARANCE</h2>""")
        tab1, tab2 = st.tabs(["LOGIN", "REQUEST ACCESS"])
        with tab1:
            with st.form("login"):
                u = st.text_input("CODENAME"); p = st.text_input("PASSPHRASE", type="password")
                if st.form_submit_button("ENTER"):
                    ud = auth.verify_login(u.lower(), p)
                    if ud: auth.login_user(ud); st.rerun()
                    else: st.error("DENIED")
        with tab2:
            with st.form("reg"):
                u = st.text_input("NEW NAME"); p = st.text_input("NEW PASS", type="password"); e = st.text_input("EMAIL")
                if st.form_submit_button("JOIN"):
                    if auth.register_new_user(u.lower(), p, e): 
                        st.success("CREATED. LOGGING IN..."); 
                        ud = auth.verify_login(u.lower(), p)
                        auth.login_user(ud)
                        time.sleep(1); st.rerun()
                    else: st.error("TAKEN")
    render_footer()

# --- MAIN CONTROLLER ---
if not st.session_state['initialized']: fold_layer_view()
else:
    if not auth.check_auth(): login_view()
    else:
        pg = st.session_state['page']
        if pg == 'feed': feed_view()
        elif pg == 'profile': profile_view()
        elif pg == 'messenger': messenger_view()
        elif pg == 'post': post_view()
        elif pg == 'fold': fold_view()
        elif pg == 'admin': admin_view()
        elif pg == 'search': search_view()
        elif pg == 'notifications': notifications_view()
        elif pg == 'groups': groups_view()
        elif pg == 'group_page': group_page_view()
        else: feed_view()