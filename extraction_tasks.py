"""
extraction_tasks.py — Extraction task for the Lector Doc Extractor.

Only ONE task uses the LangExtract API (Gemini):
  - main_ideas: extracts key ideas capturing 'Aha!' moments with parent-child structure.

Social media posts and lecture notes are generated from main_ideas by Gemini directly
(see api/main.py: _generate_social_from_ideas, _generate_teaching_from_ideas).
"""

import textwrap
from dataclasses import dataclass, field

import langextract as lx


@dataclass
class ExtractionTask:
    """A named extraction task with its prompt and examples."""
    name: str
    description: str
    prompt: str
    examples: list[lx.data.ExampleData] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# TASK: IDEAS PRINCIPALES — educational designer approach with Aha! moments
# ═══════════════════════════════════════════════════════════════════════════════

TASK_MAIN_IDEAS = ExtractionTask(
    name="main_ideas",
    description="Ideas principales · Momentos Aha! · Estructura padre-hijo",
    prompt=textwrap.dedent("""\
        Act as a world-class educational designer and master teacher.
        Extract the key ideas from the text, capturing the 'Aha!' moments that
        make this material truly memorable and transformational for learners.

        For each extraction:
        - Use EXACT text passages — do not paraphrase or invent wording.
        - Identify the 'Aha!' moment: what makes this insight surprising,
          counterintuitive, or genuinely transformational for the reader?
        - Note any specific frameworks, mental models, examples, or analogies
          the author uses to make the idea concrete and memorable.
        - Establish a clear parent-child structure:
            • "main_idea"  = the core insight (parent level)
            • "argument"   = a supporting point that reinforces a main idea (child)
            • "conclusion" = the actionable or transformational takeaway

        For attributes, provide:
        - "aha_moment":   the surprising or transformational insight in plain language
                          (what would make a student say 'I never thought of it that way!')
        - "parent_idea":  for arguments and conclusions, which main_idea they support
                          (brief phrase identifying the parent)
        - "framework":    specific model, example, analogy, or tool the author uses
                          (leave empty string "" if none)
        - "importance":   "high", "medium", or "low"

        Focus on what makes each idea TEACHABLE and MEMORABLE.
        Avoid generic summaries — capture what makes this idea unforgettable.
        Don't just summarize; capture the insight that changes how you think.
    """),
    examples=[
        lx.data.ExampleData(
            text=(
                "The most powerful force in the universe is compound interest. "
                "Small, consistent investments over long periods create extraordinary wealth. "
                "This principle applies not only to money but to knowledge, relationships, "
                "and skills. Therefore, the key to success is patience and consistency, "
                "not brilliance or luck."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="main_idea",
                    extraction_text="The most powerful force in the universe is compound interest",
                    attributes={
                        "aha_moment": "Consistency over time beats raw talent — anyone can harness compound growth, not just the gifted",
                        "framework":  "Compound interest as a universal principle applicable to all domains, not just finance",
                        "importance": "high",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="argument",
                    extraction_text="Small, consistent investments over long periods create extraordinary wealth",
                    attributes={
                        "aha_moment": "Tiny daily actions compound into massive results — the barrier to greatness is lower than we think",
                        "parent_idea": "Compound interest as the most powerful force",
                        "framework":  "The 1% better every day model",
                        "importance": "high",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="argument",
                    extraction_text="This principle applies not only to money but to knowledge, relationships, and skills",
                    attributes={
                        "aha_moment": "Every domain has its own compounding — reading, practicing, connecting all compound just like money",
                        "parent_idea": "Compound interest as the most powerful force",
                        "framework":  "Domain generalization of compounding: knowledge, relationships, skills",
                        "importance": "medium",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="conclusion",
                    extraction_text="the key to success is patience and consistency, not brilliance or luck",
                    attributes={
                        "aha_moment": "Talent is overrated — showing up daily beats being gifted; success is a process, not a gift",
                        "parent_idea": "Compound interest as the most powerful force",
                        "framework":  "",
                        "importance": "high",
                    },
                ),
            ],
        )
    ],
)


# ═══════════════════════════════════════════════════════════════════════════════
# ALL TASKS — only main_ideas uses the LangExtract API
# Social media and teaching material are generated from main_ideas by Gemini
# ═══════════════════════════════════════════════════════════════════════════════

TASKS = [TASK_MAIN_IDEAS]


def get_task_by_name(name: str) -> ExtractionTask | None:
    """Get a specific task by name."""
    for task in TASKS:
        if task.name == name:
            return task
    return None
