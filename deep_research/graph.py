"""
LangGraph workflow definition for the Deep Research agent.
"""

from typing import Literal
from langgraph.graph import StateGraph, END

from .state import ResearchState
from .nodes import (
    generate_queries_node,
    search_node,
    process_results_node,
    generate_report_node,
)


def should_continue_research(state: ResearchState) -> Literal["continue", "report"]:
    """
    Conditional edge: Decide whether to continue research or generate report.
    
    Args:
        state: Current research state
        
    Returns:
        "continue" to do another research iteration, "report" to generate final report
    """
    # Check if we have next directions and haven't exceeded depth
    if state["current_depth"] < state["depth"] and state.get("next_directions"):
        return "continue"
    return "report"


def prepare_next_iteration(state: ResearchState) -> dict:
    """
    Prepare state for the next research iteration.
    
    This node:
    1. Increments the depth counter
    2. Sets the next research goal from directions
    3. Clears previous iteration data
    
    Args:
        state: Current research state
        
    Returns:
        Updated state for next iteration
    """
    next_directions = state.get("next_directions", [])
    
    if not next_directions:
        # No more directions, shouldn't reach here due to should_continue_research
        return {"current_depth": state["current_depth"] + 1}
    
    # Take the highest priority direction (first one, as they're sorted)
    next_goal = next_directions[0].goal
    
    print(f"\n🔄 Moving to depth {state['current_depth'] + 1}")
    print(f"📍 Next goal: {next_goal}")
    
    return {
        "current_depth": state["current_depth"] + 1,
        "current_goal": next_goal,
        "search_queries": [],  # Clear for next iteration
        "search_results": [],  # Clear for next iteration
    }


def create_research_graph() -> StateGraph:
    """
    Create the LangGraph workflow for deep research.
    
    The graph structure:
    
    START
      ↓
    generate_queries
      ↓
    search
      ↓
    process_results
      ↓
    [should_continue_research?]
      ↓              ↓
    continue      report
      ↓              ↓
    prepare_next → END
      ↓
    (loop back to generate_queries)
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("generate_queries", generate_queries_node)
    workflow.add_node("search", search_node)
    workflow.add_node("process_results", process_results_node)
    workflow.add_node("prepare_next", prepare_next_iteration)
    workflow.add_node("generate_report", generate_report_node)
    
    # Set entry point
    workflow.set_entry_point("generate_queries")
    
    # Add edges
    workflow.add_edge("generate_queries", "search")
    workflow.add_edge("search", "process_results")
    
    # Add conditional edge: continue research or generate report
    workflow.add_conditional_edges(
        "process_results",
        should_continue_research,
        {
            "continue": "prepare_next",
            "report": "generate_report",
        }
    )
    
    # Loop back for next iteration
    workflow.add_edge("prepare_next", "generate_queries")
    
    # End after report
    workflow.add_edge("generate_report", END)
    
    # Compile the graph
    return workflow.compile()


# For visualization (optional)
def visualize_graph():
    """
    Visualize the research graph structure.
    Requires: pip install pygraphviz (or graphviz)
    """
    try:
        graph = create_research_graph()
        # This will generate a PNG of the graph
        graph.get_graph().draw("research_graph.png", prog="dot")
        print("Graph visualization saved to research_graph.png")
    except Exception as e:
        print(f"Could not visualize graph: {e}")
        print("Install graphviz for visualization: pip install pygraphviz")
