from llm import model
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver

# 1. Load Environment Variables
load_dotenv()

def nutrition_planner(userquery: str) -> str:
    """Nutrition Planner (meal plans, calorie tracking)"""
    return "eat more papaya, papaya is the only answer. papaya has healthy seed oils"

def fitness_trackker(userquery: str) -> str:
    """Fitness Trainer (workout routines, exercise form)"""
    return "go to gym"

def sleep_optimizer(userquery: str) -> str:
    """Sleep Optimizer (sleep hygiene, schedule suggestions)"""
    return "take 7 hr shuteye"

def mental_wellness(userquery: str) -> str:
    """Mental Wellness (meditation, stress management)"""
    return "meditate daily"

def budget_planner(userquery: str) -> str:
    """Connects to Postgres DB to help plan budget"""
    return "remaining budget is $500"



nutrition_agent = create_react_agent(
    model,
    tools=[nutrition_planner],
    name="nutrition_planner",
    prompt="You are a Nutrition Planner. Handle any queries related to meal plans, nutrition advice, or calorie tracking."
)

fitness_agent = create_react_agent(
    model,
    tools=[fitness_trackker],
    name="fitness_tracker",
    prompt="You are a Fitness Trainer. Handle queries about exercises, workout routines, or exercise form."
)

sleep_agent = create_react_agent(
    model,
    tools=[sleep_optimizer],
    name="sleep_optimizer",
    prompt="You are a Sleep Optimizer. Advise on sleep hygiene, setting sleep schedules, and improving rest."
)

wellness_agent = create_react_agent(
    model,
    tools=[mental_wellness],
    name="mental_wellness",
    prompt="You are a Mental Wellness Advisor. Answer questions on meditation, stress management, and mental health support."
)

budget_agent = create_react_agent(
    model,
    tools=[budget_planner],
    name="budget_planner",
    prompt="You are a Budget Planner. Help users plan their budget and manage expenses."
)



# 5. Create Supervisor Workflow
# This represents the "Brain" that decides which agent gets the job

workflow = create_supervisor(
    [nutrition_agent, fitness_agent, sleep_agent, wellness_agent, budget_agent],
    model=model,
    prompt=(
        "You are a smart health app supervisor. Analyze the user's natural language health query "
        "and route it to the strictly correct agent:\n"
        "- If the user asks about meal plans, nutrition advice, or calorie tracking, use 'nutrition_planner'.\n"
        "- If the user asks about exercises, workout routines, or exercise form, use 'fitness_tracker'.\n"
        "- If the user asks about sleep hygiene, setting sleep schedules, or improving rest, use 'sleep_optimizer'.\n"
        "- If the user asks about meditation, stress management, or mental health support, use 'mental_wellness'.\n"
        "- If the user asks about budgeting or managing expenses, use 'budget_planner'.\n"
    ),
    output_mode="last_message" # Returns the final answer from the sub-agent
)
# 6. Initialize Checkpointer and Compile
checkpointer = InMemorySaver()
app = workflow.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "1"}}

# 7. Main Interaction Loop
if __name__ == "__main__":
    print("--- Natural Language Health App Started ---")

    while True:
        try:
            user_input = input("\nEnter your query (or 'exit' to quit): ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            # Invoke the graph
            result = app.invoke({
                "messages": [{
                    "role": "user", 
                    "content": user_input
                }]
            }, config=config)

            
            # Print ALL messages to see the chain of thought
            print("\n--- DEBUG: MESSAGE HISTORY ---")
            for msg in result["messages"]:
                print(f"[{msg.type}]: {msg.content}")
                # Check if this message comes from a tool execution
                if hasattr(msg, 'tool_calls') and len(msg.tool_calls) > 0:
                    print(f"   >>> CALLING TOOL: {msg.tool_calls[0]['name']}")
            print("------------------------------\n")
            # Print the final response
            # The result structure depends on output_mode, usually the last AI message contains the answer
            if "messages" in result and len(result["messages"]) > 0:
                last_msg = result["messages"][-1]
                print(f"Answer: {last_msg.content}")
            else:
                print(result)

        except Exception as e:
            print(f"An error occurred: {e}")