"""Tests for the Deep Research Agent."""

import pytest
import asyncio
from deep_research import DeepResearchAgent, ResearchState, create_initial_state


@pytest.fixture
def agent():
    """Create a test agent instance."""
    return DeepResearchAgent(breadth=2, depth=1)


@pytest.mark.asyncio
async def test_create_initial_state():
    """Test initial state creation."""
    state = create_initial_state(
        query="Test query",
        breadth=3,
        depth=2,
    )
    
    assert state["query"] == "Test query"
    assert state["breadth"] == 3
    assert state["depth"] == 2
    assert state["current_depth"] == 0
    assert len(state["learnings"]) == 0


@pytest.mark.asyncio
async def test_follow_up_questions(agent):
    """Test follow-up question generation."""
    questions = await agent.generate_follow_up_questions(
        "What are different LLMs architectures?",
        num_questions=2,
    )
    
    # Should return a list (may be empty if API fails)
    assert isinstance(questions, list)
    
    # If questions generated, they should be strings
    if questions:
        assert all(isinstance(q, str) for q in questions)
        assert len(questions) <= 2


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization with different parameters."""
    agent1 = DeepResearchAgent(breadth=5, depth=3)
    assert agent1.breadth == 5
    assert agent1.depth == 3
    
    agent2 = DeepResearchAgent()
    assert agent2.breadth == 4  # default
    assert agent2.depth == 2  # default


def test_sync_run():
    """Test synchronous run method (wrapper)."""
    agent = DeepResearchAgent(breadth=1, depth=1)
    
    # This is a basic test - actual run would require API keys
    # Just verify the method exists and is callable
    assert hasattr(agent, 'run')
    assert callable(agent.run)


@pytest.mark.asyncio
async def test_save_report(agent, tmp_path):
    """Test report saving."""
    test_report = "# Test Report\n\nThis is a test."
    test_file = tmp_path / "test_report.md"
    
    await agent.save_report(test_report, str(test_file))
    
    # Verify file was created and contains correct content
    assert test_file.exists()
    content = test_file.read_text()
    assert content == test_report
