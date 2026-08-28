from datetime import datetime
from langchain_core.tools import tool
from ddgs import DDGS

@tool
def get_current_datetime() -> str:
    """Returns the current live date and time."""
    return datetime.now().strftime("%A, %d %B %Y, %I:%M %p")

@tool
def web_search(query: str) -> str:
    """Search the internet for real-time news, cricket scores, and live queries."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return "No search results found."
            output = [f"Title: {r.get('title')}\nSnippet: {r.get('body')}" for r in results]
            return "\n\n".join(output)
    except Exception as e:
        return f"Search error: {str(e)}"

@tool
def get_cricket_score(country: str) -> str:
    """Use this tool when user asks about cricket scores."""
    return f"Live Cricket Update: Score between India and {country} is 120-3"