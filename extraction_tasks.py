"""
extraction_tasks.py — 5 extraction task definitions for multi-purpose book analysis.

Each task defines a prompt + few-shot examples for LangExtract.
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
# TASK 1: IDEAS PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════════════

TASK_MAIN_IDEAS = ExtractionTask(
    name="main_ideas",
    description="Ideas principales, argumentos y conclusiones del texto",
    prompt=textwrap.dedent("""\
        Extract the main ideas, key arguments, and conclusions from the text.
        For each main idea, identify the exact text passage that expresses it.
        Use exact text for extractions. Do not paraphrase.
        Classify each extraction as: main_idea, argument, or conclusion.
        Provide meaningful attributes including a brief summary and the
        importance level (high, medium, low).
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
                        "summary": "Compound interest as the most powerful force",
                        "importance": "high",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="argument",
                    extraction_text="Small, consistent investments over long periods create extraordinary wealth",
                    attributes={
                        "summary": "Consistency over time produces great results",
                        "supports": "compound interest principle",
                        "importance": "high",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="argument",
                    extraction_text="This principle applies not only to money but to knowledge, relationships, and skills",
                    attributes={
                        "summary": "Compounding applies beyond finance",
                        "supports": "universality of compound interest",
                        "importance": "medium",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="conclusion",
                    extraction_text="the key to success is patience and consistency, not brilliance or luck",
                    attributes={
                        "summary": "Success comes from patience, not talent",
                        "importance": "high",
                    },
                ),
            ],
        )
    ],
)


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 2: CONTENIDO PARA REDES SOCIALES (X / INSTAGRAM)
# ═══════════════════════════════════════════════════════════════════════════════

