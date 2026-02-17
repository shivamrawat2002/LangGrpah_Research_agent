"""
All prompts used in the Deep Research agent.
"""

# Follow-up questions generation
FOLLOW_UP_QUESTIONS_PROMPT = """You are a research assistant helping to understand a user's research needs.

Given the research query: "{query}"

Generate {num_questions} thoughtful follow-up questions that would help you better understand:
- The specific aspects the user is most interested in
- The depth and breadth of information needed
- Any specific constraints or preferences
- The intended use of the research

Return ONLY a JSON array of strings, like: ["question 1", "question 2", "question 3"]
Do not include any other text or formatting."""


# Query generation
GENERATE_QUERIES_PROMPT = """You are a research assistant generating search queries.

Research Goal: {goal}

{context}

Generate {breadth} diverse and specific search queries that will help achieve this research goal.

Guidelines:
- Make queries specific and targeted
- Cover different aspects and angles
- Use professional/academic terminology when appropriate
- Include relevant time constraints if needed (e.g., "2024", "latest")
- Avoid redundant queries

{previous_learnings}

Return ONLY a JSON array of query strings, like: ["query 1", "query 2", "query 3"]
Do not include any other text or formatting."""


# Process results and extract learnings
PROCESS_RESULTS_PROMPT = """You are a research analyst extracting key learnings from search results.

Research Goal: {goal}

Search Results:
{results}

Analyze these results and extract:
1. Key learnings and insights (5-10 important findings)
2. Each learning should be specific, factual, and cite sources

Return your response as a JSON object with this structure:
{{
  "learnings": [
    {{
      "content": "Specific learning or insight",
      "sources": ["url1", "url2"],
      "confidence": 0.9
    }}
  ]
}}

Focus on quality over quantity. Ensure each learning is substantive and well-sourced."""


# Generate next research directions
GENERATE_DIRECTIONS_PROMPT = """You are a research planner deciding what to explore next.

Original Query: {query}

Current Research Goal: {goal}

Learnings So Far:
{learnings}

Based on what we've learned, generate {breadth} new research directions that would:
- Deep dive into the most important or interesting aspects
- Fill gaps in our current understanding
- Follow up on promising leads
- Explore related areas that matter

Return a JSON array of objects with this structure:
{{
  "directions": [
    {{
      "goal": "Specific research goal",
      "rationale": "Why this direction is important",
      "priority": 1
    }}
  ]
}}

Order by priority (1 = highest). Focus on directions that will add the most value."""


# Generate final report
GENERATE_REPORT_PROMPT = """You are a research writer creating a comprehensive report.

Original Query: {query}

Research Context:
{context}

All Learnings:
{learnings}

Create a detailed, well-structured research report in markdown format.

Requirements:
- Start with an executive summary
- Organize findings into logical sections with clear headings
- Use bullet points and numbered lists for readability
- Include specific facts, data, and examples
- Cite sources using markdown links: [source text](url)
- End with a conclusion and potential next steps
- Maintain a professional, analytical tone
- Aim for depth and comprehensiveness

The report should be thorough enough to be useful as a reference document."""


# Answer mode prompt (simpler)
ANSWER_QUERY_PROMPT = """You are a research assistant providing a comprehensive answer.

Question: {query}

{context}

Research Findings:
{learnings}

Provide a detailed, well-structured answer that:
- Directly addresses the question
- Synthesizes information from all sources
- Includes specific facts and examples
- Cites sources using markdown links: [source text](url)
- Is clear, concise, and authoritative

Format your answer in markdown with appropriate headings and structure."""
