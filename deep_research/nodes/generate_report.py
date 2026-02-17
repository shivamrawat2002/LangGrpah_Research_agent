"""
Generate final report node.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from ..state import ResearchState
from ..tools import LLMProvider
from ..utils import (
    GENERATE_REPORT_PROMPT,
    format_learnings,
    format_sources,
    format_context,
    create_report_header,
)


async def generate_report_node(state: ResearchState) -> dict:
    """
    Generate the final research report.
    
    This node:
    1. Compiles all learnings from research iterations
    2. Organizes sources
    3. Generates a comprehensive markdown report
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with final_report
    """
    print("\n📝 Generating final research report...")
    
    # Format all learnings
    learnings_text = format_learnings(state.get("learnings", []))
    
    if not learnings_text or learnings_text == "No learnings yet.":
        print("⚠️ No learnings to compile into report")
        return {"final_report": "No research data available to generate report."}
    
    # Format context
    context = format_context(
        follow_up_answers=state.get("follow_up_answers"),
    )
    
    # Build prompt
    prompt = GENERATE_REPORT_PROMPT.format(
        query=state["query"],
        context=context,
        learnings=learnings_text,
    )
    
    # Generate report using LLM
    llm_provider = LLMProvider()
    llm = llm_provider.get_llm(temperature=0.7)
    
    messages = [
        SystemMessage(content="You are a professional research writer creating comprehensive reports."),
        HumanMessage(content=prompt),
    ]
    
    try:
        response = await llm.ainvoke(messages)
        report_content = response.content
        
        # Add header
        header = create_report_header(
            query=state["query"],
            breadth=state["breadth"],
            depth=state["depth"],
        )
        
        # Add sources section
        sources_section = format_sources(state.get("all_sources", []))
        
        # Combine all parts
        full_report = f"{header}\n{report_content}\n\n{sources_section}"
        
        print("✅ Report generated successfully")
        
        return {"final_report": full_report}
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return {"final_report": f"Error generating report: {str(e)}"}
