import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURATION ---
UNIVERSAL_PASSWORD = "newbo-jury-2026"
DATA_FILE = "submissions.json"

st.set_page_config(page_title="NewBo City Market - Call for Artists Review", layout="wide")

# Custom CSS for Tile Cards & Styling
st.markdown("""
<style>
    .submission-tile {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s ease-in-out;
    }
    .submission-tile:hover {
        border-color: #2563eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .comment-box {
        background-color: #f1f5f9;
        border-left: 4px solid #2563eb;
        padding: 10px 14px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    .comment-header {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .comment-text {
        font-size: 0.95rem;
        color: #1e293b;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔒 NewBo Jury Portal")
        password = st.text_input("Enter the universal password:", type="password")
        reviewer_name = st.text_input("Your Name / Reviewer Initials (Optional):", value="Reviewer")
        
        if st.button("Log In", type="primary"):
            if password == UNIVERSAL_PASSWORD:
                st.session_state["password_correct"] = True
                st.session_state["reviewer_name"] = reviewer_name if reviewer_name.strip() else "Reviewer"
                st.rerun()
            else:
                st.error("Incorrect password.")
        return False
    return True

# --- DATA HANDLING (With Thread-Safe/File-Based Persisted Shared Notes) ---
def load_data():
    if not os.path.exists(DATA_FILE):
        st.error(f"Data file {DATA_FILE} not found. Please ensure submissions.json exists.")
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --- MAIN APP ---
if check_password():
    # Load freshest state from disk on every rerun
    data = load_data()

    if "selected_id" not in st.session_state:
        st.session_state["selected_id"] = "1"

    st.title("🎨 NewBo City Market - Call for Artists Reviewer")
    st.caption(f"Logged in as: **{st.session_state.get('reviewer_name', 'Reviewer')}** | Password-authenticated shared session")

    # Layout: Left column for Submission Tiles Navigation, Right column for Detailed Viewer & Notes
    col_nav, col_detail = st.columns([1, 2], gap="medium")

    # --- LEFT SIDE: TILE NAVIGATION GRID ---
    with col_nav:
        st.subheader("Submissions (29 Total)")
        
        # Grid layout for tiles
        tile_cols = st.columns(2)
        
        for idx, (sub_id, info) in enumerate(data.items()):
            col_target = tile_cols[idx % 2]
            with col_target:
                is_selected = (st.session_state["selected_id"] == sub_id)
                btn_type = "primary" if is_selected else "secondary"
                
                notes_count = len(info.get("notes_list", []))
                
                # Render Tile Button
                tile_label = f"#{sub_id} {info['name']}\n💬 {notes_count} Notes"
                if col_target.button(tile_label, key=f"tile_{sub_id}", use_container_width=True, type=btn_type):
                    st.session_state["selected_id"] = sub_id
                    st.rerun()

    # --- RIGHT SIDE: DETAILED VIEW & PERSISTED SHARED NOTES ---
    with col_detail:
        selected_id = st.session_state["selected_id"]
        artist = data.get(selected_id, {})

        if artist:
            st.markdown(f"## #{selected_id}. {artist.get('name', 'Unknown')}")
            
            # Artist Statement & Links Section
            with st.expander("📄 Artist Statement & Details", expanded=True):
                st.write(artist.get("statement", "No statement provided."))
                st.markdown("---")
                work_link = artist.get("work_link", "")
                if work_link:
                    st.markdown(f"🔗 **Portfolio Link:** [{work_link}]({work_link})")
                else:
                    st.info("No external portfolio link submitted.")

            # Shared Committee Notes Section
            st.markdown("### 📝 Shared Jury Notes")
            st.caption("Notes added here are saved directly to disk and visible to all logged-in reviewers.")

            # Load existing notes
            notes_list = artist.get("notes_list", [])
            
            # Display past notes in a clean feed
            if notes_list:
                for note_item in reversed(notes_list):
                    author = note_item.get("author", "Anonymous")
                    timestamp = note_item.get("timestamp", "")
                    text = note_item.get("text", "")
                    
                    st.markdown(f"""
                    <div class="comment-box">
                        <div class="comment-header">👤 {author} • {timestamp}</div>
                        <div class="comment-text">{text}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No notes recorded for this artist yet. Be the first to leave feedback!")

            # Add New Note Form
            st.markdown("#### Add a Note")
            new_note_text = st.text_area("Write your feedback or vote:", key=f"note_input_{selected_id}", height=120)
            
            if st.button("Submit Shared Note", type="primary"):
                if new_note_text.strip():
                    # Refresh data before appending to prevent overwrites from simultaneous users
                    current_data = load_data()
                    
                    if "notes_list" not in current_data[selected_id]:
                        current_data[selected_id]["notes_list"] = []
                        
                    current_data[selected_id]["notes_list"].append({
                        "author": st.session_state.get("reviewer_name", "Reviewer"),
                        "timestamp": datetime.now().strftime("%b %d, %Y - %I:%M %p"),
                        "text": new_note_text.strip()
                    })
                    
                    save_data(current_data)
                    st.toast("Note added and synced for all reviewers!", icon="🎉")
                    st.rerun()
                else:
                    st.warning("Please enter a note before submitting.")