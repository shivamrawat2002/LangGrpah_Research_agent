"""
Deep Research Agent - LangGraph Implementation

A Python implementation of the Deep Research agent using LangGraph framework.
"""

from .agent import DeepResearchAgent
from .graph import create_research_graph
from .state import ResearchState

__version__ = "0.1.0"

__all__ = [
    "DeepResearchAgent",
    "create_research_graph",
    "ResearchState",
]
