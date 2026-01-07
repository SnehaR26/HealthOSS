from llm import model
from pydantic import BaseModel
import os
from typing import Literal, Dict, Any
import re
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver
from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from agents import nutrition_agent, fitness_agent, sleep_agent, wellness_agent, spending_agent


# check_llm = model.invoke("what is breakfast?")
# print(f"LLM Check Response: {check_llm.content}")

app = FastAPI(title="Health Supervisor API") 


class UserQuery(BaseModel):
    query: str

# 1. Load Environment Variables
load_dotenv()
# DB_HOST = os.getenv("DB_HOST")
# DB_NAME = os.getenv("DB_NAME")
# DB_USER = os.getenv("DB_USER") 
# DB_PASS = os.getenv("DB_PASS")

#agent_list = list(ALL_AGENTS.values())
# def nutrition_planner(userquery: str) -> Dict[str, Any]:
#     """
#     Simple rule-based nutrition planner.
#     - Detects goal: lose, gain, maintain weight.
#     - Detects diet type: veg, vegan, non-veg.
#     - Returns 1-day sample meal plan + tips.
#     """
#     q = userquery.lower()

#     # 1) Goal detection
#     if any(k in q for k in ["lose fat", "fat loss", "weight loss", "slim", "reduce weight"]):
#         goal = "weight_loss"
#         kcal_adj = -400
#     elif any(k in q for k in ["gain weight", "bulk", "build mass"]):
#         goal = "weight_gain"
#         kcal_adj = +300
#     else:
#         goal = "maintenance"
#         kcal_adj = 0

#     # 2) Diet type
#     if "vegan" in q:
#         diet_type = "vegan"
#     elif any(k in q for k in ["vegetarian", "veg only"]):
#         diet_type = "vegetarian"
#     else:
#         diet_type = "flexible"

#     # 3) Very rough calorie target (fallback when no profile data)
#     base_kcal = 2200
#     target_kcal = base_kcal + kcal_adj

#     # 4) Build a simple day plan
#     if diet_type == "vegan":
#         breakfast = "Oats with soy milk, banana, chia seeds, and peanut butter"
#         lunch = "Buddha bowl with quinoa, lentils, mixed veggies, and tahini"
#         dinner = "Tofu stir-fry with brown rice and mixed vegetables"
#     elif diet_type == "vegetarian":
#         breakfast = "Oats with yogurt/curd, nuts, and seasonal fruit"
#         lunch = "Dal, roti, mixed veg sabzi, and salad"
#         dinner = "Paneer/soy curry with brown rice and salad"
#     else:  # flexible / non-veg
#         breakfast = "Oats or eggs with whole-grain toast and fruit"
#         lunch = "Grilled chicken/fish or dal, brown rice, salad, and veggies"
#         dinner = "Light curry with beans or lean meat plus veggies"

#     response = {
#         "goal": goal,
#         "diet_type": diet_type,
#         "target_calories_approx": target_kcal,
#         "day_plan": {
#             "breakfast": breakfast,
#             "lunch": lunch,
#             "dinner": dinner,
#             "snacks": [
#                 "Handful of nuts or seeds",
#                 "One fruit (apple, banana, or seasonal fruit)",
#                 "Optional: yogurt/curd or buttermilk"
#             ]
#         },
#         "tips": [
#             "Aim for at least 20-30 g protein per main meal.",
#             "Fill half your plate with vegetables where possible.",
#             "Keep added sugar and ultra-processed foods minimal.",
#             "Drink enough water throughout the day."
#         ]
#     }
#     return response

# def fitness_trackker(userquery: str) -> Dict[str, Any]:
#     """
#     Simple workout recommender:
#     - Detects experience: beginner / intermediate.
#     - Detects goal: strength, fat loss, general fitness.
#     - Returns 3-day template with sets/reps.
#     """
#     q = userquery.lower()

#     # Experience
#     if any(k in q for k in ["beginner", "new to gym", "starting out"]):
#         level = "beginner"
#     elif any(k in q for k in ["intermediate", "lifting for years", "advanced"]):
#         level = "intermediate"
#     else:
#         level = "beginner"

