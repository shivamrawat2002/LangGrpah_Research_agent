"""
Command-line interface for the Deep Research agent.
"""

import asyncio
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown

from deep_research import DeepResearchAgent


console = Console()


def print_banner():
    """Print welcome banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║         🔬 Deep Research Agent - LangGraph           ║
    ║                                                       ║
    ║   AI-powered research assistant for deep analysis    ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


async def main():
    """Main CLI entry point."""
    # Load environment variables
    load_dotenv()
    
    # Check required API keys
    if not os.getenv("FIRECRAWL_API_KEY"):
        console.print("❌ FIRECRAWL_API_KEY not found in environment!", style="bold red")
        console.print("Please set it in .env file or environment variables.")
        return
    
    # if not os.getenv("OPENAI_API_KEY") and not os.getenv("FIREWORKS_API_KEY"):
    #     console.print("❌ No LLM API key found!", style="bold red")
    #     console.print("Please set OPENAI_API_KEY or FIREWORKS_API_KEY in .env file.")
    #     return
    
    print_banner()
    
    # Get research query
    console.print("\n[bold]Step 1: Research Query[/bold]")
    query = Prompt.ask("What would you like to research?")
    
    if not query.strip():
        console.print("❌ Query cannot be empty!", style="bold red")
        return
    
    # Get breadth parameter
    console.print("\n[bold]Step 2: Research Breadth[/bold]")
    console.print("Number of search queries per iteration (recommended: 3-10)")
    breadth = IntPrompt.ask("Breadth", default=4)
    
    # Get depth parameter
    console.print("\n[bold]Step 3: Research Depth[/bold]")
    console.print("Number of research iterations (recommended: 1-5)")
    depth = IntPrompt.ask("Depth", default=2)
    
    # Initialize agent
    agent = DeepResearchAgent(breadth=breadth, depth=depth)
    
    # Generate follow-up questions
    console.print("\n[bold]Step 4: Follow-up Questions[/bold]")
    console.print("Generating questions to better understand your needs...\n")
    
    follow_up_questions = await agent.generate_follow_up_questions(query)
    follow_up_answers = []
    
    if follow_up_questions:
        console.print(Panel(
            "These questions help refine the research direction:",
            title="Follow-up Questions",
            border_style="blue"
        ))
        
        for i, question in enumerate(follow_up_questions, 1):
            answer = Prompt.ask(f"\n[cyan]{i}. {question}[/cyan]")
            if answer.strip():
                follow_up_answers.append(answer)
    
    # Confirm before starting
    console.print("\n[bold yellow]⚠️  Research Configuration:[/bold yellow]")
    console.print(f"  Query: {query}")
    console.print(f"  Breadth: {breadth}")
    console.print(f"  Depth: {depth}")
    console.print(f"  Follow-up answers: {len(follow_up_answers)}")
    console.print("\n[dim]This may take several minutes depending on depth...[/dim]")
    
    if not Confirm.ask("\nStart research?", default=True):
        console.print("Research cancelled.", style="yellow")
        return
    
    # Run research
    try:
        result = await agent.run_async(
            query=query,
            follow_up_answers=follow_up_answers,
            skip_follow_up=True,  # Already generated
        )
        
        # Display report
        console.print("\n" + "=" * 70)
        console.print("\n[bold green]✅ Research Complete![/bold green]\n")
        
        # Show report preview
        report = result["final_report"]
        
        # Ask if user wants to see the full report in terminal
        if Confirm.ask("Display full report in terminal?", default=False):
            console.print("\n")
            md = Markdown(report)
            console.print(md)
        
        # Save to file
        filename = Prompt.ask(
            "\nSave report to file?",
            default="report.md"
        )
        
        if filename:
            await agent.save_report(report, filename)
            console.print(f"\n✅ Report saved to [bold]{filename}[/bold]")
        
        # Summary stats
        console.print(f"\n[bold]Research Statistics:[/bold]")
        console.print(f"  📚 Learnings: {len(result['learnings'])}")
        console.print(f"  🔗 Sources: {len(result['sources'])}")
        console.print(f"  📄 Report length: {len(report)} characters")
        
    except KeyboardInterrupt:
        console.print("\n\n❌ Research interrupted by user.", style="bold red")
    except Exception as e:
        console.print(f"\n\n❌ Error during research: {e}", style="bold red")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\nGoodbye! 👋", style="bold cyan")
