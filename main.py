import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from decouple import config

from textwrap import dedent
from agents import TravelAgents
from tasks import TravelTasks

# Install duckduckgo-search for this example:
# !pip install -U duckduckgo-search

from langchain.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
os.environ["OPENAI_ORGANIZATION"] = config("OPENAI_ORGANIZATION_ID")

# This is the main class that you will use to define your custom crew.
# You can define as many agents and tasks as you want in agents.py and tasks.py


class TripCrew:
    def __init__(self, origin, cities, travel_dates, interests):
        self.origin = origin
        self.cities = cities
        self.travel_dates = travel_dates
        self.interests = interests

    def run(self):
        # Define your custom agents and tasks in agents.py and tasks.py
        agents = TravelAgents()
        tasks = TravelTasks()

        # Define your custom agents and tasks here
        agent_expert_travel_agent = agents.expert_travel_agent()
        agent_city_selection_expert = agents.city_selection_expert()
        agent_local_tour_guide = agents.local_tour_guide()

        # Custom tasks include agent name and variables as input
        task_plan_itinerary = tasks.plan_itinerary(
            agent=agent_expert_travel_agent,
            city=self.cities,
            travel_dates=self.travel_dates,
            interests=self.interests
        )

        task_identify_city = tasks.identify_city(
            agent=agent_city_selection_expert,
            origin=self.origin,
            city=self.cities,
            travel_dates=self.travel_dates,
            interests=self.interests
        )

        task_gather_city_info = tasks.gather_city_info(
            agent=agent_local_tour_guide,
            city=self.cities,
            travel_dates=self.travel_dates,
            interests=self.interests 
        )

        # Define your custom crew here
        crew = Crew(
            agents=[agent_expert_travel_agent, agent_city_selection_expert,agent_local_tour_guide],
            tasks=[task_plan_itinerary, task_identify_city,task_gather_city_info],
            verbose=True,
        )

        result = crew.kickoff()
        return result


# This is the main function that you will use to run your custom crew.
if __name__ == "__main__":
    print("## Welcome to Crew AI Template")
    print("-------------------------------")
    var1 = input(dedent("""Enter variable 1: """))
    var2 = input(dedent("""Enter variable 2: """))

    custom_crew = CustomCrew(var1, var2)
    result = custom_crew.run()
    print("\n\n########################")
    print("## Here is you custom crew run result:")
    print("########################\n")
    print(result)