import streamlit as st
import json
import os
import glob
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="NewBo Mural Artist Submissions",
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
                # Use the filename (without extension) as the key/ID if not specified
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

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "nav"
if "active_submission_id" not in st.session_state:
    st.session_state.active_submission_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = "Reviewer"
if "filter_favorites" not in st.session_state:
    st.session_state.filter_favorites = False

# 1. Password Protection Gate
if not st.session_state.authenticated:
    st.title("🔒 NewBo Artist Selection Committee")
    st.subheader("Protected Access")
    
    pwd_input = st.text_input("Enter Committee Password", type="password")
    if st.button("Log In"):
        if pwd_input == APP_PASSWORD:
            st.session_state.authenticated = True
            st.success("Access Granted!")
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    st.stop()

# Load submissions data
submissions = load_data()

# Sidebar Controls
st.sidebar.title("🎨 Reviewer Panel")
st.session_state.user_name = st.sidebar.text_input("Reviewer Name / Initials", value=st.session_state.user_name)
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
    # Sort keys to display sequentially if they are numbered
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
                
                st.markdown(f"### #{key}. {item['name']}")
                st.write(f"{item['statement'][:100]}...")
                st.caption(f"Status: {fav_icon} Favorite | 💬 {notes_cnt} Notes")
                
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
        if "email" in sub or "phone" in sub:
            st.caption(f"📧 {sub.get('email', 'N/A')} | 📞 {sub.get('phone', 'N/A')}")
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
    st.markdown(f"**Primary Link:** 🔗 [{sub['work_link']}]({sub['work_link']})")
    
    if "files" in sub and sub["files"]:
        st.markdown("**Additional Submitted Files:**")
        for f in sub["files"]:
            st.markdown(f"- 📄 [{f}]({f})")
    
    st.markdown("---")
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