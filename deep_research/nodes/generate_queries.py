"""
Generate search queries node for the research graph.
"""

import json
from langchain_core.messages import HumanMessage, SystemMessage

from ..state import ResearchState
from ..tools import LLMProvider
from ..utils import (
    GENERATE_QUERIES_PROMPT,
    format_learnings,
    format_context,
    extract_json_from_text,
)


async def generate_queries_node(state: ResearchState) -> dict:
    """
    Generate search queries based on current research goal.
    
    This node:
    1. Takes the current research goal
    2. Considers previous learnings if available
    3. Generates diverse search queries using LLM
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with search_queries
    """
    print(f"\n🔍 Generating {state['breadth']} search queries for: {state['current_goal']}")
    
    # Prepare context
    context = format_context(
        follow_up_answers=state.get("follow_up_answers"),
        current_depth=state["current_depth"],
        total_depth=state["depth"],
    )
    
    # Format previous learnings if available
    previous_learnings = ""
    if state.get("learnings"):
        learnings_text = format_learnings(state["learnings"])
        previous_learnings = f"\nPrevious Learnings:\n{learnings_text}\n\nBuild on these learnings and explore new angles."
    
    # Build prompt
    prompt = GENERATE_QUERIES_PROMPT.format(
        goal=state["current_goal"],
        breadth=state["breadth"],
        context=context,
        previous_learnings=previous_learnings,
    )
    
    # Get LLM and generate queries
    llm_provider = LLMProvider()
    llm = llm_provider.get_structured_llm()
    
    messages = [
        SystemMessage(content="You are a research query generator. Return only valid JSON."),
        HumanMessage(content=prompt),
    ]
    
    try:
        response = await llm.ainvoke(messages)
        
        # Parse JSON response
        content = extract_json_from_text(response.content)
        queries = json.loads(content)
        
        # Ensure we have a list
        if isinstance(queries, dict) and "queries" in queries:
            queries = queries["queries"]
        
        # Validate
        if not isinstance(queries, list):
            print("⚠️ Invalid response format, using fallback queries")
            queries = [state["current_goal"]]
        
        # Limit to breadth
        queries = queries[:state["breadth"]]
        
        print(f"✅ Generated {len(queries)} queries:")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")
        
        return {"search_queries": queries}
        
    except Exception as e:
        print(f"❌ Error generating queries: {e}")
        # Fallback: use the current goal as the only query
        return {"search_queries": [state["current_goal"]]}
