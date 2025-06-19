import sys
import os
import pathlib
import asyncio
from typing import List, Dict, Any
import traceback
import threading
import queue
import time
import uuid

# Path setup
current_script_dir = pathlib.Path(__file__).parent.resolve()
project_root = current_script_dir.parent
print("In app", project_root)

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st

# Ensure we're using the right event loop policy for Windows/cross-platform compatibility
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Import the simplified agentic flow
from graph import agentic_flow

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

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "background_loop" not in st.session_state:
    st.session_state.background_loop = None

if "background_thread" not in st.session_state:
    st.session_state.background_thread = None

class AsyncRunner:
    """Helper class to run async functions in a background thread with proper event loop management"""
    
    def __init__(self):
        self.loop = None
        self.thread = None
        
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

async def get_agentic_response(user_input: str, thread_id: str):
    """Get response from the agentic flow"""
    try:
        print(f"Getting agentic response for: {user_input[:50]}...")
        
        # Prepare the config with thread_id for conversation continuity
        config = {"configurable": {"thread_id": thread_id}}
        
        # Create the initial state with user input
        initial_state = {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            }
        
        # Get the agent response using the simplified flow
        result = await agentic_flow.ainvoke(initial_state, config=config)
        
        print("Agentic response received successfully")
        final_message = result["messages"][-1]["content"]
        return final_message, None
        
    except Exception as e:
        error_msg = f"Error getting agentic response: {str(e)}\n{traceback.format_exc()}"
        print(f"Agentic response error: {error_msg}")
        return None, error_msg

# UI Components
with st.sidebar:
    st.title("🤖 Investica")
    st.markdown("---")
    
    # Show thread ID for debugging
    st.subheader("Session Info")
    st.text(f"Thread ID: {st.session_state.thread_id[:8]}...")
    
    # Chat controls
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("🔄 New Session"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.success("New session started!")
        st.rerun()
    
    st.markdown("---")
    
    # Settings
    st.subheader("Settings")
    show_debug = st.checkbox("Show Debug Info", value=False)
    
    # Connection status
    st.subheader("Status")
    st.success("🟢 Agentic Flow Ready")

st.title("Investica")

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

# Chat input
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
                # Get response from agentic flow using the background thread
                response_data, error = st.session_state.async_runner.run_async(
                    get_agentic_response(user_input, st.session_state.thread_id)
                )
                
                if error:
                    st.error(f"Error: {error}")
                    assistant_message = f"I encountered an error: {error}"
                else:
                    # Extract the response content
                    if isinstance(response_data, dict):
                        # If response is a dict, try to get the main content
                        assistant_message = str(response_data.get('content', response_data.get('response', str(response_data))))
                    else:
                        assistant_message = str(response_data) if response_data else "I'm sorry, I couldn't generate a response."
                
                st.markdown(assistant_message)
                
                assistant_msg = {
                    "role": "assistant", 
                    "content": assistant_message
                }
                
                if show_debug:
                    assistant_msg["debug_info"] = {
                        "raw_response": response_data,
                        "thread_id": st.session_state.thread_id,
                        "response_type": type(response_data).__name__
                    }
                
                st.session_state.messages.append(assistant_msg)
                
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg
                })

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        AI Chatbot powered by Agentic Flow
    </div>
    """, 
    unsafe_allow_html=True
)

# Cleanup function (called when app is stopped)
def cleanup():
    """Cleanup resources"""
    try:
        if st.session_state.async_runner:
            st.session_state.async_runner.cleanup()
    except Exception as e:
        print(f"Cleanup error: {e}")

# Register cleanup function
import atexit
atexit.register(cleanup)