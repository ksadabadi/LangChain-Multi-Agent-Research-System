from src.tools.tools import web_search, scrape_url
from rich import print

# result = web_search("Latest news on AI research today")
# print(output)

# result = scrape_url("https://telanganatoday.com/tag/ai-research")

result = web_search.invoke("What is the latest research on using AI for climate change mitigation?")
print(result)