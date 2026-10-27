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

# Initialize default submissions dataset if file doesn't exist
DEFAULT_SUBMISSIONS = {
    "1": {
        "name": "Joseph Dulin-Didonato",
        "statement": "For six years, I've built an extensive portfolio of large scale murals, projects, gallery pieces, and commissions consistently delivering quality work on time. This piece should offer an exciting experience while showcasing images from Czech/ Bohemian history. The design could reflect everything from wildlife and natural features collaging with traditional patterns and clothing...",
        "work_link": "https://www.instagram.com/the_outside_artist/?hl=en",
        "notes_list": [],
        "is_favorite": False
    },
    "2": {
        "name": "Legacy Murals (Danielle Flicek & Matt Novak)",
        "statement": "Legacy Murals is built on over 25 years of artistic passion, transforming ordinary spaces into extraordinary works of art that inspire, connect, and leave a lasting impression. Dani brings over 25 years of professional painting experience while Matt brings strengths in project coordination, logistics, and technical problem-solving.",
        "work_link": "https://www.legacymuralsmn.com",
        "notes_list": [],
        "is_favorite": False
    },
    "3": {
        "name": "Sena Ostrander",
        "statement": "I'm a Denver-based painter and muralist whose work explores human connection, identity, and storytelling through expressive figurative imagery, vibrant color, and layered compositions. Public art has the ability to transform everyday spaces into places of connection and shared experience.",
        "work_link": "https://www.senaostrander.com",
        "notes_list": [],
        "is_favorite": False
    },
    "4": {
        "name": "Megan Roethler",
        "statement": "Since graduating UNI in 2020 with a BFA in painting, my work has expanded into a variety of creative outlets including small scale painting, digital rendering, murals, tattooing, and sculpture. My day job as a tattooer gives me a strong sense for working collaboratively.",
        "work_link": "https://www.instagram.com/rat_toos",
        "notes_list": [],
        "is_favorite": False
    },
    "5": {
        "name": "Tacy Cummings",
        "statement": "Hey there, I'm Tacy Cummings, a mural artist based in Iowa. I'm all about color, texture, and making bold and vibrant statements through my art. My work is unique and reflects my passion for bringing communities together through large-scale impact pieces.",
        "work_link": "https://crmurals.org/wp-content/uploads/elementor/forms/6adf4fc289dec.pdf",
        "notes_list": [],
        "is_favorite": False
    },
    "6": {
        "name": "ANYTOWN MURAL & SIGN LLC (Michael Ferrarell)",
        "statement": "Michael Ferrarell is a Chicago-based muralist and sign painter whose artistic practice focuses heavily on site-responsive aesthetics. His hand-painted visual narratives celebrate elements of heritage, nostalgia, natural beauty, industry, community, and civic pride.",
        "work_link": "https://www.instagram.com/anytownmuralandsign/",
        "notes_list": [],
        "is_favorite": False
    },
    "7": {
        "name": "Brandon Hogan",
        "statement": "I paint the moments a community needs to remember. My practice centers on large-scale murals and live event painting — work made in public, at the scale of the room it serves. I compose around the wall's structural features including stage, garage doors, and speakers.",
        "work_link": "https://instagram.com/bhxartt",
        "notes_list": [],
        "is_favorite": False
    },
    "8": {
        "name": "Lauren Brunson",
        "statement": "I see my pieces as expressions of free will and intuitive artistic exploration. I work in experimental media and figurative shading to reflect human duality, psychological subtones, and balance.",
        "work_link": "https://www.instagram.com/laurenrbrunson",
        "notes_list": [],
        "is_favorite": False
    },
    "9": {
        "name": "Kierim Visinhiriiev & ODVs Art Studio",
        "statement": "Kierim Visinhiriiev is collaborating with ODVs Art Studio (Toronto, Canada) for the NewBo City Market indoor mural. ODVs Art Studio specializes in spray paint and airbrush large-scale murals, including commercial installations across Ontario and 3D illusion murals.",
        "work_link": "https://odvsart.com",
        "notes_list": [],
        "is_favorite": False
    },
    "10": {
        "name": "David Neeld",
        "statement": "I make murals that read as one bold image from a distance and reward a closer look, crafted collaboratively with the community. I bring 23 years of engineering project management, 3a/3b lift certification, and hand-painted original artwork (no AI).",
        "work_link": "https://davidneeldstudio.com",
        "notes_list": [],
        "is_favorite": False
    },
    "11": {
        "name": "Jay Morgan (BLVD Murals)",
        "statement": "Jay Morgan is founder of BLVD Murals, an Austin-based studio with 15+ years of experience in large-scale commercial murals, public art, and architectural installations that reflect local creative energy and district history.",
        "work_link": "https://blvdmurals.com",
        "notes_list": [],
        "is_favorite": False
    },
    "12": {
        "name": "Amanda Stout",
        "statement": "For five years I have created public art that draws inspiration from environmental patterns and surrealist depictions of wildlife and nature. My work uses vibrant color and playful styles to bridge cultural gaps and celebrate community traditions.",
        "work_link": "https://astt8ec8.myportfolio.com/",
        "notes_list": [],
        "is_favorite": False
    },
    "13": {
        "name": "Jesse Coughlin",
        "statement": "Inspired from plants, pop art, graffiti, cartoons, and comics. Bright colors and bold lines adding visual appeal to the masses.",
        "work_link": "https://crmurals.org/wp-content/uploads/elementor/forms/6ad44bf18fb5e.jpeg",
        "notes_list": [],
        "is_favorite": False
    },
    "14": {
        "name": "laporsha Pledge",
        "statement": "I love to paint. I am ready to start painting more & getting my work known around the world.",
        "work_link": "https://crmurals.org/wp-content/uploads/elementor/forms/6ad442b0c1ece.jpeg",
        "notes_list": [],
        "is_favorite": False
    },
    "15": {
        "name": "Michael Grant / Captain KA’Zen",
        "statement": "A multidisciplinary international artist and creator of Japofuturist murals that blend Japanese aesthetics with African heritage and ancestral memory to honor community history while imagining new futures.",
        "work_link": "https://linktr.ee/AKcUracy",
        "notes_list": [],
        "is_favorite": False
    }
}

# Add entries up to 29 if missing
for i in range(16, 30):
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

submissions = load_data()

# Custom CSS styling for tile grid, overlays, and static 'X' button
st.markdown("""
<style>
    /* Fixed overlay backdrop */
    .modal-backdrop {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: rgba(0, 0, 0, 0.65);
        z-index: 9998;
    }
    /* Fixed overlay content container */
    .modal-box {
        position: fixed;
        top: 5vh; left: 10vw; width: 80vw; height: 90vh;
        background-color: #ffffff;
        color: #1a1a1a;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        z-index: 9999;
        overflow-y: auto;
    }
    /* Sticky Top-Right Static 'X' Close Button */
    .close-btn-container {
        position: absolute;
        top: 15px;
        right: 20px;
        z-index: 10000;
    }
    /* Tile layout