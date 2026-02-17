"""
Main Deep Research Agent class.
"""

import json
import asyncio
from typing import Any
from langchain_core.messages import HumanMessage, SystemMessage

from .graph import create_research_graph
from .state import create_initial_state, ResearchState
from .tools import LLMProvider
from .utils import FOLLOW_UP_QUESTIONS_PROMPT, extract_json_from_text


class DeepResearchAgent:
    """
    Deep Research Agent using LangGraph.
    
    This agent performs iterative, deep research by:
    1. Understanding the research query through follow-up questions
    2. Generating targeted search queries
    3. Executing searches and extracting learnings
    4. Recursively exploring deeper based on findings
    5. Generating comprehensive reports
    
    Example:
        agent = DeepResearchAgent(breadth=4, depth=2)
        result = agent.run("What are the latest developments in quantum computing?")
        print(result["final_report"])
    """
    
    def __init__(
        self,
        breadth: int = 4,
        depth: int = 2,
        concurrency_limit: int = 3,
    ):
        """
        Initialize the Deep Research Agent.
        
        Args:
            breadth: Number of search queries per iteration (3-10 recommended)
            depth: Number of research iterations (1-5 recommended)
            concurrency_limit: Maximum concurrent searches (1-10)
        """
        self.breadth = breadth
        self.depth = depth
        self.concurrency_limit = concurrency_limit
        self.graph = create_research_graph()
        self.llm_provider = LLMProvider()
    
    async def generate_follow_up_questions(
        self,
        query: str,
        num_questions: int = 3,
    ) -> list[str]:
        """
        Generate follow-up questions to better understand the research needs.
        
        Args:
            query: The research query
            num_questions: Number of follow-up questions to generate
            
        Returns:
            List of follow-up questions
        """
        print(f"\n💭 Generating {num_questions} follow-up questions...")
        
        prompt = FOLLOW_UP_QUESTIONS_PROMPT.format(
            query=query,
            num_questions=num_questions,
        )
        
        llm = self.llm_provider.get_structured_llm()
        
        messages = [
            SystemMessage(content="You are a research assistant. Return only valid JSON."),
            HumanMessage(content=prompt),
        ]
        
        try:
            response = await llm.ainvoke(messages)
            content = extract_json_from_text(response.content)
            questions = json.loads(content)
            
            if isinstance(questions, dict) and "questions" in questions:
                questions = questions["questions"]
            
            if not isinstance(questions, list):
                return []
            
            return questions[:num_questions]
            
        except Exception as e:
            print(f"❌ Error generating follow-up questions: {e}")
            return []
    
    async def run_async(
        self,
        query: str,
        follow_up_answers: list[str] | None = None,
        skip_follow_up: bool = False,
    ) -> dict[str, Any]:
        """
        Run the research agent asynchronously.
        
        Args:
            query: The research query
            follow_up_answers: Answers to follow-up questions (optional)
            skip_follow_up: Skip generating follow-up questions
            
        Returns:
            Dictionary containing the final report and metadata
        """
        print("=" * 60)
        print(f"🚀 Starting Deep Research: {query}")
        print(f"📊 Parameters: Breadth={self.breadth}, Depth={self.depth}")
        print("=" * 60)
        
        # Generate and ask follow-up questions if not skipped
        if not skip_follow_up and not follow_up_answers:
            questions = await self.generate_follow_up_questions(query)
            if questions:
                print("\n❓ Follow-up questions generated:")
                for i, q in enumerate(questions, 1):
                    print(f"  {i}. {q}")
                print("\nNote: In CLI mode, these will be asked interactively.")
        
        # Create initial state
        initial_state = create_initial_state(
            query=query,
            breadth=self.breadth,
            depth=self.depth,
            follow_up_answers=follow_up_answers,
        )
        
        # Run the graph
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            print("\n" + "=" * 60)
            print("✅ Research Complete!")
            print(f"📚 Total learnings: {len(final_state.get('learnings', []))}")
            print(f"🔗 Total sources: {len(final_state.get('all_sources', []))}")
            print("=" * 60)
            
            return {
                "final_report": final_state.get("final_report", ""),
                "learnings": final_state.get("learnings", []),
                "sources": final_state.get("all_sources", []),
                "query": query,
                "breadth": self.breadth,
                "depth": self.depth,
            }
            
        except Exception as e:
            print(f"\n❌ Error during research: {e}")
            raise
    
    def run(
        self,
        query: str,
        follow_up_answers: list[str] | None = None,
        skip_follow_up: bool = False,
    ) -> dict[str, Any]:
        """
        Run the research agent (synchronous wrapper).
        
        Args:
            query: The research query
            follow_up_answers: Answers to follow-up questions (optional)
            skip_follow_up: Skip generating follow-up questions
            
        Returns:
            Dictionary containing the final report and metadata
        """
        return asyncio.run(
            self.run_async(query, follow_up_answers, skip_follow_up)
        )
    
    async def save_report(
        self,
        report: str,
        filename: str = "report.md",
    ):
        """
        Save the research report to a file.
        
        Args:
            report: The report content
            filename: Output filename
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n💾 Report saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")