#     # Goal
#     if any(k in q for k in ["lose fat", "fat loss", "cutting"]):
#         goal = "fat_loss"
#     elif any(k in q for k in ["gain muscle", "build muscle", "hypertrophy", "bulk"]):
#         goal = "muscle_gain"
#     else:
#         goal = "general_fitness"

#     # Simple 3-day split
#     day1 = {
#         "name": "Full body A",
#         "exercises": [
#             {"name": "Squat (bodyweight or barbell)", "sets": 3, "reps": 8 if goal == "muscle_gain" else 12},
#             {"name": "Push-up or Bench Press", "sets": 3, "reps": 8 if goal == "muscle_gain" else 12},
#             {"name": "Row (cable/dumbbell)", "sets": 3, "reps": 10},
#             {"name": "Plank", "sets": 3, "duration_seconds": 30}
#         ]
#     }

#     day2 = {
#         "name": "Cardio & Core",
#         "exercises": [
#             {"name": "Brisk walk or light jog", "duration_minutes": 20},
#             {"name": "Cycling / cross-trainer", "duration_minutes": 15},
#             {"name": "Crunches", "sets": 3, "reps": 15},
#             {"name": "Side plank", "sets": 3, "duration_seconds": 20}
#         ]
#     }

#     day3 = {
#         "name": "Full body B",
#         "exercises": [
#             {"name": "Deadlift or hip hinge variation", "sets": 3, "reps": 6 if goal == "muscle_gain" else 10},
#             {"name": "Overhead press (dumbbell/barbell)", "sets": 3, "reps": 8},
#             {"name": "Lat pulldown / pull-up", "sets": 3, "reps": 8},
#             {"name": "Lunges", "sets": 3, "reps_per_leg": 10}
#         ]
#     }

#     response = {
#         "level": level,
#         "goal": goal,
#         "recommended_frequency_per_week": 3 if level == "beginner" else 4,
#         "plan": [day1, day2, day3],
#         "general_tips": [
#             "Warm up for 5–10 minutes before workouts.",
#             "Use a weight where the last 2 reps are challenging but doable with good form.",
#             "Rest 60–90 seconds between sets for most exercises.",
#             "Increase weight or reps gradually over weeks."
#         ]
#     }
#     return response


# def sleep_optimizer(userquery: str) -> Dict[str, Any]:
#     """
#     Rule-based sleep advice:
#     - Tries to detect age group.
#     - Recommends target sleep range + simple schedule.
#     """
#     q = userquery.lower()

#     # Age detection by regex (very rough)
#     age = None
#     m = re.search(r"(\d{1,2})\s*(years|yrs|yo|year old)", q)
#     if m:
#         age = int(m.group(1))

#     if age is None:
#         age_group = "adult"
#         recommended_hours = "7–9"
#     elif age < 1:
#         age_group = "infant"
#         recommended_hours = "12–16 (including naps)"
#     elif 1 <= age <= 2:
#         age_group = "toddler"
#         recommended_hours = "11–14 (including naps)"
#     elif 3 <= age <= 5:
#         age_group = "preschool"
#         recommended_hours = "10–13 (including naps)"
#     elif 6 <= age <= 12:
#         age_group = "school_age"
#         recommended_hours = "9–12"
#     elif 13 <= age <= 18:
#         age_group = "teen"
#         recommended_hours = "8–10"
#     else:
#         age_group = "adult"
#         recommended_hours = "7–9"

#     # Simple schedule heuristic: assume typical wake at 7:00
#     wake_time = "07:00"
#     if age_group in ["adult", "teen"]:
#         bed_time = "22:30–23:30"
#     else:
#         bed_time = "20:00–21:00"

#     response = {
#         "age_group": age_group,
#         "recommended_hours": recommended_hours,
#         "suggested_schedule": {
#             "target_bed_time": bed_time,
#             "target_wake_time": wake_time
#         },
#         "sleep_hygiene_tips": [
#             "Keep a consistent sleep and wake time, even on weekends.",
#             "Avoid screens and bright light for 30–60 minutes before bed.",
#             "Limit caffeine in the late afternoon and evening.",
#             "Keep the bedroom dark, cool, and quiet.",
#             "Use bed mostly for sleep, not for work or long phone scrolling."
#         ]
#     }
#     return response


