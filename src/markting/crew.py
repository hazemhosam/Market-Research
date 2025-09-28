from crewai import Agent, Process, Task, Crew, LLM
from crewai.project import CrewBase, agent, task, crew 
from crewai_tools import (SerperDevTool, ScrapeWebsiteTool, DirectoryReadTool, FileReadTool,
                          FileWriterTool)
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel, Field
from dotenv import load_dotenv 
from typing import List
from datetime import datetime

_ = load_dotenv() 

llm = LLM("gemini/gemini-2.0-flash",
          temperature=.3) 

class Content(BaseModel):
    content_type: str = Field(...,
                              description="The type of content to be created (e.g., blog post, social media post, video)")
    topic: str = Field(..., description="The topic of the content")
    target_audience: str = Field(..., description="The target audience for the content")
    tags: List[str] = Field(..., description="Tags to be used for the content")
    content: str = Field(..., description="The content itself")

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
        ],  max_iter=30,
            max_rpm=3,
            verbose=True)
        
    @agent
    def content_creator_social_media(self) -> Agent:
        return Agent(
            config=self.agents_config['content_creator_social_media'],#type: ignore
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool()
            ],
            inject_date=True,
            llm=llm,
            allow_delegation=True,
            max_iter=30,
            max_rpm=3
        )

    @agent
    def content_writer_blogs(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer_blogs'],#type: ignore
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts/blogs'),
                FileWriterTool(),
                FileReadTool()
            ],
            inject_date=True,
            llm=llm,
            allow_delegation=True,
            max_iter=5,
            max_rpm=3
        )

    @agent
    def seo_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_specialist'],#type: ignore
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool()
            ],
            inject_date=True,
            llm=llm,
            allow_delegation=True,
            max_iter=3,
            max_rpm=3
        )
     
    @task
    def market_research(self) -> Task:
        return Task(
            config=self.tasks_config['market_research'], #type: ignore
            agent=self.marketing_agent() #type: ignore
         )
    
    @task
    def marketing_strategy(self) -> Task:
        return Task(
            config=self.tasks_config['marketing_strategy'],#type: ignore
            agent=self.marketing_agent()
        )

    @task
    def create_content_calendar(self) -> Task:
        return Task(
            config=self.tasks_config['create_content_calendar'],#type: ignore
            agent=self.content_creator_social_media()
        )

    @task
    def prepare_post_drafts(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_post_drafts'],#type: ignore
            agent=self.content_creator_social_media(),
            output_json=Content
        )

    @task
    def prepare_scripts_for_reels(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_scripts_for_reels'],#type: ignore
            agent=self.content_creator_social_media(),
            output_json=Content
        )

    @task
    def content_research_for_blogs(self) -> Task:
        return Task(
            config=self.tasks_config['content_research_for_blogs'],#type: ignore
            agent=self.content_writer_blogs()
        )

    @task
    def draft_blogs(self) -> Task:
        return Task(
            config=self.tasks_config['draft_blogs'],#type: ignore
            agent=self.content_writer_blogs(),
            output_json=Content
        )

    @task
    def seo_optimization(self) -> Task:
        return Task(
            config=self.tasks_config['seo_optimization'],#type: ignore
            agent=self.seo_specialist(),
            output_json=Content
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
        "budget": "15,000 $",
        "current_date": datetime.now().strftime("%Y-%m-%d")}
crew = MarkteingCrew()
crew.crew().kickoff(inputs) 
            
         
        