TASK_SOCIAL_MEDIA = ExtractionTask(
    name="social_media",
    description="Contenido para X (Twitter) e Instagram: citas, insights, hooks",
    prompt=textwrap.dedent("""\
        Extract content from the text that would be highly engaging for social media.
        Look for: powerful quotes, surprising insights, controversial statements,
        practical tips, and emotionally resonant passages.
        Use exact text for extractions. Do not paraphrase.
        Classify each as: quote, insight, or hook.
        In attributes, provide:
        - For quotes: a suggested tweet (max 280 chars) and instagram_caption
        - For insights: a one-line takeaway and suggested hashtags
        - For hooks: why it grabs attention and suggested platform (X or IG or both)
    """),
    examples=[
        lx.data.ExampleData(
            text=(
                "People don't buy what you do, they buy why you do it. "
                "And what you do simply proves what you believe. "
                "The goal is not to do business with everybody who needs what you have. "
                "The goal is to do business with people who believe what you believe."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="quote",
                    extraction_text="People don't buy what you do, they buy why you do it",
                    attributes={
                        "tweet": "People don't buy what you do, they buy WHY you do it. 🎯\n\nStop selling features. Start sharing purpose.",
                        "instagram_caption": "💡 People don't buy what you do, they buy WHY you do it.\n\nLa gente no compra lo que haces, compra por qué lo haces.\n\n#leadership #purpose #marketing #mindset",
                        "virality": "high",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="insight",
                    extraction_text="The goal is to do business with people who believe what you believe",
                    attributes={
                        "takeaway": "Attract aligned customers, not just any customers",
                        "hashtags": "#business #branding #values #entrepreneurship",
                        "platform": "both",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="hook",
                    extraction_text="what you do simply proves what you believe",
                    attributes={
                        "attention_reason": "Challenges conventional thinking about actions vs beliefs",
                        "platform": "X",
                    },
                ),
            ],
        )
    ],
)


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 3: MATERIAL PARA CLASES
# ═══════════════════════════════════════════════════════════════════════════════

TASK_TEACHING = ExtractionTask(
    name="teaching_material",
    description="Material pedagógico: conceptos, definiciones, ejemplos, preguntas de discusión",
    prompt=textwrap.dedent("""\
        Extract content useful for teaching and classroom discussion.
        Identify: key concepts with definitions, illustrative examples,
        and passages that could spark discussion questions.
        Use exact text for extractions. Do not paraphrase.
        Classify each as: concept, definition, example, or discussion_question.
        In attributes, provide:
        - For concepts: a clear explanation and difficulty level (basic, intermediate, advanced)
        - For definitions: the term being defined
        - For examples: what concept it illustrates
        - For discussion_questions: a suggested question based on the passage and
          expected learning outcome
    """),
    examples=[
        lx.data.ExampleData(
            text=(
                "Inflation is the rate at which the general level of prices for goods "
                "and services rises, eroding purchasing power. For example, if inflation "
                "is 3% per year, a $100 basket of goods will cost $103 next year. "
                "Central banks attempt to limit inflation through monetary policy, "
                "but this creates tension with economic growth objectives."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="concept",
                    extraction_text="Inflation is the rate at which the general level of prices for goods and services rises",
                    attributes={
                        "explanation": "The sustained increase in the general price level of goods and services over time",
                        "difficulty": "basic",
                        "subject_area": "economics",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="definition",
                    extraction_text="eroding purchasing power",
                    attributes={
                        "term": "purchasing power erosion",
                        "explanation": "The decline in the value of money relative to goods",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="example",
                    extraction_text="if inflation is 3% per year, a $100 basket of goods will cost $103 next year",
                    attributes={
                        "illustrates": "inflation rate calculation",
                        "type": "numerical example",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="discussion_question",
                    extraction_text="this creates tension with economic growth objectives",
                    attributes={
                        "suggested_question": "How should central banks balance controlling inflation with promoting economic growth? What are the tradeoffs?",
                        "learning_outcome": "Understanding monetary policy tradeoffs",
                        "difficulty": "intermediate",
                    },
                ),
            ],
        )
    ],
)


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 4: MENSAJE / IDEA CENTRAL
# ═══════════════════════════════════════════════════════════════════════════════

TASK_CENTRAL_MESSAGE = ExtractionTask(
    name="central_message",
    description="Tesis central del libro con evidencia de soporte",
    prompt=textwrap.dedent("""\
        Identify the central thesis or core message of the text, along with
        the key supporting evidence and arguments.
        Use exact text for extractions. Do not paraphrase.
        Classify each as: thesis, core_message, or supporting_evidence.
        In attributes, provide:
        - For thesis: a one-sentence summary and confidence level (certain, likely, possible)
        - For core_message: why this is central to the author's argument
        - For supporting_evidence: what thesis/message it supports and how strongly
          (strong, moderate, weak)
    """),
    examples=[
        lx.data.ExampleData(
            text=(
                "The central argument of this work is that habits, not goals, "
                "determine our long-term outcomes. Goals are useful for setting direction, "
                "but systems are what produce results. Every Olympic athlete wants to win gold; "
                "the difference lies in their daily systems and routines."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="thesis",
                    extraction_text="habits, not goals, determine our long-term outcomes",
                    attributes={
                        "summary": "Habits are more important than goals for achieving results",
                        "confidence": "certain",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="core_message",
                    extraction_text="systems are what produce results",
                    attributes={
                        "centrality": "This is the actionable restatement of the thesis — focus on building systems",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="supporting_evidence",
                    extraction_text="Every Olympic athlete wants to win gold; the difference lies in their daily systems and routines",
                    attributes={
                        "supports": "habits over goals thesis",
                        "strength": "strong",
                        "type": "analogy",
                    },
                ),
            ],
        )
    ],
)


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 5: KNOWLEDGE BASE PARA BOT Q&A
# ═══════════════════════════════════════════════════════════════════════════════

TASK_KNOWLEDGE_BASE = ExtractionTask(
    name="knowledge_base",
    description="Base de conocimiento para bot profesor: hechos, explicaciones, Q&A",
    prompt=textwrap.dedent("""\
        Extract factual knowledge, concept explanations, and question-answer pairs
        from the text. This will be used to build a knowledge base for an
        educational chatbot that answers questions critically and objectively.
        Use exact text for extractions. Do not paraphrase.
        Classify each as: fact, concept_explanation, or qa_pair.
        In attributes, provide:
        - For facts: the domain/topic and whether it's an opinion vs established fact
        - For concept_explanations: the concept name, a clear explanation,
          and related concepts
        - For qa_pairs: a well-formed question and a comprehensive answer
          based on the text, plus a critical perspective noting any limitations
          or counterarguments
    """),
    examples=[
        lx.data.ExampleData(
            text=(
                "Diversification reduces portfolio risk without necessarily reducing returns. "
                "By holding assets that are not perfectly correlated, losses in one investment "
                "can be offset by gains in another. Harry Markowitz formalized this concept "
                "in Modern Portfolio Theory in 1952, for which he received the Nobel Prize."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="fact",
                    extraction_text="Harry Markowitz formalized this concept in Modern Portfolio Theory in 1952, for which he received the Nobel Prize",
                    attributes={
                        "topic": "finance, portfolio theory",
                        "type": "established fact",
                        "verifiable": "yes",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="concept_explanation",
                    extraction_text="Diversification reduces portfolio risk without necessarily reducing returns",
                    attributes={
                        "concept": "Diversification",
                        "explanation": "Spreading investments across different assets to reduce overall risk",
                        "related_concepts": "correlation, portfolio theory, risk management",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="qa_pair",
                    extraction_text="By holding assets that are not perfectly correlated, losses in one investment can be offset by gains in another",
                    attributes={
                        "question": "How does diversification reduce investment risk?",
                        "answer": "By holding assets that are not perfectly correlated, losses in one investment can be offset by gains in another, reducing overall portfolio volatility.",
                        "critical_note": "Diversification does not eliminate systemic risk. In severe market downturns, correlations tend to increase and diversification benefits diminish.",
                    },
                ),
            ],
        )
    ],
)


# ═══════════════════════════════════════════════════════════════════════════════
# ALL TASKS
# ═══════════════════════════════════════════════════════════════════════════════

TASKS = [
    TASK_MAIN_IDEAS,
    TASK_SOCIAL_MEDIA,
    TASK_TEACHING,
    TASK_CENTRAL_MESSAGE,
    TASK_KNOWLEDGE_BASE,
]


def get_task_by_name(name: str) -> ExtractionTask | None:
    """Get a specific task by name."""
    for task in TASKS:
        if task.name == name:
            return task
    return None
