🩺 HealthOSS: Multi-Agent Health Ecosystem (POC)
HealthOSS is a Proof of Concept (POC) for an intelligent health and wellness management platform. It utilizes a Multi-Agent Supervisor Architecture to provide specialized assistance across various pillars of health, from physical fitness to financial wellness.

Instead of a single "catch-all" chatbot, HealthOSS employs a team of specialized ReAct Agents orchestrated by a central Supervisor, ensuring high accuracy and context-aware responses.

🚀 Core Functionalities
The system is divided into specialized domains, each managed by a dedicated AI agent:

1. 🍱 Nutrition Agent
Purpose: Expert guidance on diet and meal planning.

Capabilities: Analyzes caloric intake, suggests macro-balanced meals, and provides nutritional breakdowns for various food items.

2. 🏋️ Fitness Agent
Purpose: Personal training and exercise optimization.

Capabilities: Recommends workout routines, explains proper exercise form, and tracks physical activity goals.

3. 😴 Sleep Agent
Purpose: Recovery and circadian rhythm management.

Capabilities: Offers insights into sleep hygiene, analyzes sleep patterns, and provides tips for better overnight recovery.

4. 🧘 Wellness Agent
Purpose: Holistic health and mental well-being.

Capabilities: Guides users through mindfulness practices, stress management techniques, and supplement information.

5. 💰 Health Spending Tracker
Purpose: Financial oversight of health-related expenses.

Capabilities: Logs Natural Language User input into a backend PostgreSQL DB, along with automatically mapped category

🏗️ System Architecture
The project is built using a Supervisor-Worker pattern:

The Supervisor: Acts as the "Brain." It receives user input, determines which specialist is best suited for the task, and routes the query.

The Agents (Workers): Built using langgraph.prebuilt.create_react_agent, these agents have access to specific tools (like the database) to perform actions.

State Management: Uses InMemorySaver to maintain conversation history across different agents, allowing for a seamless user experience.
