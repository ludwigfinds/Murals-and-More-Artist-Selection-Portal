import streamlit as st
import json
import os
import glob
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="NewBo City Market Mural Artist Submissions",
    page_icon="🎨",
    layout="wide"
)

SUBMISSIONS_DIR = "submissions"
APP_PASSWORD = "NewBoMural2026"  # Set your app access password here

def load_data():
    """Load all JSON files from the submissions directory."""
    submissions = {}
    if not os.path.exists(SUBMISSIONS_DIR):
        os.makedirs(SUBMISSIONS_DIR)
        
    # Read all .json files in the folder
    file_paths = glob.glob(os.path.join(SUBMISSIONS_DIR, "*.json"))
    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                s_id = os.path.basename(file_path).replace(".json", "")
                submissions[s_id] = data
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")
            
    return submissions

def save_data(s_id, data):
    """Save updates (like favorites or notes) back to the specific JSON file."""
    if not os.path.exists(SUBMISSIONS_DIR):
        os.makedirs(SUBMISSIONS_DIR)
    file_path = os.path.join(SUBMISSIONS_DIR, f"{s_id}.json")
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

    # Check primary work link for image format
    if work_link and isinstance(work_link, str):
        lower_wl = work_link.strip().lower().split('?')[0]
        if lower_wl.endswith(img_extensions) and work_link not in images_to_show:
            images_to_show.append(work_link)
        elif lower_wl.endswith(pdf_extensions) and work_link not in pdfs_to_show:
            pdfs_to_show.append(work_link)

    # Render Image Gallery
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

    # Render PDF Documents
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

    # Render Other Files
    if other_files:
        st.markdown("### 📁 Additional Documents & Links")
        for idx, file_url in enumerate(other_files):
            filename = file_url.split('/')[-1]
            st.markdown(f"- 🔗 [{filename}]({file_url})")
        st.markdown("---")

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "nav"
if "active_submission_id" not in st.session_state:
    st.session_state.active_submission_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "filter_favorites" not in st.session_state:
    st.session_state.filter_favorites = False

# 1. Password Protection Gate with Mandatory Reviewer Name
if not st.session_state.authenticated:
    st.title("🔒 NewBo City Market Artist Selection Committee")
    st.subheader("Protected Access")
    
    name_input = st.text_input("Reviewer Name", value=st.session_state.user_name, placeholder="e.g. Jane Doe")
    pwd_input = st.text_input("Enter Committee Password", type="password")
    
    if st.button("Log In"):
        if not name_input.strip():
            st.error("Please enter your name to proceed.")
        elif pwd_input != APP_PASSWORD:
            st.error("Incorrect password. Please try again.")
        else:
            st.session_state.user_name = name_input.strip()
            st.session_state.authenticated = True
            st.success(f"Welcome, {st.session_state.user_name}! Access Granted.")
            st.rerun()
    st.stop()

# Load submissions data
submissions = load_data()

# Sidebar Controls
st.sidebar.title("🎨 Reviewer Panel")
st.session_state.user_name = st.sidebar.text_input("Reviewer Name", value=st.session_state.user_name)
st.sidebar.markdown("---")
st.session_state.filter_favorites = st.sidebar.checkbox("⭐ Show Favorites Only", value=st.session_state.filter_favorites)

if st.sidebar.button("🔒 Log Out"):
    st.session_state.authenticated = False
    st.session_state.current_view = "nav"
    st.session_state.active_submission_id = None
    st.rerun()

# 2. Page Navigation Handling
if st.session_state.current_view == "nav" or not st.session_state.active_submission_id:
    st.title("NewBo City Market - Artist Submissions")
    st.caption(f"Showing entries automatically loaded from the `{SUBMISSIONS_DIR}/` directory.")

    # Filter submissions
    filtered_keys = []
    sorted_keys = sorted(submissions.keys(), key=lambda x: int(x) if x.isdigit() else x)
    
    for k in sorted_keys:
        v = submissions[k]
        if st.session_state.filter_favorites:
            if v.get("is_favorite", False):
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
                fav_icon = "⭐" if item.get("is_favorite", False) else "☆"
                notes_cnt = len(item.get("notes_list", []))
                files_cnt = len(item.get("files", []))
                
                st.markdown(f"### #{key}. {item['name']}")
                st.write(f"{item['statement'][:100]}...")
                st.caption(f"Status: {fav_icon} Favorite | 💬 {notes_cnt} Notes | 📁 {files_cnt} Files")
                
                c1, c2 = st.columns([3, 1])
                if c1.button("View Submission", key=f"nav_to_{key}", use_container_width=True):
                    st.session_state.active_submission_id = key
                    st.session_state.current_view = "detail"
                    st.rerun()
                    
                if c2.button(fav_icon, key=f"fav_tile_{key}", use_container_width=True):
                    submissions[key]["is_favorite"] = not submissions[key].get("is_favorite", False)
                    save_data(key, submissions[key])
                    st.rerun()

else:
    # INDIVIDUAL SUBMISSION PAGE
    s_id = st.session_state.active_submission_id
    sub = submissions.get(s_id)
    
    if not sub:
        st.error("Submission not found.")
        if st.button("⬅ Back to Submissions List"):
            st.session_state.current_view = "nav"
            st.session_state.active_submission_id = None
            st.rerun()
        st.stop()

    if st.button("⬅ Back to Submissions List"):
        st.session_state.current_view = "nav"
        st.session_state.active_submission_id = None
        st.rerun()

    st.markdown("---")
    
    col_title, col_fav = st.columns([4, 1])
    with col_title:
        st.title(f"Submission #{s_id}: {sub['name']}")
        contact_info = []
        if sub.get("email"):
            contact_info.append(f"📧 {sub['email']}")
        if sub.get("phone"):
            contact_info.append(f"📞 {sub['phone']}")
        if contact_info:
            st.caption(" | ".join(contact_info))
            
    with col_fav:
        is_fav = sub.get("is_favorite", False)
        fav_label = "⭐ Favorited" if is_fav else "☆ Add to Favorites"
        if st.button(fav_label, key="page_fav_btn", use_container_width=True):
            submissions[s_id]["is_favorite"] = not is_fav
            save_data(s_id, submissions[s_id])
            st.rerun()

    st.markdown("### Artist Statement")
    st.info(sub["statement"])
    
    st.markdown("### Portfolio & Work Links")
    work_link = sub.get("work_link", "")
    if work_link:
        st.markdown(f"**Primary Online Portfolio:** 🔗 [{work_link}]({work_link})")
    
    st.markdown("---")
    
    # Render all submission files & artwork gallery
    render_submission_gallery(sub.get("files", []), work_link)
    
    # Real-time Shared Reviewer Notes
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
            current_data = load_data()
            entry = {
                "author": st.session_state.user_name,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "text": new_note.strip()
            }
            current_data[s_id].setdefault("notes_list", []).append(entry)
            save_data(s_id, current_data[s_id])
            st.success("Note saved for all reviewers!")
            st.rerun()
