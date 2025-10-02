import streamlit as st
import os
import time
import json
from datetime import datetime
from openai import OpenAI

# SET YOUR OPENAI API KEY HERE
# DO NOT PUSH THE API KEYS TO GITHUB, THIS IS ONLY FOR DEMO PURPOSES
OPENAI_API_KEY = ""
ASSISTANT_ID = ""

st.set_page_config(page_title="KI Assistenten Chat", page_icon="", layout="wide")

# Custom CSS to make sidebar wider
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 450px;
        max-width: 450px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Initialize session state
if "thread" not in st.session_state:
    st.session_state.thread = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logs" not in st.session_state:
    st.session_state.logs = []
if "show_logs" not in st.session_state:
    st.session_state.show_logs = False
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""


def add_log(level, message, details=None):
    """Add a log entry to the session state"""
    # Translate log levels to German
    level_translation = {
        "INFO": "INFO",
        "SUCCESS": "ERFOLG",
        "ERROR": "FEHLER",
        "DEBUG": "DEBUG",
    }
    german_level = level_translation.get(level, level)

    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": german_level,
        "message": message,
        "details": details,
    }
    st.session_state.logs.append(log_entry)
    # Keep only last 100 logs to prevent memory issues
    if len(st.session_state.logs) > 100:
        st.session_state.logs = st.session_state.logs[-100:]


def create_thread():
    """Create a new thread"""
    add_log("INFO", "Erstelle neuen Thread")
    try:
        thread = client.beta.threads.create()
        add_log("SUCCESS", f"Thread erfolgreich erstellt", {"thread_id": thread.id})
        return thread
    except Exception as e:
        add_log("ERROR", f"Fehler beim Erstellen des Threads: {e}")
        st.error(f"Error creating thread: {e}")
        return None


def submit_message(assistant_id, thread_id, user_message):
    """Submit a message to the thread and create a run"""
    add_log(
        "INFO",
        f"Sende Nachricht",
        {"thread_id": thread_id, "message_length": len(user_message)},
    )
    try:
        # Create message
        message = client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_message
        )
        add_log("SUCCESS", f"Nachricht erstellt", {"message_id": message.id})

        # Create run
        run = client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )
        add_log("SUCCESS", f"Run erstellt", {"run_id": run.id, "status": run.status})
        return run
    except Exception as e:
        add_log("ERROR", f"Fehler beim Senden der Nachricht: {e}")
        st.error(f"Error submitting message: {e}")
        return None


def wait_on_run(run, thread_id):
    """Wait for a run to complete"""
    add_log(
        "INFO",
        f"Warte auf Abschluss des Runs",
        {"run_id": run.id, "initial_status": run.status},
    )
    status_count = 0
    while run.status == "queued" or run.status == "in_progress":
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            status_count += 1
            if status_count % 10 == 0:  # Log every 5 seconds
                add_log(
                    "DEBUG",
                    f"Run-Status-Prüfung",
                    {"run_id": run.id, "status": run.status, "checks": status_count},
                )
            time.sleep(0.5)
        except Exception as e:
            add_log("ERROR", f"Fehler bei der Prüfung des Run-Status: {e}")
            st.error(f"Error checking run status: {e}")
            break

    add_log(
        "INFO",
        f"Run abgeschlossen",
        {"run_id": run.id, "final_status": run.status, "total_checks": status_count},
    )
    return run


def get_thread_messages(thread_id):
    """Get all messages in a thread"""
    add_log("INFO", f"Rufe Thread-Nachrichten ab", {"thread_id": thread_id})
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id, order="asc")
        message_count = len(messages.data) if messages.data else 0
        add_log(
            "SUCCESS",
            f"Nachrichten abgerufen",
            {"count": message_count, "thread_id": thread_id},
        )
        return messages
    except Exception as e:
        add_log("ERROR", f"Fehler beim Abrufen der Nachrichten: {e}")
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
st.title("KI Assistenten Chat")