# def mental_wellness(userquery: str) -> Dict[str, Any]:
#     """
#     Basic mental wellness helper:
#     - Detects main concern: stress, anxiety, focus, mood.
#     - Returns a small routine + grounding techniques.
#     """
#     q = userquery.lower()

#     if "anxiety" in q or "anxious" in q:
#         concern = "anxiety"
#     elif "stress" in q or "burnout" in q or "overwhelmed" in q:
#         concern = "stress"
#     elif "focus" in q or "concentrat" in q:
#         concern = "focus"
#     elif "sad" in q or "low mood" in q or "depressed" in q:
#         concern = "mood"
#     else:
#         concern = "general"

#     daily_routine = [
#         "2–5 minutes of slow deep breathing (inhale 4s, exhale 6s) once or twice per day.",
#         "5–10 minutes of light movement or a short walk, ideally outdoors.",
#         "Short check-in journal: write 3 things on your mind and one small action for tomorrow.",
#         "Brief wind-down routine before bed: dim lights, no work or heavy social media."
#     ]

#     response = {
#         "primary_concern": concern,
#         "suggested_daily_routine": daily_routine,
#         "in_the_moment_techniques": [
#             "5-4-3-2-1 grounding: name 5 things you see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.",
#             "Box breathing: inhale 4s, hold 4s, exhale 4s, hold 4s, repeat 4–6 times.",
#             "Body scan: slowly relax muscles from toes up to face, noticing tension without judging."
#         ],
#         "safety_note": (
#             "If you have thoughts of self-harm, harming others, or severe distress, "
#             "please contact local emergency services or a mental health professional."
#         )
#     }
#     return response

# def log_health_spend( amount: float, category: Literal['nutrition', 'fitness', 'wellness'], description: str) -> str:
#     """
#     Records a health-related expense into the database. 
#     Use this tool whenever a user mentions spending money on health, gym, food, or supplements.
    
#     Args:
#         amount: The numerical value of the expense (e.g., 500.0)
#         category: The type of spend. Must be 'nutrition', 'fitness', or 'wellness'.
#         description: A short summary of what the money was spent on.
#     """
#     DB_HOST = os.getenv("DB_HOST")
#     DB_NAME = os.getenv("DB_NAME")
#     DB_USER = os.getenv("DB_USER") 
#     DB_PASS = os.getenv("DB_PASS")

#     conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    
#     try:
#         with conn.cursor() as curs:
#             # Log the entry
#             curs.execute(
#                 "INSERT INTO health_spending_log (user_id, category, amount, description) "
#                 "VALUES (%s, %s, %s, %s)",
#                 ('1', category, amount, description)
#             )
            
#             # Fetch updated totals for the response
#             curs.execute("""
#                 SELECT category, COALESCE(SUM(amount), 0) 
#                 FROM health_spending_log WHERE user_id = '1' GROUP BY category
#             """)
#             totals = dict(curs.fetchall())
#             conn.commit()
            
#             # Return a clear confirmation string so the LLM knows it's done
#             return f"Successfully logged ₹{amount} for {description}. Current totals: {totals}"
#     except Exception as e:
#         return f"Error logging spend: {str(e)}"
#     finally:
#         conn.close()

# # 3. Create Agent with strict instructions to prevent loops
# system_prompt = (
#     "You are a health budget assistant. "
#     "When a user reports a spend, call the 'log_health_spend' tool EXACTLY ONCE. "
#     "After receiving the tool output, provide a friendly summary to the user and STOP. "
#     "Do not call the tool again for the same request."
# )

# # Use memory to maintain conversation context
# memory = InMemorySaver()
# spending_agent = create_react_agent(
#     model,
#     tools=[log_health_spend],
#     prompt=system_prompt,
#     checkpointer=memory
# )

# nutrition_agent = create_react_agent(
#     model,
#     tools=[nutrition_planner],
#     name="nutrition_planner",
#     prompt=("You are a Nutrition Planner. Handle any queries related to meal plans, nutrition advice, or calorie tracking."
#             "You MUST answer ONLY by calling one of your tools.\n"
#         "Do NOT answer directly; always use a tool, even if you know the answer.\n"
#     )
# )

