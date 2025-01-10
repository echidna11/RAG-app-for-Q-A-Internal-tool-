import streamlit as st
from streamlit_oauth import OAuth2Component
import json, base64, os
from datetime import datetime
from db import MySQLDatabase
from rag_pipeline import RagUtil

AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
CLIENT_ID = '7800200758-80traj3lcfbthmk29jlaqii17aq0067s.apps.googleusercontent.com'
CLIENT_SECRET = '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'
REDIRECT_URI = "http://localhost:8501/"
SCOPE = "openid email profile https://www.googleapis.com/auth/drive.readonly"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZATION_URL, TOKEN_URL, TOKEN_URL)


import io, re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload

def fetch_file(file_path):
    if 'token' in st.session_state:
        # Load credentials from session state
        creds = Credentials(
            token=None,
            refresh_token=st.session_state.refresh_token,
            token_uri=TOKEN_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )

        drive_service = build('drive', 'v3', credentials=creds)

        # Extract file ID from file_path using regular expression
        file_id_match = re.search(r"/d/([a-zA-Z0-9_-]+)", file_path)
        if file_id_match:
            file_id = file_id_match.group(1)

            try:
                # Request the file content
                request = drive_service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print("Download %d%%." % int(status.progress() * 100))

                # Save the file locally
                file_info = drive_service.files().get(fileId=file_id).execute()
                file_name = file_info['name']
                file_extension = file_name.split('.')[-1]
                with open(f"files/{file_name}", "wb") as f:
                    f.write(fh.getvalue())

                print("File downloaded successfully.")
                return f"{file_name}"
            except Exception as e:
                print("Error downloading file:", e)
                return None
        else:
            print("Invalid file URL. Please provide a valid Google Drive file URL.")
            return None
    else:
        print("Token not found in session state.")
        return None

if 'token' not in st.session_state:

    # to figure out the permission tab, where it asks for access on each login, 
    # look into access type below here and make change here"

    result = oauth2.authorize_button("Continue with Google", REDIRECT_URI, SCOPE, extras_params={"access_type": "offline"}, icon="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 48 48'%3E%3Cdefs%3E%3Cpath id='a' d='M44.5 20H24v8.5h11.8C34.7 33.9 30.1 37 24 37c-7.2 0-13-5.8-13-13s5.8-13 13-13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 4.1 29.6 2 24 2 11.8 2 2 11.8 2 24s9.8 22 22 22c11 0 21-8 21-22 0-1.3-.2-2.7-.5-4z'/%3E%3C/defs%3E%3CclipPath id='b'%3E%3Cuse xlink:href='%23a' overflow='visible'/%3E%3C/clipPath%3E%3Cpath clip-path='url(%23b)' fill='%23FBBC05' d='M0 37V11l17 13z'/%3E%3Cpath clip-path='url(%23b)' fill='%23EA4335' d='M0 11l17 13 7-6.1L48 14V0H0z'/%3E%3Cpath clip-path='url(%23b)' fill='%2334A853' d='M0 37l30-23 7.9 1L48 0v48H0z'/%3E%3Cpath clip-path='url(%23b)' fill='%234285F4' d='M48 48L17 24l-4-3 35-10z'/%3E%3C/svg%3E")
    print(result)
    if result:
        id_token = result["token"]["id_token"]
        payload = id_token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        payload = json.loads(base64.b64decode(payload))
        email = payload["email"]
        print("The email of the user is:",email)
        st.session_state.token = result['token']
        st.session_state.user_info = result.get('user_info')
        st.session_state.email_id = email
        db = MySQLDatabase(host='localhost', user='root', password='vikas123', database='mydatabase')
        db.connect()
        db.new_user(email)
        st.session_state.access_token = result['token']['access_token']
        st.session_state.refresh_token = result['token']['refresh_token']
        st.session_state.logged_in = True
        st.experimental_rerun()