with st.sidebar:
    st.header("Konfiguration")

    # OpenAI API Key input
    api_key_input = st.text_input(
        "OpenAI API Key",
        value=OPENAI_API_KEY,
        help="Enter your OpenAI API Key",
        type="password",
    )
    has_api_key = bool(st.session_state.openai_api_key)
    assistant_id_input = st.text_input(
        "Assistenten-ID",
        value=ASSISTANT_ID,
        help="Enter your OpenAI Assistant ID",
        type="password",
        disabled=not has_api_key,
    )

    if api_key_input:
        st.session_state.openai_api_key = api_key_input
    elif not api_key_input and not OPENAI_API_KEY:
        api_key_from_env = os.getenv("OPENAI_API_KEY", "")
        if api_key_from_env:
            st.session_state.openai_api_key = api_key_from_env

    if has_api_key:
        try:
            client = OpenAI(api_key=st.session_state.openai_api_key)
        except Exception as e:
            st.error(f"Failed to initialize OpenAI client: {e}")
            has_api_key = False
    else:
        st.warning("Bitte geben Sie Ihren OpenAI API Key ein")
        st.info(
            "Sie können einen API Key von der [OpenAI Platform](https://platform.openai.com/api-keys) erhalten."
        )

    if assistant_id_input and has_api_key:
        st.session_state.assistant_id = assistant_id_input

        try:
            assistant = client.beta.assistants.retrieve(assistant_id_input)
            st.success(
                f"Sie sind nun verbunden mit dem Assistenten: **{assistant.name}**"
            )
            st.write(f"**Model:** {assistant.model}")
            if assistant.instructions is not None:
                st.write(f"**Instructions:** {assistant.instructions[:100]}...")

            if st.button("New Chat", type="secondary"):
                thread = create_thread()
                if thread:
                    st.session_state.thread = thread
                    st.session_state.messages = []
                    st.rerun()

        except Exception as e:
            st.error(f"Failed to connect to assistant: {e}")
            st.stop()
    elif not has_api_key:
        st.stop()
    else:
        st.warning("Bitte geben Sie eine Assistenten-ID ein, um zu chatten")
        st.info(
            "Sie können eine Assistenten-ID von der [OpenAI Playground](https://platform.openai.com/playground) Webseite erhalten."
        )
        st.stop()

    st.divider()
    st.markdown(f"### Logs ({len(st.session_state.logs)})")

    if st.button(
        "▶ Ausklappen" if not st.session_state.show_logs else "▼ Zuklappen",
        key="logs_toggle",
    ):
        st.session_state.show_logs = not st.session_state.show_logs
        st.rerun()

    if st.session_state.show_logs:
        if st.session_state.logs:
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Löschen", type="secondary", key="clear_logs"):
                    st.session_state.logs = []
                    st.rerun()

            with col2:
                logs_json = json.dumps(st.session_state.logs, indent=2, default=str)
                st.download_button(
                    label="Export",
                    data=logs_json,
                    file_name=f"chat_protokolle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key="export_logs",
                )

            col3, col4 = st.columns(2)
            with col3:
                filter_level = st.selectbox(
                    "Filter",
                    ["ALLE", "FEHLER", "INFO", "ERFOLG", "DEBUG"],
                    key="log_filter",
                )

            with col4:
                max_logs = st.number_input(
                    "Max anzeigen",
                    min_value=5,
                    max_value=100,
                    value=20,
                    step=5,
                    key="max_logs",
                )

            st.markdown("---")

            filtered_logs = [
                log
                for log in reversed(st.session_state.logs)
                if filter_level == "ALLE" or log["level"] == filter_level
            ][: int(max_logs)]

            level_colors = {
                "FEHLER": "🔴",
                "ERFOLG": "🟢",
                "INFO": "🔵",
                "DEBUG": "⚪",
            }

            for i, log in enumerate(filtered_logs):
                icon = level_colors.get(log["level"], "⚪")

                with st.expander(
                    f"{icon} {log['timestamp'].split()[1]} - {log['message'][:40]}...",
                    expanded=log["level"] == "FEHLER",
                ):
                    log_text = f"Level: {log['level']}\nZeit: {log['timestamp']}\nNachricht: {log['message']}"
                    st.text(log_text)

                    if log["details"]:
                        st.json(log["details"])
        else:
            st.info("Keine Protokolle verfügbar")

if not st.session_state.thread:
    thread = create_thread()
    if thread:
        st.session_state.thread = thread
    else:
        st.error("Failed to create thread. Please try again.")
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

user_input = st.chat_input("Tippen Sie hier")

if user_input and assistant_id_input:
    with st.chat_message("user"):
        st.write(user_input)

    with st.spinner("Assistent is am überlegen..."):
        run = submit_message(assistant_id_input, st.session_state.thread.id, user_input)

        if run:
            run = wait_on_run(run, st.session_state.thread.id)

            if run.status == "completed":
                messages = get_thread_messages(st.session_state.thread.id)
                if messages and messages.data:
                    st.session_state.messages = messages.data

                    for message in reversed(messages.data):
                        if message.role == "assistant" and message.content:
                            with st.chat_message("assistant"):
                                st.write(message.content[0].text.value)
                            break
            elif run.status == "failed":
                st.error(
                    f"Die Interaktion mit dem Assistenten ist fehlgeschlagen: {run.last_error}"
                )
            elif run.status == "requires_action":
                st.info(
                    "Der Assistent benötigt Tools (müssen in den Einstellungen des Assistenten aktiviert werden, bevor sie verwendet werden können). Bitte überprüfen Sie Ihre Einstellungen."
                )
            else:
                st.warning(
                    f"Die Konversation mit dem Assistenten ist fehlgeschlagen: {run.status}"
                )
