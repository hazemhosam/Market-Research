from crewai import Agent, Process, Task, Crew, LLM
from crewai.project import CrewBase, agent, task, crew 
from crewai_tools import (SerperDevTool, ScrapeWebsiteTool, DirectoryReadTool, FileReadTool,
                          FileWriterTool)
from crewai.agents.agent_builder.base_agent import BaseAgent
from dotenv import load_dotenv 
from typing import List
from datetime import datetime
import os

_ = load_dotenv() 

llm = LLM("gemini/gemini-2.0-flash",
          temperature=.3) 

@CrewBase
class MarkteingCrew():
    agents: List[BaseAgent]
    tasks: List[Task] 
    
    @agent
    def marketing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['markteing_agent'], #type: ignore
            llm=llm, tools=[
            SerperDevTool(),
            ScrapeWebsiteTool(),
            DirectoryReadTool(directory_path="./resources/drafts"),
            FileReadTool(),
            FileWriterTool()
        ],  max_iter=5,
            max_rpm=3,
            verbose=True)
     
    @task
    def market_research(self) -> Task:
        return Task(
            config=self.tasks_config['market_research'], #type: ignore
            agent=self.marketing_agent() #type: ignore
         )
    @crew
    def crew(self) -> Crew:
        """Creates the content writing crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


inputs = {
        "product_name": "AI Powered Excel Automation Tool",
        "target_audience": "Small and Medium Enterprises (SMEs)",
        "product_description": "A tool that automates repetitive tasks in Excel using AI, saving time and reducing errors.",
        "budget": "Rs. 50,000",
        "current_date": datetime.now().strftime("%Y-%m-%d")}
crew = MarkteingCrew()
crew.crew().kickoff(inputs) 
            
         
        
