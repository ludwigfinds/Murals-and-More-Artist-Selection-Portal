import streamlit as st
import json
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="NewBo Mural Artist Submissions",
    page_icon="🎨",
    layout="wide"
)

DATA_FILE = "submissions.json"
APP_PASSWORD = "NewBoMural2026"  # Set your app access password here

# Initialize default submissions dataset if file doesn't exist
DEFAULT_SUBMISSIONS = {
    "1": {
        "name": "Joseph Dulin-Didonato",
        "statement": "For six years, I've built an extensive portfolio of large scale murals, projects, gallery pieces, and commissions consistently delivering quality work on time. This piece should offer an exciting experience while showcasing images from Czech/ Bohemian history.",
        "work_link": "https://www.instagram.com/the_outside_artist/?hl=en",
        "notes_list": [],
        "is_favorite": False
    },
    "2": {
        "name": "Legacy Murals (Danielle Flicek & Matt Novak)",
        "statement": "Legacy Murals is built on over 25 years of artistic passion, transforming ordinary spaces into extraordinary works of art that inspire, connect, and leave a lasting impression.",
        "work_link": "https://www.legacymuralsmn.com",
        "notes_list": [],
        "is_favorite": False
    },
    "3": {
        "name": "Sena Ostrander",
        "statement": "I'm a Denver-based painter and muralist whose work explores human connection, identity, and storytelling through expressive figurative imagery, vibrant color, and layered compositions.",
        "work_link": "https://www.senaostrander.com",
        "notes_list": [],
        "is_favorite": False
    },
    "4": {
        "name": "Megan Roethler",
        "statement": "Since graduating UNI in 2020 with a BFA in painting, my work has expanded into a variety of creative outlets including small scale painting, digital rendering, murals, tattooing, and sculpture.",
        "work_link": "https://www.instagram.com/rat_toos",
        "notes_list": [],
        "is_favorite": False
    },
    "5": {
        "name": "Tacy Cummings",
        "statement": "Hey there, I'm Tacy Cummings, a mural artist based in Iowa. I'm all about color, texture, and making bold and vibrant statements through my art.",
        "work_link": "https://crmurals.org/wp-content/uploads/elementor/forms/6adf4fc289dec.pdf",
        "notes_list": [],
        "is_favorite": False
    },
    "6": {
        "name": "ANYTOWN MURAL & SIGN LLC (Michael Ferrarell)",
        "statement": "Michael Ferrarell is a Chicago-based muralist and sign painter whose artistic practice focuses heavily on site-responsive aesthetics.",
        "work_link": "https://www.instagram.com/anytownmuralandsign/",
        "notes_list": [],
        "is_favorite": False
    },
    "7": {
        "name": "Brandon Hogan",
        "statement": "I paint the moments a community needs to remember. My practice centers on large-scale murals and live event painting — work made in public, at the scale of the room it serves.",
        "work_link": "https://instagram.com/bhxartt",
        "notes_list": [],
        "is_favorite": False
    },
    "8": {
        "name": "Lauren Brunson",
        "statement": "I see my pieces as expressions of free will and intuitive artistic exploration. I work in experimental media and figurative shading to reflect human duality.",
        "work_link": "https://www.instagram.com/laurenrbrunson",
        "notes_list": [],
        "is_favorite": False
    },
    "9": {
        "name": "Kierim Visinhiriiev & ODVs Art Studio",
        "statement": "Kierim Visinhiriiev is collaborating with ODVs Art Studio (Toronto, Canada) for the NewBo City Market indoor mural, specializing in spray paint and airbrush large-scale murals.",
        "work_link": "https://odvsart.com",
        "notes_list": [],
        "is_favorite": False
    },
    "10": {
        "name": "David Neeld",
        "statement": "I make murals that read as one bold image from a distance and reward a closer look, crafted collaboratively with the community. I bring 23 years of engineering project management.",
        "work_link": "https://davidneeldstudio.com",
        "notes_list": [],
        "is_favorite": False
    },
    "11": {
        "name": "Jay Morgan (BLVD Murals)",
        "statement": "Jay Morgan is founder of BLVD Murals, an Austin-based studio with 15+ years of experience in large-scale commercial murals, public art, and architectural installations.",
        "work_link": "https://blvdmurals.com",
        "notes_list": [],
        "is_favorite": False
    },
    "12": {
        "name": "Amanda Stout",
        "statement": "For five years I have created public art that draws inspiration from environmental patterns and surrealist depictions of wildlife and nature.",
        "work_link": "https://astt8ec8.myportfolio.com/",
        "notes_list": [],
        "is_favorite": False
    }
}

