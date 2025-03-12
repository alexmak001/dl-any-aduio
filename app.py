import streamlit as st
import subprocess
import sys
import os
import zipfile
import shutil

def download_playlist(playlist_url, output_dir):
    """Calls spotDL via subprocess to download the playlist into output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Using --output to direct downloaded files into the folder.
    # The output template here is set to "folder/{artists} - {title}.{output-ext}"
    command = [
        sys.executable, "-m", "spotdl", "download", playlist_url
    ]

    # Start the subprocess and capture stdout (merging stderr).
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True, # ensures we get strings (not bytes)
        cwd=output_dir
    )
    
    # Create a placeholder in the Streamlit app for the log output.
    log_placeholder = st.empty()
    log_text = ""
    
    # Read output line by line and update the placeholder.
    for line in process.stdout:
        log_text += line
        log_placeholder.text(log_text)
    
    process.wait()
    return log_text


def zip_directory(folder_path, zip_filename):
    """Zip the contents of folder_path into zip_filename."""
    zip_path = os.path.join(folder_path, zip_filename)
    # Remove previous zip if exists
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Skip the zip file itself
                if file == zip_filename:
                    continue
                file_path = os.path.join(root, file)
                # Store files relative to folder_path in the zip archive
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    return zip_path

# Streamlit UI
st.title("Download Spotify Playlist")

playlist_url = st.text_input("Enter Spotify Playlist URL:")

if st.button("Download Playlist"):
    if playlist_url:
        st.info("Starting download. This may take a while...")
        
        # Define the output directory for this download session.
        output_dir = "downloads"
        
        # Optionally, you could clear out the folder before each download:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        # Run the download process
        download_playlist(playlist_url, output_dir)
        
        # Zip the downloaded folder to let user download all tracks as one file.
        zip_file = zip_directory(output_dir, "playlist.zip")
        
        st.success("Download complete!")
        with open(zip_file, "rb") as f:
            st.download_button("Download ZIP", data=f, file_name="playlist.zip")
    else:
        st.error("Please enter a valid Spotify playlist URL.")
