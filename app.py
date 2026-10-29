import streamlit as st
import json
import os
import glob
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Murals & More Artist Selection Portal",
    page_icon="🎨",
    layout="wide"
)

# Base Directories and Files
BASE_DIR = "data"
SUBMISSIONS_DIR = "submissions"
USERS_FILE = os.path.join(BASE_DIR, "users.json")
PROJECTS_FILE = os.path.join(BASE_DIR, "projects.json")

# Ensure required directories exist
for directory in [BASE_DIR, SUBMISSIONS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# --- Data Management Functions ---

def load_users():
    if not os.path.exists(USERS_FILE):
        # Create default admin user if none exists
        default_users = {
            "admin": {
                "password": "adminpassword",
                "role": "admin",
                "assigned_projects": ["NewBo City Market Mural Project"]
            }
        }
        with open(USERS_FILE, "w") as f:
            json.dump(default_users, f, indent=4)
        return default_users
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users_data):
    with open(USERS_FILE, "w") as f:
        json.dump(users_data, f, indent=4)

def load_projects():
    if not os.path.exists(PROJECTS_FILE):
        # Default project
        default_projects = ["NewBo City Market Mural Project"]
        with open(PROJECTS_FILE, "w") as f:
            json.dump(default_projects, f, indent=4)
        return default_projects
    with open(PROJECTS_FILE, "r") as f:
        return json.load(f)

def save_projects(projects_data):
    with open(PROJECTS_FILE, "w") as f:
        json.dump(projects_data, f, indent=4)
    # Create a subfolder for new projects if it doesn't exist
    for p in projects_data:
        p_dir = os.path.join(SUBMISSIONS_DIR, p)
        if not os.path.exists(p_dir):
            os.makedirs(p_dir)

def load_project_submissions(project_name):
    """Load all JSON files from the specific project directory."""
    submissions = {}
    p_dir = os.path.join(SUBMISSIONS_DIR, project_name)
    if not os.path.exists(p_dir):
        os.makedirs(p_dir)
        
    file_paths = glob.glob(os.path.join(p_dir, "*.json"))
    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                s_id = os.path.basename(file_path).replace(".json", "")
                submissions[s_id] = data
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")
            
    return submissions