# Fill remaining submissions up to 29 entries
for i in range(13, 30):
    idx_str = str(i)
    if idx_str not in DEFAULT_SUBMISSIONS:
        DEFAULT_SUBMISSIONS[idx_str] = {
            "name": f"Artist Submission #{i}",
            "statement": f"Portfolio entry and artist statement for submission #{i}.",
            "work_link": f"https://portfolio.artist{i}.com",
            "notes_list": [],
            "is_favorite": False
        }

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_SUBMISSIONS
    else:
        save_data(DEFAULT_SUBMISSIONS)
        return DEFAULT_SUBMISSIONS

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "nav"  # Options: 'nav' or 'detail'
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
    # ------------------ NAVIGATION PAGE ------------------
    st.title("NewBo City Market - Artist Submissions")
    st.caption("Select any submission tile below to view its dedicated page, links, and shared notes.")

    # Filter submissions
    filtered_keys = []
    for k, v in submissions.items():
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
                    save_data(submissions)
                    st.rerun()

else:
    # ------------------ INDIVIDUAL SUBMISSION PAGE ------------------
    s_id = st.session_state.active_submission_id
    sub = submissions.get(s_id)
    
    if not sub:
        st.error("Submission not found.")
        if st.button("⬅ Back to Submissions List"):
            st.session_state.current_view = "nav"
            st.session_state.active_submission_id = None
            st.rerun()
        st.stop()

    # Back button
    if st.button("⬅ Back to Submissions List"):
        st.session_state.current_view = "nav"
        st.session_state.active_submission_id = None
        st.rerun()

    st.markdown("---")
    
    # Header & Favorite Toggle
    col_title, col_fav = st.columns([4, 1])
    with col_title:
        st.title(f"Submission #{s_id}: {sub['name']}")
    with col_fav:
        is_fav = sub.get("is_favorite", False)
        fav_label = "⭐ Favorited" if is_fav else "☆ Add to Favorites"
        if st.button(fav_label, key="page_fav_btn", use_container_width=True):
            submissions[s_id]["is_favorite"] = not is_fav
            save_data(submissions)
            st.rerun()

    # Submission Details
    st.markdown("### Artist Statement")
    st.info(sub["statement"])
    
    st.markdown("### Portfolio & Work Link")
    st.markdown(f"🔗 [{sub['work_link']}]({sub['work_link']})")
    
    st.markdown("---")
    
    # Real-time Shared Notes
    st.subheader("💬 Shared Reviewer Notes")
    notes_list = sub.get("notes_list", [])
    
    if not notes_list:
        st.write("_No reviewer notes added yet._")
    else:
        for n in notes_list:
            st.warning(f"**{n['author']}** _({n['time']})_:\n\n{n['text']}")

    # Form to add a new note
    st.markdown("#### Add a Reviewer Note")
    with st.form(key=f"page_note_form_{s_id}"):
        new_note = st.text_area("Your Feedback / Note:")
        submitted = st.form_submit_button("Submit Note")
        
        if submitted and new_note.strip():
            # Reload fresh data to keep multi-user sync
            current_data = load_data()
            entry = {
                "author": st.session_state.user_name,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "text": new_note.strip()
            }
            current_data[s_id].setdefault("notes_list", []).append(entry)
            save_data(current_data)
            st.success("Note saved for all reviewers!")
            st.rerun()