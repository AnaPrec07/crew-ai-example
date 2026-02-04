import os
from crewai import Agent, Task, Crew, Process
from decouple import config
from google.auth import default
from google.cloud import aiplatform

from textwrap import dedent
from agents import TravelAgents
from tasks import TravelTasks

# Install duckduckgo-search for this example:
# !pip install -U duckduckgo-search

from langchain.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

# Initialize GCP credentials and Vertex AI
# When running on Cloud Run, this will automatically use the service account
# For local development, set GOOGLE_APPLICATION_CREDENTIALS environment variable
try:
    credentials, project_id = default()
    gcp_project = config("GCP_PROJECT_ID", default=project_id)
    gcp_location = config("GCP_LOCATION", default="us-central1")
    
    # Initialize Vertex AI
    aiplatform.init(project=gcp_project, location=gcp_location)
    
    # Set environment variables for Vertex AI
    os.environ["GOOGLE_CLOUD_PROJECT"] = gcp_project
    os.environ["GOOGLE_CLOUD_LOCATION"] = gcp_location
except Exception as e:
    print(f"Warning: Could not initialize GCP credentials: {e}")
    print("Make sure GOOGLE_APPLICATION_CREDENTIALS is set or running on Cloud Run")
    gcp_project = config("GCP_PROJECT_ID", default=None)
    gcp_location = config("GCP_LOCATION", default="us-central1")

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