# fitness_agent = create_react_agent(
#     model,
#     tools=[fitness_trackker],
#     name="fitness_tracker",
#     prompt=("You are a Fitness Trainer. Handle queries about exercises, workout routines, or exercise form."
#             "You MUST answer ONLY by calling one of your tools.\n"
#         "Do NOT answer directly; always use a tool, even if you know the answer.\n"
#     )
# )

# sleep_agent = create_react_agent(
#     model,
#     tools=[sleep_optimizer],
#     name="sleep_optimizer",
#     prompt=("You are a Sleep Optimizer. Advise on sleep hygiene, setting sleep schedules, and improving rest."
#             "You MUST answer ONLY by calling one of your tools.\n"
#         "Do NOT answer directly; always use a tool, even if you know the answer.\n"
#     )
# )

# wellness_agent = create_react_agent(
#     model,
#     tools=[mental_wellness],
#     name="mental_wellness",
#     prompt=("You are a Mental Wellness Advisor. Answer questions on meditation, stress management, and mental health support."
#             "You MUST answer ONLY by calling one of your tools.\n"
#         "Do NOT answer directly; always use a tool, even if you know the answer.\n"
#     )
# )

workflow = create_supervisor(
    [nutrition_agent, wellness_agent, sleep_agent, fitness_agent, spending_agent],
    #agent_list,
    model=model,
    prompt=(
       "You are a smart health app supervisor. Analyze the user's query "
        "and route it to exactly one correct agent.\n"
        "Do not answer user questions yourself; your only job is to delegate "
        "to one agent, which will answer using its tools."
        "- If the user asks about meal plans, nutrition advice, or calorie tracking, use 'nutrition_planner'.\n"
        "- If the user asks about exercises, workout routines, or exercise form, use 'fitness_tracker'.\n"
        "- If the user asks about sleep hygiene, setting sleep schedules, or improving rest, use 'sleep_optimizer'.\n"
        "- If the user asks about meditation, stress management, or mental health support, use 'mental_wellness'.\n"
        "- If the user asks about expenses and spending, use 'spending_tracker'.\n"
    ),
    output_mode="last_message" # Returns the final answer from the sub-agent
)
# 6. Initialize Checkpointer and Compile
memory = InMemorySaver()
graph_app = workflow.compile(checkpointer=memory)

@app.post("/chat")
async def chat_endpoint(request: UserQuery):
    try:
        print(f"Received query: {request.query}")
        config = {"configurable": {"thread_id": "1"}}
        print("--- Natural Language Health App Started ---")
        result = graph_app.invoke({
            "messages": [{
                "role": "user", 
                "content": request.query
            }]
        }, config=config)


        # Extract the final response
        if "messages" in result and len(result["messages"]) > 0:
            last_msg = result["messages"][-1]
            return {
                "response": last_msg.content,

            }
        else:
            return {"response": "No response generated."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)

    # while True:
    #     try:
    #         user_input = input("\nEnter your query (or 'exit' to quit): ")
            
    #         if user_input.lower() in ['exit', 'quit']:
    #             print("Goodbye!")
    #             break
                
    #         # Invoke the graph
    #         result = app.invoke({
    #             "messages": [{
    #                 "role": "user", 
    #                 "content": user_input
    #             }]
    #         }, config=config)

            
    #         # Print ALL messages to see the chain of thought
    #         print("\n--- DEBUG: MESSAGE HISTORY ---")
    #         for msg in result["messages"]:
    #             print(f"[{msg.type}]: {msg.content}")
    #             # Check if this message comes from a tool execution
    #             if hasattr(msg, 'tool_calls') and len(msg.tool_calls) > 0:
    #                 print(f"   >>> CALLING TOOL: {msg.tool_calls[0]['name']}")
    #         print("------------------------------\n")
    #         # Print the final response
    #         # The result structure depends on output_mode, usually the last AI message contains the answer
    #         if "messages" in result and len(result["messages"]) > 0:
    #             last_msg = result["messages"][-1]
    #             print(f"Answer: {last_msg.content}")
    #         else:
    #             print(result)

    #     except Exception as e:
    #         print(f"An error occurred: {e}")