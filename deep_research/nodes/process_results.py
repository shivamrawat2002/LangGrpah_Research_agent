"""
Process search results and extract learnings node.
"""

import json
from langchain_core.messages import HumanMessage, SystemMessage

from ..state import ResearchState, Learning, ResearchDirection
from ..tools import LLMProvider, truncate_to_tokens
from ..utils import (
    PROCESS_RESULTS_PROMPT,
    GENERATE_DIRECTIONS_PROMPT,
    format_search_results,
    format_learnings,
    extract_json_from_text,
)


async def process_results_node(state: ResearchState) -> dict:
    """
    Process search results to extract learnings and generate next directions.
    
    This node:
    1. Analyzes search results
    2. Extracts key learnings
    3. Generates next research directions (if depth > 0)
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with learnings and next_directions
    """
    search_results = state.get("search_results", [])
    if not search_results:
        print("⚠️ No search results to process")
        return {"learnings": [], "next_directions": []}
    
    print(f"\n🧠 Processing {len(search_results)} search results...")
    
    # Format results for LLM
    results_by_query = {}
    for result in search_results:
        query = result["query"]
        if query not in results_by_query:
            results_by_query[query] = []
        results_by_query[query].append(result)
    
    results_text = format_search_results(results_by_query)
    
    # Truncate if too long (keep within token limits)
    results_text = truncate_to_tokens(results_text, max_tokens=8000)
    
    # Extract learnings
    learnings = await extract_learnings(state["current_goal"], results_text)
    
    print(f"✅ Extracted {len(learnings)} learnings")
    
    # Generate next directions if we haven't reached max depth
    next_directions = []
    if state["current_depth"] < state["depth"]:
        print(f"\n🎯 Generating next research directions (depth {state['current_depth'] + 1}/{state['depth']})...")
        next_directions = await generate_next_directions(
            state["query"],
            state["current_goal"],
            learnings,
            state["breadth"],
        )
        print(f"✅ Generated {len(next_directions)} new directions")
    
    return {
        "learnings": learnings,
        "next_directions": next_directions,
    }


async def extract_learnings(goal: str, results: str) -> list[Learning]:
    """Extract key learnings from search results."""
    
    prompt = PROCESS_RESULTS_PROMPT.format(
        goal=goal,
        results=results,
    )
    
    llm_provider = LLMProvider()
    llm = llm_provider.get_reasoning_llm()
    
    messages = [
        SystemMessage(content="You are a research analyst. Return only valid JSON."),
        HumanMessage(content=prompt),
    ]
    
    try:
        response = await llm.ainvoke(messages)
        content = extract_json_from_text(response.content)
        data = json.loads(content)
        
        # Parse learnings
        learnings = []
        for item in data.get("learnings", []):
            learnings.append(Learning(
                content=item.get("content", ""),
                sources=item.get("sources", []),
                confidence=item.get("confidence", 1.0),
            ))
        
        return learnings
        
    except Exception as e:
        print(f"❌ Error extracting learnings: {e}")
        return []


async def generate_next_directions(
    query: str,
    current_goal: str,
    learnings: list[Learning],
    breadth: int,
) -> list[ResearchDirection]:
    """Generate next research directions based on learnings."""
    
    learnings_text = format_learnings(learnings)
    
    prompt = GENERATE_DIRECTIONS_PROMPT.format(
        query=query,
        goal=current_goal,
        learnings=learnings_text,
        breadth=breadth,
    )
    
    llm_provider = LLMProvider()
    llm = llm_provider.get_reasoning_llm()
    
    messages = [
        SystemMessage(content="You are a research planner. Return only valid JSON."),
        HumanMessage(content=prompt),
    ]
    
    try:
        response = await llm.ainvoke(messages)
        content = extract_json_from_text(response.content)
        data = json.loads(content)
        
        # Parse directions
        directions = []
        for item in data.get("directions", []):
            directions.append(ResearchDirection(
                goal=item.get("goal", ""),
                rationale=item.get("rationale", ""),
                priority=item.get("priority", 1),
            ))
        
        # Sort by priority
        directions.sort(key=lambda x: x.priority)
        
        return directions[:breadth]
        
    except Exception as e:
        print(f"❌ Error generating directions: {e}")
        return []
