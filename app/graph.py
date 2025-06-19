from pydantic_ai import Agent
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated, List
from langgraph.types import interrupt
from dotenv import load_dotenv
import logfire
import asyncio
import uuid

from app.utils import model
from app.agents import get_zerodha_agent

# Load environment variables
load_dotenv()

# Configure logfire to suppress warnings (optional)
logfire.configure(send_to_logfire='never')

router_agent = Agent(  
    model = model,
    system_prompt='Your job is to route the user to the relevant agent.',  
)

end_conversation_agent = Agent(  
    model = model,
    system_prompt='Your job is to end a conversation and summarize the whole conversation.',  
)

# Define state schema
class AgentState(TypedDict):
    messages: Annotated[List[dict], lambda x, y: x + y]

async def router_agen(state: AgentState):
    prompt = f"""
        Based on the conversation till now, your task is to route to which agent we should go.

        {state['messages']}

        List of available agents:
        "zerodha_agent": It is capable of doing trade execution, market anaylsis and post-trade tasks.
        "end_conversation_agent:" It's task is to end the conversation and provide the final result.

        Output should the name of the agent which is chosen.

        Example Outputs:
        "end_conversation_agent"
        "zerodha_agent"
    """

    result = await router_agent.run(prompt)
    next_action = result.output

    if next_action == "zerodha_agent":
        return "zerodha_agent"
    else:
        return "end_conversation"

async def zerodga_agent(state: AgentState):
    mcp_client, mcp_agent = await get_zerodha_agent()
    
    try:
            result = await mcp_agent.run(state['messages'][-1], message_history=state['messages'][:-1])
            
            # Add the new messages to the chat history
            return {
                "messages": [
                    {
                        "role": "assistant", 
                        "content": result.output
                    }
                ]
            }
    except Exception as e:
        print(f"\n[Error] An error occurred: {str(e)}")
    finally:
        await mcp_client.cleanup()

# End of conversation agent to give instructions for executing the agent
async def end_conversation(state: AgentState):
    prompt = f"""Summarize the conversation and give the final output, ther user will see only your output, so make you sure you present a good, concise yet clear output. You may make tables, charts or any other form of visual representaiton of the data to make the output more appealing.
    
    This is the conversation:
    {state['messages']}
    """

    result = await end_conversation_agent.run(prompt)
    return {
        "messages": [
            {
                "role": "assistant", 
                "content": result.output
            }
        ]
    }

builder = StateGraph(AgentState)

# Add nodes
builder.add_node("zerodha_agent", zerodga_agent)
builder.add_node("end_conversation", end_conversation)

# Set edges
builder.add_conditional_edges(
    START,
    router_agen,
    {
        "zerodha_agent": "zerodha_agent", 
        "end_conversation": "end_conversation"
    }
)
builder.add_conditional_edges(
    "zerodha_agent",
    router_agen,
    {
        "zerodha_agent": "zerodha_agent", 
        "end_conversation": "end_conversation"
    }
)
builder.add_edge("end_conversation", END)

# Configure persistence
memory = MemorySaver()
agentic_flow = builder.compile(checkpointer=memory)

async def run_cli():
    """Interactive CLI for testing the agentic flow"""
    print("🚀 Agentic Flow CLI Test")
    print("=" * 50)
    print("Commands:")
    print("  - Type your message to interact with agents")
    print("  - Type 'quit' or 'exit' to end the session")
    print("  - Type 'clear' to start a new conversation")
    print("  - Type 'help' to see this menu again")
    print("=" * 50)
    
    # Generate a unique thread ID for this session
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("\n👋 Thanks for testing! Goodbye!")
                break
            elif user_input.lower() == 'clear':
                thread_id = str(uuid.uuid4())
                config = {"configurable": {"thread_id": thread_id}}
                print("\n🔄 New conversation started!")
                continue
            elif user_input.lower() == 'help':
                print("\nCommands:")
                print("  - Type your message to interact with agents")
                print("  - Type 'quit' or 'exit' to end the session")
                print("  - Type 'clear' to start a new conversation")
                print("  - Type 'help' to see this menu again")
                continue
            elif not user_input:
                print("Please enter a message or command.")
                continue
            
            # Prepare initial state with user message
            initial_state = {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            }
            
            print("\n🤖 Processing...")
            
            # Run the agentic flow
            result = await agentic_flow.ainvoke(initial_state, config=config)
            
            # Display the final response
            if result and "messages" in result:
                final_message = result["messages"][-1]["content"]
                print(f"\n🎯 Assistant: {final_message}")
            else:
                print("\n⚠️  No response received from the agents.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    asyncio.run(run_cli())