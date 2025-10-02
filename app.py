import streamlit as st
import os
import time
from openai import OpenAI

# SET YOUR OPENAI API KEY HERE
# DO NOT PUSH THE API KEYS TO GITHUB, THIS IS ONLY FOR DEMO PURPOSES
OPENAI_API_KEY = ""
ASSISTANT_ID = ""

st.set_page_config(page_title="KI Assistenten Chat", page_icon="", layout="wide")


@st.cache_resource
def get_openai_client():
    api_key = OPENAI_API_KEY if OPENAI_API_KEY else os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        _ = st.error("Please set your OpenAI API key.")
        return None
    return OpenAI(api_key=api_key)


client = get_openai_client()

# Initialize session state
if "thread" not in st.session_state:
    st.session_state.thread = None
if "messages" not in st.session_state:
    st.session_state.messages = []


# Configuration
@st.cache_resource
def get_assistant_id():
    assistant_id = ASSISTANT_ID if ASSISTANT_ID else os.getenv("ASSISTANT_ID", "")
    if not assistant_id:
        _ = st.error("Please set your Assistant ID.")
        return None
    return assistant_id


def create_thread():
    """Create a new thread"""
    try:
        thread = client.beta.threads.create()
        return thread
    except Exception as e:
        _ = st.error(f"Error creating thread: {e}")
        return None


def submit_message(assistant_id, thread_id, user_message):
    """Submit a message to the thread and create a run"""
    try:
        # Create message
        client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_message
        )

        # Create run
        run = client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )
        return run
    except Exception as e:
        st.error(f"Error submitting message: {e}")
        return None


def wait_on_run(run, thread_id):
    """Wait for a run to complete"""
    while run.status == "queued" or run.status == "in_progress":
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            time.sleep(0.5)
        except Exception as e:
            st.error(f"Error checking run status: {e}")
            break
    return run


def get_thread_messages(thread_id):
    """Get all messages in a thread"""
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id, order="asc")
        return messages
    except Exception as e:
        st.error(f"Error getting messages: {e}")
        return None


def display_message(message):
    """Display a single message in the chat"""
    role = message.role
    content = message.content[0].text.value if message.content else ""

    if role == "user":
        with st.chat_message("user"):
            st.write(content)
    else:
        with st.chat_message("assistant"):
            st.write(content)


# Main interface
_ = st.title("KI Assistenten Chat")

with st.sidebar:
    _ = st.header("Konfiguration")

    assistant_id_input = st.text_input(
        "Assistenten-ID",
        value=ASSISTANT_ID,
        help="Enter your OpenAI Assistant ID",
        type="password",
    )

    if assistant_id_input:
        st.session_state.assistant_id = assistant_id_input

        # Get assistant info
        try:
            assistant = client.beta.assistants.retrieve(assistant_id_input)
            _ = st.success(
                f"Sie sind nun verbunden mit dem Assistenten: **{assistant.name}**"
            )
            st.write(f"**Model:** {assistant.model}")
            if assistant.instructions is not None:
                st.write(f"**Instructions:** {assistant.instructions[:100]}...")

            if st.button("New Chat", type="secondary"):
                # Create new thread
                thread = create_thread()
                if thread:
                    st.session_state.thread = thread
                    st.session_state.messages = []
                    st.rerun()

        except Exception as e:
            _ = st.error(f"Failed to connect to assistant: {e}")
            st.stop()
    else:
        _ = st.warning("Bitte geben Sie eine Assistenten-ID ein, um zu chatten")
        _ = st.info(
            "Sie können eine Assistenten-ID von der [OpenAI Playground](https://platform.openai.com/playground) Webseite erhalten."
        )
        st.stop()

# Initialize thread if not exists
if not st.session_state.thread:
    thread = create_thread()
    if thread:
        st.session_state.thread = thread
    else:
        _ = st.error("Failed to create thread. Please try again.")
        st.stop()

if st.session_state.messages and len(st.session_state.messages) > 0:
    for message in st.session_state.messages:
        display_message(message)
else:
    messages = get_thread_messages(st.session_state.thread.id)
    if messages and messages.data:
        st.session_state.messages = messages.data
        for message in st.session_state.messages:
            display_message(message)
    else:
        st.write("Starten Sie eine neue Konversation")

# Chat input
user_input = st.chat_input("Tippen Sie hier")

if user_input and assistant_id_input:
    with st.chat_message("user"):
        st.write(user_input)

    with st.spinner("Assistent is am überlegen..."):
        run = submit_message(assistant_id_input, st.session_state.thread.id, user_input)

        if run:
            run = wait_on_run(run, st.session_state.thread.id)

            if run.status == "completed":
                # Get updated messages
                messages = get_thread_messages(st.session_state.thread.id)
                if messages and messages.data:
                    st.session_state.messages = messages.data

                    # Display only the new assistant message
                    for message in reversed(messages.data):
                        if message.role == "assistant" and message.content:
                            with st.chat_message("assistant"):
                                st.write(message.content[0].text.value)
                            break
            elif run.status == "failed":
                _ = st.error(
                    f"Die Interaktion mit dem Assistenten ist fehlgeschlagen: {run.last_error}"
                )
            elif run.status == "requires_action":
                _ = st.info(
                    "Der Assistent benötigt Tools (müssen in den Einstellungen des Assistenten aktiviert werden, bevor sie verwendet werden können). Bitte überprüfen Sie Ihre Einstellungen."
                )
            else:
                _ = st.warning(
                    f"Die Konversation mit dem Assistenten ist fehlgeschlagen: {run.status}"
                )

            # Rerun to update the interface
            st.rerun()