if st.session_state.get('logged_in') and 'topic_name' not in st.session_state:
    st.markdown(
        """<style>
        .stButton>button {
            float: right;
        }
        .side-bar {
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            width: 200px;
            padding: 20px;
            background-color: #f0f0f0;
            overflow-y: auto;
        }
        .topic-button {
            color: black;
            width: 100%;
            padding: 10px;
            margin-bottom: 5px;
            text-align: left;
            background-color: #e6e6e6;
            border-radius: 5px;
            cursor: pointer;
        }
        .chat-container {
            padding: 20px;
        }
        .query-bar {
            display: flex;
            margin-bottom: 10px;
        }
        .query-input {
            flex: 1;
            margin-right: 10px;
        }
        .search-button {
            flex-shrink: 0;
        }
        .chat-messages {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            background-color: #f9f9f9;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    # Sidebar for topics
    st.sidebar.header("Topics")
    create_topic_button = st.sidebar.button("Create Topic")
    new_topic = st.sidebar.text_input("Enter topic name")
    if create_topic_button and new_topic:
        db = MySQLDatabase(host='localhost', user='root', password='vikas123', database='mydatabase')
        db.connect()
        db.add_topic( new_topic, st.session_state.email_id)  # Update the database with the new topic
        st.experimental_rerun()

    # Display user's topics
    user_email = st.session_state.get('email_id')
    if user_email:
        db = MySQLDatabase(host='localhost', user='root', password='vikas123', database='mydatabase')
        db.connect()
        user_topics = db.get_user_topics(user_email)
        st.session_state.user_topics = user_topics
        if user_topics:
            for topic_name in user_topics:  # Iterate over topic names only
                if st.sidebar.button(topic_name, key=topic_name, help="Click to enter chat"):
                    st.session_state.topic_name = topic_name
                    st.rerun()

    # Logout button
    if st.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()
elif 'logged_in' not in st.session_state:
    st.write("You are not logged in.")

if 'topic_name' in st.session_state:
    db = MySQLDatabase(host='localhost', user='root', password='vikas123', database='mydatabase')
    db.connect()

    st.sidebar.header(f"Files for {st.session_state.topic_name}")
    file_path = st.sidebar.text_input("Enter file path")
    add_file_button = st.sidebar.button("Add File")

    if add_file_button and file_path:
        with st.spinner("Processing..."):
            file_name = fetch_file(file_path)
            if file_name:
                db.add_file_to_topic(st.session_state.topic_name, st.session_state.email_id, file_name, file_path)
                file_id = db.get_file_id(file_name, st.session_state.email_id)
                rag = RagUtil()
                collection_name = db.get_collection(st.session_state.email_id, st.session_state.topic_name)
                collection_name = collection_name.replace(".", "")
                rag.set_collection(collection_name)
                print("file ID of file being inserted is", file_id)
                rag.add_file_to_collection(f"files/{file_name}", file_id)
                if os.path.exists(f"files/{file_name}"):
                    os.remove(f"files/{file_name}")
                st.experimental_rerun()
            else:
                st.error("Invalid link. Please check the link provided.")


    # Display files in the sidebar
    files = db.get_files_for_topic(st.session_state.topic_name, st.session_state.email_id)
    if files:
        for file_info in files:
            file_name = file_info[0]
            file_path = file_info[1]
            # Display file name with a cross mark for removal
            if st.sidebar.button(f"{file_name} ❌", key=file_name):
                file_id = db.get_file_id(file_name, st.session_state.email_id)
                with st.spinner("Removing file..."):
                    rag = RagUtil()
                    collection_name = db.get_collection(st.session_state.email_id, st.session_state.topic_name)
                    collection_name = collection_name.replace(".", "")
                    rag.fetch_collection(collection_name)
                    rag.remove_file_from_collection(file_id)
                    db.remove_file_from_topic(st.session_state.topic_name, file_name)
                    st.experimental_rerun()

    st.write(f"Chat for topic: {st.session_state.topic_name}")
    user_message = st.text_input("Enter your message")
    send_button = st.button("Send")

    if send_button and user_message:
        with st.spinner("Bot is typing..."):
            rag = RagUtil()
            collection_name = db.get_collection(st.session_state.email_id, st.session_state.topic_name)
            collection_name = collection_name.replace(".", "")
            rag.fetch_collection(collection_name)
            response = rag.search(user_message)
            user_id = db.get_user_id(st.session_state.email_id)
            topic_id = db.get_topic_id(user_id, st.session_state.topic_name)
            current_datetime = datetime.now()
            db.insert_query(user_id, topic_id, user_message, response, current_datetime)
            st.experimental_rerun()

    # Display chat messages with scrollable chat box
    chat_messages = db.get_chat_messages(st.session_state.email_id, st.session_state.topic_name)
    chat_container = st.empty()

    with chat_container:
        st.write("Chat Messages:")
        for message in chat_messages:
            if message[0] == st.session_state.email_id:
                st.write(f"You: {message[1]}")  # Display user's messages
            else:
                st.write(f"Bot: {message[1]}")  # Display bot's responses



    # Button to exit the topic
    if st.button("Exit Topic"):
        st.session_state.pop('topic_name')
        st.experimental_rerun()