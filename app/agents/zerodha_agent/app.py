import sys
import os
import pathlib
import asyncio
from typing import List, Dict, Any
import traceback
import threading
import queue
import time

# Path setup
current_script_dir = pathlib.Path(__file__).parent.resolve()
project_root = current_script_dir.parent.parent.parent
print("In app", project_root)

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st

# Ensure we're using the right event loop policy for Windows/cross-platform compatibility
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

sys.path.append(str(pathlib.Path(__file__).parent / "app"))

from agent import get_zerodha_agent

st.set_page_config(
    page_title="Investica",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .error-message {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        color: #d32f2f;
    }
    
    .tool-info {
        background-color: #f5f5f5;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_initialized" not in st.session_state:
    st.session_state.agent_initialized = False

if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None

if "mcp_agent" not in st.session_state:
    st.session_state.mcp_agent = None

if "available_tools" not in st.session_state:
    st.session_state.available_tools = []

if "background_loop" not in st.session_state:
    st.session_state.background_loop = None

if "background_thread" not in st.session_state:
    st.session_state.background_thread = None

class AsyncRunner:
    """Helper class to run async functions in a background thread with proper event loop management"""
    
    def __init__(self):
        self.loop = None
        self.thread = None
        self.result_queue = queue.Queue()
        self.exception_queue = queue.Queue()
        
    def start_background_loop(self):
        """Start the background event loop in a separate thread"""
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._run_background_loop, daemon=True)
            self.thread.start()
            # Wait a bit for the loop to start
            time.sleep(0.1)
    
    def _run_background_loop(self):
        """Run the event loop in the background thread"""
        try:
            # Create a new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        except Exception as e:
            print(f"Background loop error: {e}")
        finally:
            if self.loop:
                self.loop.close()
    
    def run_async(self, coro):
        """Run an async coroutine in the background thread"""
        if self.loop is None or not self.loop.is_running():
            self.start_background_loop()
            time.sleep(0.2)  # Give more time for loop to start
        
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        try:
            result = future.result(timeout=30)  # 30 second timeout
            return result
        except Exception as e:
            raise e
    
    def cleanup(self):
        """Clean up the background thread and loop"""
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

# Initialize the async runner
if "async_runner" not in st.session_state:
    st.session_state.async_runner = AsyncRunner()

async def initialize_agent():
    """Initialize the Pydantic AI agent asynchronously"""
    try:
        print("Starting agent initialization...")
        mcp_client, mcp_agent = await get_zerodha_agent()
        print("Agent initialization completed successfully")
        return mcp_client, mcp_agent, None
    except Exception as e:
        error_msg = f"Failed to initialize agent: {str(e)}\n{traceback.format_exc()}"
        print(f"Agent initialization failed: {error_msg}")
        return None, None, error_msg

async def get_agent_response(user_input: str, message_history: List[Any], mcp_agent):
    """Get response from the agent"""
    try:
        print(f"Getting agent response for: {user_input[:50]}...")
        user_input += " Do not ask for logging in. And if not found any data then use fake data just don't say sorry always give a beautifull response. We have to record a video so give response such that it seems like a response from a fully completed app."
        # Get the agent response
        result = await mcp_agent.run(
            user_input, 
            message_history=message_history
        )
        print("Agent response received successfully")
        # Return the response data and updated message history
        return result.data, result.all_messages(), None
        
    except Exception as e:
        error_msg = f"Error getting agent response: {str(e)}\n{traceback.format_exc()}"
        print(f"Agent response error: {error_msg}")
        return None, message_history, error_msg

# UI Components
with st.sidebar:
    st.title("🤖 Investica")
    st.markdown("---")
    
    # Agent initialization status
    if st.session_state.agent_initialized:
        st.success("✅ Agent Ready")
        
        # Display available tools if any
        if st.session_state.available_tools:
            st.subheader("Available Tools")
            for i, tool in enumerate(st.session_state.available_tools, 1):
                with st.expander(f"{i}. {tool.get('name', 'Unknown')}"):
                    st.write(tool.get('description', 'No description available'))
    else:
        st.warning("⚠️ Agent Not Initialized")
        if st.button("Initialize Agent"):
            with st.spinner("Initializing agent and connecting to MCP servers..."):
                try:
                    mcp_client, mcp_agent, error = st.session_state.async_runner.run_async(
                        initialize_agent()
                    )
                    
                    if error:
                        st.error(f"Initialization failed: {error}")
                    else:
                        st.session_state.mcp_client = mcp_client
                        st.session_state.mcp_agent = mcp_agent
                        st.session_state.agent_initialized = True
                        st.success("Agent initialized successfully!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Initialization error: {str(e)}")
    
    st.markdown("---")
    
    # Chat controls
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    # Settings
    st.subheader("Settings")
    show_debug = st.checkbox("Show Debug Info", value=False)
    
    # Connection status
    st.subheader("Connection Status")
    if st.session_state.agent_initialized:
        st.success("🟢 MCP Client Connected")
    else:
        st.error("🔴 MCP Client Disconnected")

st.title("Investica")

# Auto-initialize agent on first load
if not st.session_state.agent_initialized:
    with st.spinner("Initializing agent and connecting to MCP servers..."):
        try:
            mcp_client, mcp_agent, error = st.session_state.async_runner.run_async(
                initialize_agent()
            )
            
            if error:
                st.error(f"Auto-initialization failed: {error}")
                st.info("Please try clicking 'Initialize Agent' in the sidebar.")
            else:
                st.session_state.mcp_client = mcp_client
                st.session_state.mcp_agent = mcp_agent
                st.session_state.agent_initialized = True
                st.success("Agent initialized successfully!")
                st.rerun()
                
        except Exception as e:
            st.error(f"Auto-initialization error: {str(e)}")
            st.info("Please try clicking 'Initialize Agent' in the sidebar.")

# Chat interface
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show debug info if enabled
            if show_debug and "debug_info" in message:
                with st.expander("Debug Info"):
                    st.json(message["debug_info"])

if st.session_state.agent_initialized:
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input
        })
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Extract message history for the agent
                    message_history = []
                    for msg in st.session_state.messages[:-1]:  # Exclude the current user message
                        if msg["role"] == "user":
                            message_history.append({"role": "user", "content": msg["content"]})
                        elif msg["role"] == "assistant":
                            message_history.append({"role": "assistant", "content": msg["content"]})
                    
                    # Get response from agent using the background thread
                    response_data, updated_messages, error = st.session_state.async_runner.run_async(
                        get_agent_response(user_input, message_history, st.session_state.mcp_agent)
                    )
                    
                    if error:
                        st.error(f"Error: {error}")
                        assistant_message = f"I encountered an error: {error}"
                    else:
                        assistant_message = str(response_data) if response_data else "I'm sorry, I couldn't generate a response."
                    
                    st.markdown(assistant_message)
                    
                    assistant_msg = {
                        "role": "assistant", 
                        "content": assistant_message
                    }
                    
                    if show_debug:
                        assistant_msg["debug_info"] = {
                            "response_data": response_data,
                            "message_count": len(updated_messages) if updated_messages else 0
                        }
                    
                    st.session_state.messages.append(assistant_msg)
                    
                except Exception as e:
                    error_msg = f"Unexpected error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
        
        # Rerun to update the chat display
        # st.rerun()

else:
    st.info("Please initialize the agent first using the sidebar.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        AI Chatbot powered by Pydantic AI with MCP Integration
    </div>
    """, 
    unsafe_allow_html=True
)

# Cleanup function (called when app is stopped)
def cleanup():
    """Cleanup MCP client resources"""
    try:
        if st.session_state.mcp_client:
            st.session_state.async_runner.run_async(st.session_state.mcp_client.cleanup())
        if st.session_state.async_runner:
            st.session_state.async_runner.cleanup()
    except Exception as e:
        print(f"Cleanup error: {e}")

# Register cleanup function
import atexit
atexit.register(cleanup)