def save_submission(project_name, s_id, data):
    """Save updates (favorites/notes) back to the specific JSON file in the project folder."""
    p_dir = os.path.join(SUBMISSIONS_DIR, project_name)
    if not os.path.exists(p_dir):
        os.makedirs(p_dir)
    file_path = os.path.join(p_dir, f"{s_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def render_submission_gallery(files, work_link):
    """Display submission files in a clean visual gallery grid."""
    if isinstance(files, str):
        files = [files]
    elif not isinstance(files, list):
        files = []
        
    clean_files = [f.strip() for f in files if isinstance(f, str) and f.strip()]
    
    img_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
    pdf_extensions = ('.pdf',)
    
    images_to_show = []
    pdfs_to_show = []
    other_files = []

    for f in clean_files:
        lower_f = f.lower().split('?')[0]
        if lower_f.endswith(img_extensions):
            images_to_show.append(f)
        elif lower_f.endswith(pdf_extensions):
            pdfs_to_show.append(f)
        else:
            other_files.append(f)

    if work_link and isinstance(work_link, str):
        lower_wl = work_link.strip().lower().split('?')[0]
        if lower_wl.endswith(img_extensions) and work_link not in images_to_show:
            images_to_show.append(work_link)
        elif lower_wl.endswith(pdf_extensions) and work_link not in pdfs_to_show:
            pdfs_to_show.append(work_link)

    if images_to_show:
        st.markdown(f"### 🖼️ Artwork & Portfolio Gallery ({len(images_to_show)} Images)")
        cols_per_row = 3
        for i in range(0, len(images_to_show), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                idx = i + j
                if idx < len(images_to_show):
                    img_url = images_to_show[idx]
                    with cols[j]:
                        with st.container(border=True):
                            st.image(img_url, use_container_width=True, caption=f"Artwork #{idx+1}")
                            st.markdown(f"🔗 [View High-Res Image]({img_url})")
        st.markdown("---")

    if pdfs_to_show:
        st.markdown("### 📄 Submitted PDF Documents")
        for idx, pdf_url in enumerate(pdfs_to_show):
            filename = pdf_url.split('/')[-1]
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"📄 **Portfolio Document #{idx+1}:** `{filename}`")
            with c2:
                st.link_button(f"Open PDF #{idx+1}", pdf_url, use_container_width=True)
        st.markdown("---")

    if other_files:
        st.markdown("### 📁 Additional Documents & Links")
        for idx, file_url in enumerate(other_files):
            filename = file_url.split('/')[-1]
            st.markdown(f"- 🔗 [{filename}]({file_url})")
        st.markdown("---")

# --- Session State Initialization ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "assigned_projects" not in st.session_state:
    st.session_state.assigned_projects = []
if "active_project" not in st.session_state:
    st.session_state.active_project = None
if "current_view" not in st.session_state:
    st.session_state.current_view = "nav"
if "active_submission_id" not in st.session_state:
    st.session_state.active_submission_id = None
if "filter_favorites" not in st.session_state:
    st.session_state.filter_favorites = False

users_db = load_users()
projects_db = load_projects()
save_projects(projects_db) # Ensure project directories are created

# --- 1. Login Gate ---
if not st.session_state.authenticated:
    st.title("🔒 Murals & More Artist Selection Portal")
    st.subheader("Protected Access")
    
    login_user = st.text_input("Username")
    login_pwd = st.text_input("Password", type="password")
    
    if st.button("Log In"):
        if login_user in users_db and users_db[login_user]["password"] == login_pwd:
            st.session_state.username = login_user
            st.session_state.role = users_db[login_user]["role"]
            st.session_state.assigned_projects = users_db[login_user].get("assigned_projects", [])
            
            # Auto-assign the first available project if one exists
            if st.session_state.assigned_projects:
                st.session_state.active_project = st.session_state.assigned_projects[0]
                
            st.session_state.authenticated = True
            st.success(f"Welcome, {login_user}! Access Granted.")
            st.rerun()
        else:
            st.error("Invalid username or password.")
    st.stop()


# --- Sidebar Navigation ---
st.sidebar.title("🎨 Portal Dashboard")
st.sidebar.markdown(f"**User:** {st.session_state.username} ({st.session_state.role.capitalize()})")

# Project Selector
if st.session_state.assigned_projects:
    st.session_state.active_project = st.sidebar.selectbox(
        "📂 Active Project", 
        st.session_state.assigned_projects, 
        index=st.session_state.assigned_projects.index(st.session_state.active_project) if st.session_state.active_project in st.session_state.assigned_projects else 0
    )
else:
    st.sidebar.warning("You have no assigned projects.")

st.sidebar.markdown("---")

if st.session_state.role == "admin":
    if st.sidebar.button("⚙️ Admin Settings"):
        st.session_state.current_view = "admin"
        st.session_state.active_submission_id = None
        st.rerun()

if st.sidebar.button("🏠 Submissions Gallery"):
    st.session_state.current_view = "nav"
    st.session_state.active_submission_id = None
    st.rerun()

if st.session_state.current_view == "nav":
    st.session_state.filter_favorites = st.sidebar.checkbox("⭐ Show My Favorites Only", value=st.session_state.filter_favorites)

if st.sidebar.button("🔒 Log Out"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- Main Logic Routing ---

if st.session_state.current_view == "admin" and st.session_state.role == "admin":
    st.title("⚙️ Admin Settings & User Management")
    
    # Manage Projects
    st.subheader("Manage Projects")
    new_project_name = st.text_input("New Project Name")
    if st.button("Add Project"):
        if new_project_name and new_project_name not in projects_db:
            projects_db.append(new_project_name)
            save_projects(projects_db)
            # Auto assign admin to new project
            users_db[st.session_state.username]["assigned_projects"].append(new_project_name)
            save_users(users_db)
            st.success(f"Project '{new_project_name}' added successfully!")
            st.rerun()

    st.markdown("---")
    
    # Manage Users
    st.subheader("Invite / Manage Users")
    with st.form("add_user_form"):
        new_username = st.text_input("Username")
        new_password = st.text_input("Temporary Password")
        new_role = st.selectbox("Role", ["reviewer", "admin"])
        assign_projects = st.multiselect("Assign to Projects", projects_db)
        
        submitted = st.form_submit_button("Add/Update User")
        if submitted:
            if new_username and new_password:
                users_db[new_username] = {
                    "password": new_password,
                    "role": new_role,
                    "assigned_projects": assign_projects
                }
                save_users(users_db)
                st.success(f"User '{new_username}' saved successfully!")
            else:
                st.error("Username and Password are required.")

elif st.session_state.current_view == "nav" and st.session_state.active_project:
    st.title(f"{st.session_state.active_project} - Submissions")
    
    submissions = load_project_submissions(st.session_state.active_project)

    if not submissions:
        st.info("No submissions found for this project. Upload JSON files into the project's submission folder.")
    else:
        # Filter submissions
        filtered_keys = []
        sorted_keys = sorted(submissions.keys(), key=lambda x: int(x) if x.isdigit() else x)
        
        for k in sorted_keys:
            v = submissions[k]
            # Favorites are now stored per user in a list called 'favorited_by'
            favorited_by = v.get("favorited_by", [])
            is_fav = st.session_state.username in favorited_by
            
            if st.session_state.filter_favorites:
                if is_fav:
                    filtered_keys.append(k)
            else:
                filtered_keys.append(k)

        # Tile Grid Layout
        cols = st.columns(3)
        for idx, key in enumerate(filtered_keys):
            item = submissions[key]
            col = cols[idx % 3]
            
            with col:
                with st.container(border=True):
                    favorited_by = item.get("favorited_by", [])
                    is_fav = st.session_state.username in favorited_by
                    fav_icon = "⭐" if is_fav else "☆"
                    notes_cnt = len(item.get("notes_list", []))
                    files_cnt = len(item.get("files", []))
                    
                    st.markdown(f"### {item.get('name', 'Unknown Artist')}")
                    statement_preview = item.get('statement', '')[:100] + "..." if item.get('statement') else "No statement."
                    st.write(statement_preview)
                    st.caption(f"Status: {fav_icon} Favorited | 💬 {notes_cnt} Notes | 📁 {files_cnt} Files")
                    
                    c1, c2 = st.columns([3, 1])
                    if c1.button("Review", key=f"nav_to_{key}", use_container_width=True):
                        st.session_state.active_submission_id = key
                        st.session_state.current_view = "detail"
                        st.rerun()
                        
                    if c2.button(fav_icon, key=f"fav_tile_{key}", use_container_width=True):
                        if is_fav:
                            item["favorited_by"].remove(st.session_state.username)
                        else:
                            item.setdefault("favorited_by", []).append(st.session_state.username)
                        save_submission(st.session_state.active_project, key, item)
                        st.rerun()

elif st.session_state.current_view == "detail" and st.session_state.active_project and st.session_state.active_submission_id:
    s_id = st.session_state.active_submission_id
    project = st.session_state.active_project
    submissions = load_project_submissions(project)
    sub = submissions.get(s_id)
    
    if not sub:
        st.error("Submission not found.")
        st.button("⬅ Back to Submissions List", on_click=lambda: st.session_state.update({"current_view": "nav", "active_submission_id": None}))
        st.stop()

    if st.button("⬅ Back to Submissions List"):
        st.session_state.current_view = "nav"
        st.session_state.active_submission_id = None
        st.rerun()

    st.markdown("---")
    
    col_title, col_fav = st.columns([4, 1])
    with col_title:
        st.title(f"Artist: {sub.get('name', 'Unknown Artist')}")
        contact_info = []
        if sub.get("email"):
            contact_info.append(f"📧 {sub.get('email')}")
        if sub.get("phone"):
            contact_info.append(f"📞 {sub.get('phone')}")
        if contact_info:
            st.caption(" | ".join(contact_info))
            
    with col_fav:
        favorited_by = sub.get("favorited_by", [])
        is_fav = st.session_state.username in favorited_by
        fav_label = "⭐ Favorited by you" if is_fav else "☆ Add to My Favorites"
        if st.button(fav_label, key="page_fav_btn", use_container_width=True):
            if is_fav:
                sub["favorited_by"].remove(st.session_state.username)
            else:
                sub.setdefault("favorited_by", []).append(st.session_state.username)
            save_submission(project, s_id, sub)
            st.rerun()

    st.markdown("### Artist Statement")
    st.info(sub.get("statement", "No statement provided."))
    
    st.markdown("### Portfolio & Work Links")
    work_link = sub.get("work_link", "")
    if work_link:
        st.markdown(f"**Primary Online Portfolio:** 🔗 [{work_link}]({work_link})")
    
    st.markdown("---")
    
    render_submission_gallery(sub.get("files", []), work_link)
    
    st.subheader("💬 Shared Reviewer Notes")
    notes_list = sub.get("notes_list", [])
    
    if not notes_list:
        st.write("_No reviewer notes added yet._")
    else:
        for n in notes_list:
            st.warning(f"**{n['author']}** _({n['time']})_:\n\n{n['text']}")

    st.markdown("#### Add a Reviewer Note")
    with st.form(key=f"page_note_form_{s_id}"):
        new_note = st.text_area("Your Feedback / Note:")
        submitted = st.form_submit_button("Submit Note")
        
        if submitted and new_note.strip():
            # Reload to avoid race conditions
            current_subs = load_project_submissions(project)
            entry = {
                "author": st.session_state.username,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "text": new_note.strip()
            }
            current_subs[s_id].setdefault("notes_list", []).append(entry)
            save_submission(project, s_id, current_subs[s_id])
            st.success("Note saved and shared with the committee!")
            st.rerun()