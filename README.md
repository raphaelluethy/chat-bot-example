# AI Assistant Chat with Streamlit

A simple chat application built with Streamlit and the OpenAI Assistants API that allows you to interact with existing AI assistants.

## Prerequisites

1. **Python 3.12+**: Make sure you have Python 3.12 or higher installed
2. **OpenAI API Key**: Get your API key from [OpenAI Platform](https://platform.openai.com/)
3. **Assistant ID**: Create an assistant in the [OpenAI Playground](https://platform.openai.com/playground)

## Installation

1. Clone or download this project
2. Install dependencies using uv (recommended) or pip:

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

4. Set your environment variables (for demo purposes, you can also set them in the code):

```bash
# For macOS/Linux
export OPENAI_API_KEY="your-api-key-here"
export ASSISTANT_ID="your-assistant-id-here"

# For Windows
set OPENAI_API_KEY="your-api-key-here"
set ASSISTANT_ID="your-assistant-id-here"
```

## Getting Your Assistant ID

1. Go to the [OpenAI Playground](https://platform.openai.com/playground)
2. Create or select an existing assistant
3. Copy the Assistant ID from the assistant details (starts with `asst_`)

## Usage

1. **Start the application**:
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Enter your Assistant ID**:
   - Use the sidebar to enter your Assistant ID or if you want to persist it, set it in the code or the `.env` file
   - The app will automatically connect and display assistant details
