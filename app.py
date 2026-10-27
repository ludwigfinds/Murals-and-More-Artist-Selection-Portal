import streamlit as st
import json
import os

# --- CONFIGURATION ---
UNIVERSAL_PASSWORD = "newbo-jury-2026"  # Change this to your preferred password
DATA_FILE = "submissions.json"

st.set_page_config(page_title="NewBo City Market - Call for Artists Review", layout="wide")

# --- AUTHENTICATION ---
def check_password():
    """Returns True if the user has entered the correct password."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔒 NewBo Jury Portal")
        password = st.text_input("Enter the universal password:", type="password")
        if st.button("Log In"):
            if password == UNIVERSAL_PASSWORD:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        return False
    return True

# --- DATA HANDLING ---
def load_data():
    if not os.path.exists(DATA_FILE):
        st.error(f"Data file {DATA_FILE} not found. Please create it.")
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
    st.toast("Notes saved successfully!", icon="✅")

# --- MAIN APP ---
if check_password():
    st.title("🎨 NewBo City Market - Call for Artists")
    
    data = load_data()
    
    if data:
        # Sidebar for navigation
        st.sidebar.header("Submissions (29 Total)")
        
        # Create a list of artist names for the dropdown
        artist_options = {key: f"{key} - {info['name']}" for key, info in data.items()}
        selected_id = st.sidebar.selectbox(
            "Select an artist to review:", 
            options=list(artist_options.keys()), 
            format_func=lambda x: artist_options[x]
        )
        
        artist = data[selected_id]
        
        # Main review area
        st.header(artist["name"])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Artist Statement")
            st.write(artist["statement"])
            
            st.subheader("Portfolio / Work Link")
            st.markdown(f"🔗 [View {artist['name']}'s Submitted Work]({artist['work_link']})")
            
        with col2:
            st.subheader("Committee Notes")
            st.info("Notes saved here are visible to everyone logged in with the password.")
            
            # Text area for notes
            current_notes = artist.get("notes", "")
            new_notes = st.text_area("Leave your thoughts, questions, or votes here:", value=current_notes, height=300)
            
            if st.button("Save Notes", type="primary"):
                data[selected_id]["notes"] = new_notes
                save_data(data)