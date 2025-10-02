# AI Assistant Chat with Streamlit

A simple chat application built with Streamlit and the OpenAI Assistants API that allows you to interact with existing AI assistants.

## Features

- 🤖 **Use Existing Assistants**: Connect to any assistant you've created in the OpenAI Playground
- 💬 **Persistent Conversations**: Maintain conversation history across interactions
- 🎨 **Modern UI**: Clean, responsive interface built with Streamlit
- 🔄 **Stateful API**: Leverages OpenAI's Assistants API for context-aware conversations
- ⚡ **Simple Setup**: Just provide your Assistant ID and API key to start chatting

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

3. Set your environment variables:

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
   streamlit run app.py
   ```

2. **Enter your Assistant ID**:
   - Use the sidebar to enter your Assistant ID
   - The app will automatically connect and display assistant details

3. **Start Chatting**:
   - Type your message in the chat input
   - The assistant will respond based on its configuration
   - Your conversation history is maintained throughout the session

4. **New Chat**:
   - Click "New Chat" in the sidebar to start a fresh conversation
   - This creates a new thread while keeping the same assistant

## Example Assistant Setups

### Math Tutor
Create in OpenAI Playground:
```
Name: Math Tutor
Instructions: You are a personal math tutor. Answer questions briefly, in a sentence or less.
Model: gpt-4o
Tools: Code Interpreter
```

### Code Helper
Create in OpenAI Playground:
```
Name: Code Helper
Instructions: You are an expert programmer. Help users with coding questions, debugging, and best practices.
Model: gpt-4o
Tools: Code Interpreter, File Search
```

### Writing Assistant
Create in OpenAI Playground:
```
Name: Writing Assistant
Instructions: You are a professional writing coach. Help users improve their writing, grammar, and style.
Model: gpt-4o-mini
Tools: None
```

## Understanding the Assistants API

This application uses OpenAI's Assistants API, which provides:

- **Assistants**: AI entities with specific instructions and tools
- **Threads**: Conversation containers that maintain context
- **Runs**: Execution cycles where the assistant processes messages and uses tools

Unlike the Chat Completions API, the Assistants API is stateful, meaning you don't need to send the entire conversation history with each request.

## Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ Yes |
| `ASSISTANT_ID` | Your assistant ID (optional, can be entered in UI) | ❌ No |

### Assistant Capabilities

The app supports all assistant features:
- **Code Interpreter**: For running code and calculations
- **File Search**: For searching uploaded documents
- **Function Calling**: For custom function integration
- **Multiple Models**: gpt-4o, gpt-4o-mini, etc.

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   Error: Please set the OPENAI_API_KEY environment variable
   ```
   **Solution**: Make sure your OpenAI API key is properly set as an environment variable

2. **Invalid Assistant ID**
   ```
   Error: Failed to connect to assistant: Not found
   ```
   **Solution**: Verify your Assistant ID is correct and starts with `asst_`

3. **Run Failed**
   ```
   Error: Assistant run failed: ...
   ```
   **Solution**: This could be due to API limits or server issues. Try again later

4. **Permission Denied**
   ```
   Error: You don't have permission to access this assistant
   ```
   **Solution**: Make sure you're using the same OpenAI account that created the assistant

### Getting Help

- Check the [OpenAI Assistants API Documentation](https://platform.openai.com/docs/assistants/overview)
- Review the [OpenAI Cookbook Examples](https://cookbook.openai.com/examples/assistants_api_overview_python)
- Ensure you're using the latest version of the OpenAI Python SDK

## Development

### Project Structure
```
chat-bot-example/
├── app.py              # Main Streamlit application
├── pyproject.toml      # Project configuration and dependencies
├── README.md          # This file
└── .python-version    # Python version specification
```

### Key Components

- **`get_openai_client()`**: Cached OpenAI client initialization
- **`create_thread()`**: Creates new conversation threads
- **`submit_message()`**: Sends messages and triggers assistant runs
- **`wait_on_run()`**: Polls for run completion
- **`get_thread_messages()`**: Retrieves conversation history

## License

This project is provided as an example for educational purposes. Please refer to OpenAI's terms of service for API usage guidelines.

## Contributing

Feel free to submit issues and enhancement requests!
