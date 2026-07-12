import streamlit as st
import hashlib
from PIL import Image
from PIL.ExifTags import TAGS
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="DeepTrace AI", page_icon="🧠", layout="wide")

st.title("🧠 DeepTrace AI: Digital Media Forensics")
st.markdown("### Evidence Analysis & Source Tracking Platform")
st.info("Step 1: Upload an image to begin the forensic workflow.")

# --- SIDEBAR ---
st.sidebar.header("Case Information")
case_id = st.sidebar.text_input("Case ID", "DT-2024-001")
analyst_name = st.sidebar.text_input("Analyst Name", "User_01")

# --- FUNCTIONS ---

# 1. Hashing Function (Integrity)
def calculate_hashes(file_bytes):
    md5 = hashlib.md5(file_bytes).hexdigest()
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    return md5, sha256

# 2. Metadata Function (Origin)
def extract_metadata(image):
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            exif_data[decoded] = value
    return exif_data

# --- MAIN UI ---
uploaded_file = st.file_uploader("Choose an image file...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read file bytes for hashing
    file_bytes = uploaded_file.getvalue()
    image = Image.open(uploaded_file)

    # Layout: Two columns
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🖼️ Uploaded Evidence")
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("🛡️ 1. Evidence Preservation (Hashes)")
        md5_h, sha256_h = calculate_hashes(file_bytes)
        
        # Displaying hashes in a code block for easy copying
        st.write("**MD5 Hash:**")
        st.code(md5_h)
        st.write("**SHA-256 Hash:**")
        st.code(sha256_h)
        st.success("Digital Fingerprint Generated Successfully.")

    st.divider()

    # --- METADATA SECTION ---
    st.subheader("📁 2. Metadata Forensics (EXIF Data)")
    
    metadata = extract_metadata(image)
    
    if metadata:
        # Convert dictionary to a nice table
        df_metadata = pd.DataFrame(metadata.items(), columns=["Attribute", "Value"])
        st.table(df_metadata)
        
        # Checking for "Software" signs
        if "Software" in metadata:
            st.warning(f"🚩 Potential Editing Software Detected: {metadata['Software']}")
    else:
        st.error("No EXIF Metadata found. The image may have been stripped of its history (common on Social Media).")

    # Placeholder for Phase 2
    st.divider()
    st.subheader("🔍 Next Phase: AI Manipulation Detection & ELA")
    st.write("The system is ready for AI Model integration...")