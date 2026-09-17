from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_search, scrape_url
from dotenv import load_dotenv

load_dotenv()

# Model Initialization
llm = ChatOpenAI(model = "gpt-4o-mini", temperature=0, max_tokens=2000)

# 1st Agent : Search Agent
def build_search_agent():
    """
    Build a search agent that can perform web searches.

    Returns:
        create_agent: An agent capable of performing web searches.
    """
    # Create the agent with the specified tools and prompt
    return create_agent(
        model=llm,
        tools=[web_search],
        
    )
    
# 2nd Agent : Reader Agent
def build_reader_agent():
    """
    Build a reader agent that can scrape and read content from URLs.

    Returns:
        create_agent: An agent capable of scraping and reading content from URLs.
    """
    # Create the agent with the specified tools and prompt
    return create_agent(
        model=llm,
        tools=[scrape_url],
        
    )

# Writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful research reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered: {research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well explained points)
- Conclusion
- Sources (list all URLs found in the research.)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# Critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report: {report}

Respond in this exact format:

Score: X/10
Strengths: List the strengths of the report.
Weaknesses: List the weaknesses of the report.
Areas to Improve: Suggest specific areas where the report can be improved.
One Line Verdict: Provide a concise one-line verdict on the overall quality of the report. """),
])

critic_chain = critic_prompt | llm | StrOutputParser()