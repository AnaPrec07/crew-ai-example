from crewai import Agent
from textwrap import dedent
from langchain_google_vertexai import ChatVertexAI

from tools.search_tools import SearchTools
from tools.calculator_tools import CalculatorTools

"""
Creating Agents Cheat Sheet:

- Think like a boss. Work backwards from the goal and think which employee you need
  to hire to get the job done. 
- Define the captain and the crew who orient the other agents towards the goal.
- Defien which experts the captain needs to commjunicate with and delegate tasks to. 
  Build a top down structure of the crew.

Goal:
- Create a 7 day travel itinerary with detailed per-day plans, including budget,
  packing suggestions and safety tips.

Captain/Manager/Boss:
- Role: Travel agent. 

Employees/Experts to hier: 
- City selection expert 
- Local tour guide


Notes: 
- Agents should be results driven and have a clear goal in mind. 
- Role is their job title
- Goals should be actionable
- Backstory should be their resume. 

"""

class TravelAgents:
    def __init__(self):
        self.GeminiPro = ChatVertexAI(
            model_name="gemini-pro", temperature=0.7)
        self.GeminiProAdvanced = ChatVertexAI(
            model_name="gemini-pro", temperature=0.7)

    def expert_travel_agent(self):
        return Agent(
            role="Expert Travel Agent",
            backstory=dedent(
                f"""Expert in travel planning and logistics. 
                I have decades of expereince making travel iteneraries."""),
            goal=dedent(f"""
                        Create a 7-day travel itinerary with detailed per-day plans,
                        include budget, packing suggestions, and safety tips.
                        """),
            tools=[
                SearchTools.search_internet,
                CalculatorTools.calculate
            ],
            verbose=True,
            llm=self.GeminiPro,
        )

    def city_selection_expert(self):
        return Agent(
            role="City Selection Expert",
            backstory=dedent(
                f"""Expert at analyzing travel data to pick ideal destinations"""),
            goal=dedent(
                f"""Select the best cities based on weather, season, prices, and traveler interests"""),
            tools=[SearchTools.search_internet],
            verbose=True,
            llm=self.GeminiProAdvanced,
        )

    def local_tour_guide(self):
        return Agent(
            role="Local Tour Guide",
            backstory=dedent(f"""Knowledgeable local guide with extensive information
        about the city, it's attractions and customs"""),
            goal=dedent(
                f"""Provide the BEST insights about the selected city"""),
            tools=[SearchTools.search_internet],
            verbose=True,
            llm=self.GeminiProAdvanced,
        )