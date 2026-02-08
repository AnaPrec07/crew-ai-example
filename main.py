import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from decouple import config

from textwrap import dedent
from agents import TravelAgents
from tasks import TravelTasks

from dotenv import load_dotenv

load_dotenv()


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
        agent_humorous_manager = agents.humorous_manager()

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
            cities=self.cities,
            travel_dates=self.travel_dates,
            interests=self.interests
        )

        task_gather_city_info = tasks.gather_city_info(
            agent=agent_local_tour_guide,
            city=self.cities,
            travel_dates=self.travel_dates,
            interests=self.interests 
        )

        task_compile_and_entertain = tasks.compile_and_entertain(
            agent=agent_humorous_manager,
        )

        # Define your custom crew here
        crew = Crew(
            agents=[agent_expert_travel_agent, agent_city_selection_expert,agent_local_tour_guide],
            tasks=[task_identify_city,task_gather_city_info, task_plan_itinerary, task_compile_and_entertain],
            verbose=True,
            process=Process.hierarchical,
            manager_agent=agent_humorous_manager
        )

        result = crew.kickoff()
        return result


# This is the main function that you will use to run your custom crew.
if __name__ == "__main__":
    print("## Welcome to Crew AI Template")
    print("-------------------------------")
    origin = "Panama"#input(dedent("""Enter the place of origin for your trip: """))
    cities = "Japan" #input(dedent("""Enter the cities you are interested in visiting: """))
    travel_dates = "November"#input(dedent("""Enter your travel dates: """))
    interests = "History and anime" #input(dedent("""Enter your interestes: """))

    trip_crew = TripCrew(
        origin=origin, 
        cities=cities, 
        travel_dates=travel_dates, 
        interests=interests
    )
    result = trip_crew.run()
    print("\n\n########################")
    print("## Here is you custom crew run result:")
    print("########################\n")
    print(result)