"""
Formatting utilities for research reports.
"""

from typing import Any
from datetime import datetime
from ..state import Learning, Source


def format_learnings(learnings: list[Learning]) -> str:
    """
    Format learnings into a readable text block.
    
    Args:
        learnings: List of Learning objects
        
    Returns:
        Formatted string with all learnings
    """
    if not learnings:
        return "No learnings yet."
    
    formatted = []
    for i, learning in enumerate(learnings, 1):
        sources_text = ""
        if learning.sources:
            sources_text = f" (Sources: {', '.join(learning.sources[:3])})"
        formatted.append(f"{i}. {learning.content}{sources_text}")
    
    return "\n".join(formatted)


def format_sources(sources: list[Source]) -> str:
    """
    Format sources into a bibliography section.
    
    Args:
        sources: List of Source objects
        
    Returns:
        Formatted markdown bibliography
    """
    if not sources:
        return ""
    
    # Deduplicate by URL
    seen_urls = set()
    unique_sources = []
    for source in sources:
        if source.url not in seen_urls:
            seen_urls.add(source.url)
            unique_sources.append(source)
    
    bibliography = ["## Sources\n"]
    for i, source in enumerate(unique_sources, 1):
        title = source.title or "Untitled"
        bibliography.append(f"{i}. [{title}]({source.url})")
    
    return "\n".join(bibliography)


def format_search_results(results: dict[str, list[dict[str, Any]]]) -> str:
    """
    Format search results for LLM consumption.
    
    Args:
        results: Dictionary mapping queries to search results
        
    Returns:
        Formatted string with all results
    """
    formatted = []
    
    for query, query_results in results.items():
        formatted.append(f"\n### Query: {query}\n")
        
        if not query_results:
            formatted.append("No results found.\n")
            continue
        
        for i, result in enumerate(query_results, 1):
            title = result.get("title", "Untitled")
            url = result.get("url", "")
            content = result.get("content", "")[:500]  # Truncate for brevity
            
            formatted.append(f"**Result {i}: {title}**")
            formatted.append(f"URL: {url}")
            formatted.append(f"Content: {content}...\n")
    
    return "\n".join(formatted)


def create_report_header(query: str, breadth: int, depth: int) -> str:
    """
    Create a header for the research report.
    
    Args:
        query: The research query
        breadth: Research breadth parameter
        depth: Research depth parameter
        
    Returns:
        Markdown header
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"""# Research Report: {query}

**Generated:** {timestamp}  
**Research Parameters:** Breadth={breadth}, Depth={depth}

---

"""


def create_answer_header(query: str) -> str:
    """
    Create a header for an answer document.
    
    Args:
        query: The question being answered
        
    Returns:
        Markdown header
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"""# Answer: {query}

**Generated:** {timestamp}

---

"""


def format_context(
    follow_up_answers: list[str] | None = None,
    current_depth: int = 0,
    total_depth: int = 2,
) -> str:
    """
    Format additional context for prompts.
    
    Args:
        follow_up_answers: Answers to follow-up questions
        current_depth: Current iteration depth
        total_depth: Total depth setting
        
    Returns:
        Formatted context string
    """
    context_parts = []
    
    if follow_up_answers:
        context_parts.append("User provided additional context:")
        for i, answer in enumerate(follow_up_answers, 1):
            context_parts.append(f"{i}. {answer}")
    
    if current_depth > 0:
        context_parts.append(
            f"\nThis is iteration {current_depth + 1} of {total_depth + 1}. "
            "Focus on deepening our understanding based on previous findings."
        )
    
    return "\n".join(context_parts) if context_parts else ""


def truncate_content(content: str, max_chars: int = 1000) -> str:
    """
    Truncate content to a maximum character length.
    
    Args:
        content: The content to truncate
        max_chars: Maximum characters to keep
        
    Returns:
        Truncated content with ellipsis if needed
    """
    if len(content) <= max_chars:
        return content
    return content[:max_chars] + "..."


def extract_json_from_text(text: str) -> str:
    """
    Extract JSON content from text that might have markdown code blocks.
    
    Args:
        text: Text potentially containing JSON
        
    Returns:
        Clean JSON string
    """
    text = text.strip()
    
    # Remove markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```)
        lines = lines[1:]
        # Remove last line (```)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    
    return text.strip()
