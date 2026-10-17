"""AI-Slop & Quality Audit Engine for OmniMCP Pro.

Features:
1. Real-time scanner for 2026 AI tropes & clichés with replacement suggestions.
2. 0–100 Slop Penalty Score calculation.
3. Hook Formula Classifier matching drafts against 20 proven viral formulas (F01–F20).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SlopMatch:
    phrase: str
    category: str
    suggestion: str
    severity: int  # 1 (low) to 10 (critical)
    index: int = -1


@dataclass
class HookClassification:
    formula_id: str
    formula_name: str
    confidence: float
    description: str
    example: str


@dataclass
class AuditResult:
    slop_score: int  # 0 (Human) to 100 (Synthetic Slop)
    slop_rating: str  # "Pristine", "Minor Clichés", "Noticeable Slop", "Heavy Slop"
    flagged_terms: List[SlopMatch] = field(default_factory=list)
    hook: Optional[HookClassification] = None
    character_count: int = 0
    word_count: int = 0
    reading_time_seconds: int = 0
    advice: List[str] = field(default_factory=list)


# Curated list of AI tropes and better human alternatives
SLOP_PATTERNS = [
    (r"\bdelve\b|\bdelving\b", "delve", "explore, dig into, examine, inspect", 10),
    (r"\btapestry\b", "tapestry", "system, mix, landscape, structure", 9),
    (r"\btestament to\b", "testament to", "proof of, evidence of, shows that", 8),
    (r"\bin today's (?:fast-paced|rapidly evolving|digital) world\b", "in today's world", "Cut this cliché opening entirely", 10),
    (r"\bbeacon of\b", "beacon of", "guide, model, benchmark", 7),
    (r"\bmultifaceted\b", "multifaceted", "complex, diverse, layered", 6),
    (r"\bplethora of\b", "plethora of", "many, plenty, dozen, host of", 7),
    (r"\bpivotal\b", "pivotal", "key, vital, critical", 6),
    (r"\bembark on\b|\bembarking\b", "embark", "start, begin, launch", 8),
    (r"\bunlock(?:ing)? (?:the|its) (?:full )?(?:power|potential)\b", "unlock the power", "enable, scale, build, unleash", 9),
    (r"\bseamlessly integrate[ds]?\b|\bseamless integration\b", "seamlessly integrate", "connects cleanly, pairs with, hooks into", 8),
    (r"\bgame-?changer\b", "game-changer", "major leap, breakthrough, shift", 7),
    (r"\bparamount\b", "paramount", "essential, critical, #1 priority", 6),
    (r"\bheralds a new era\b", "heralds a new era", "marks a change, shifts how we build", 9),
    (r"\bgroundbreaking\b", "groundbreaking", "novel, distinct, innovative", 6),
    (r"\bmoreover\b|\bfurthermore\b", "moreover/furthermore", "also, plus, what's more (or just start the point)", 5),
]

# 20 Proven Viral Hook Formulas (F01 - F20)
HOOK_FORMULAS = [
    {
        "id": "F01",
        "name": "The Obituary",
        "pattern": r"(?i)(?:is dead|is officially dead|rip\b|the death of|obsolete)",
        "example": "Microservices are dead. Here is what replaced them.",
        "description": "Boldly pronounces an established tool, paradigm, or practice obsolete.",
    },
    {
        "id": "F02",
        "name": "Year-over-Year Contrast",
        "pattern": r"(?i)(?:in 202[0-5].*in 202[6-9]|what changed in \d+ months|vs now)",
        "example": "Building an MCP server in 2024 vs 2026: 3 critical shifts.",
        "description": "Compares historical pain points against today's streamlined velocity.",
    },
    {
        "id": "F03",
        "name": "The Contrarian",
        "pattern": r"(?i)(?:everyone thinks|everyone is wrong|unpopular opinion|stop doing|don't believe)",
        "example": "Everyone is obsessing over agent frameworks. They are solving the wrong problem.",
        "description": "Challenges prevailing wisdom with an uncompromising, reasoned counter-argument.",
    },
    {
        "id": "F04",
        "name": "The Cold Open",
        "pattern": r"(?i)(?:at \d+ (?:am|pm)|yesterday morning|last night|3:00 am|the alert fired)",
        "example": "At 2:14 AM, our production cluster went pitch dark.",
        "description": "Drops the reader immediately into high-stakes drama or incident response.",
    },
    {
        "id": "F05",
        "name": "Hard Numbers",
        "pattern": r"(?i)(?:\$\d+|\d+x|\d+%\s*(?:faster|cheaper|reduction)|from \d+ to \d+)",
        "example": "How we slashed our cloud bill by $38,000 in 14 days without dropping traffic.",
        "description": "Leads with verifiable metrics, cost savings, or performance multipliers.",
    },
    {
        "id": "F06",
        "name": "The Vulnerable Confession",
        "pattern": r"(?i)(?:i was wrong|my biggest mistake|i screwed up|catastrophic failure|i admitted)",
        "example": "I spent 6 months building the wrong abstraction. Here is what I learned.",
        "description": "Demonstrates humility and hard-earned wisdom through a candid mistake.",
    },
    {
        "id": "F07",
        "name": "The Playbook / Cheat Sheet",
        "pattern": r"(?i)(?:the exact playbook|cheat sheet|step-by-step guide|our full stack|here is the blueprint)",
        "example": "The exact protocol-native stack we use to ship 5 production models a week.",
        "description": "Promises actionable, zero-fluff implementation artifacts and code architectures.",
    },
    {
        "id": "F08",
        "name": "The Cautionary Tale",
        "pattern": r"(?i)(?:don't make this mistake|before you (?:adopt|migrate|hire)|warning:|the danger of)",
        "example": "Before you migrate to vector search, beware this latency trap.",
        "description": "Warns peers against an invisible architectural hazard.",
    },
    {
        "id": "F09",
        "name": "The Framework Unveiling",
        "pattern": r"(?i)(?:mental model|a simple framework|the \d+-step rule|how to think about)",
        "example": "A 3-step mental model to evaluate whether your app actually needs an MCP agent.",
        "description": "Simplifies complex systems into a repeatable mental model.",
    },
    {
        "id": "F10",
        "name": "The Unpopular Observation",
        "pattern": r"(?i)(?:nobody talks about|the unspoken truth|hard truth|engineers won't admit)",
        "example": "The unspoken truth about AI code generation: 70% of velocity is spent on diff review.",
        "description": "Voices what practitioners think privately but rarely publish publicly.",
    },
    {
        "id": "F11",
        "name": "The Speed Run",
        "pattern": r"(?i)(?:in (?:under )?\d+ hours|in \d+ days|from zero to production in)",
        "example": "How we built and deployed a multi-platform social MCP server in 48 hours.",
        "description": "Spotlights high-velocity execution and agile shipping cadences.",
    },
    {
        "id": "F12",
        "name": "The Head-to-Head Benchmark",
        "pattern": r"(?i)(?:benchmark|vs\b|head to head|latency test|load test)",
        "example": "Voyager REST vs Patchright: We ran 10,000 automated queries to test throughput.",
        "description": "Delivers empirical benchmark data comparing two competing technologies.",
    },
    {
        "id": "F13",
        "name": "The Direct Challenge",
        "pattern": r"(?i)(?:if your repo doesn't|if you aren't using|you're doing it wrong if)",
        "example": "If your agent server doesn't support stdio hygiene, it's not production ready.",
        "description": "Draws a line in the sand regarding engineering standards.",
    },
    {
        "id": "F14",
        "name": "The Hidden Cost",
        "pattern": r"(?i)(?:the real cost of|the hidden bill|what nobody tells you about the pricing)",
        "example": "The hidden cost of SaaS scheduling tools: 30 seconds of browser lag per agent action.",
        "description": "Unveils hidden financial, latency, or architectural debt.",
    },
    {
        "id": "F15",
        "name": "The Paradox",
        "pattern": r"(?i)(?:the best way to .* is to|why doing less|the counter-intuitive)",
        "example": "The best way to make your autonomous agents faster is to run fewer browser instances.",
        "description": "Presents a counter-intuitive principle that turns out to be mathematically true.",
    },
    {
        "id": "F16",
        "name": "The Curated Arsenal",
        "pattern": r"(?i)(?:\d+ open-source tools|\d+ repos that replaced|\d+ libraries every)",
        "example": "5 open-source libraries that completely replaced our enterprise marketing stack.",
        "description": "High-signal tool roundups with specific production use cases.",
    },
    {
        "id": "F17",
        "name": "The Transformation",
        "pattern": r"(?i)(?:from .* to .* in|how we transformed|went from)",
        "example": "From 15-second browser timeouts to 280ms REST calls.",
        "description": "Dramatic before-and-after case study highlighting an optimization.",
    },
    {
        "id": "F18",
        "name": "The Direct Question",
        "pattern": r"(?i)^\s*(?:why are we still|is it time to|have we reached|how do you)",
        "example": "Why are we still paying $80/month for social APIs when browsers have local sessions?",
        "description": "Opens with an incisive question that demands reflection and discussion.",
    },
    {
        "id": "F19",
        "name": "The Zero to One",
        "pattern": r"(?i)(?:how we got our first|from 0 to \d+|our first \d+ users)",
        "example": "How we reached our first 1,000 GitHub stars with zero paid promotion.",
        "description": "Step-by-step account of taking an idea from inception to early traction.",
    },
    {
        "id": "F20",
        "name": "The Post-Mortem",
        "pattern": r"(?i)(?:post-?mortem|lessons from scaling|what we learned after \d+)",
        "example": "5 post-mortem lessons from running an MCP network across 500,000 agent calls.",
        "description": "Rigorous retrospective analyzing real-world systems under sustained load.",
    },
]


class AuditEngine:
    """Audits draft social content for synthetic AI patterns and classifies hooks."""

    @classmethod
    def audit_content(cls, text: str) -> AuditResult:
        if not text or not text.strip():
            return AuditResult(
                slop_score=0,
                slop_rating="Pristine",
                character_count=0,
                word_count=0,
                reading_time_seconds=0,
            )

        clean_text = text.strip()
        words = clean_text.split()
        word_count = len(words)
        char_count = len(clean_text)
        reading_time = max(1, int(word_count / 3.5))  # avg ~210 wpm = 3.5 words/sec

        flagged: List[SlopMatch] = []
        total_penalty = 0

        # 1. Scan for specific slop phrases
        for pattern, category, suggestion, severity in SLOP_PATTERNS:
            for match in re.finditer(pattern, clean_text, re.IGNORECASE):
                flagged.append(
                    SlopMatch(
                        phrase=match.group(0),
                        category=category,
                        suggestion=suggestion,
                        severity=severity,
                        index=match.start(),
                    )
                )
                total_penalty += severity * 4

        # 2. Check for staccato bullet stacks (4+ consecutive single lines with emojis or hyphens)
        staccato_count = len(re.findall(r"(?m)^[\s•\-*👉🚀💡🔥✅].{5,80}$", clean_text))
        if staccato_count >= 5:
            flagged.append(
                SlopMatch(
                    phrase="Staccato Bullet Stack",
                    category="structural",
                    suggestion="Blend repetitive short bullet points into descriptive prose paragraphs.",
                    severity=8,
                )
            )
            total_penalty += 20

        # Cap slop score to 100
        slop_score = min(100, total_penalty)

        # Rating label
        if slop_score <= 15:
            rating = "Pristine (Natural Voice)"
        elif slop_score <= 40:
            rating = "Minor AI Clichés"
        elif slop_score <= 70:
            rating = "Noticeable AI Slop"
        else:
            rating = "Heavy Synthetic Slop"

        # 3. Classify Hook
        hook = cls.classify_hook(clean_text)

        # 4. Generate constructive advice
        advice: List[str] = []
        if slop_score > 25:
            advice.append("Replace flagged corporate buzzwords with concrete verbs and specific examples.")
        if not hook or hook.confidence < 0.5:
            advice.append("Strengthen your opening line using one of the 20 proven hook formulas (e.g., F01 Obituary, F05 Hard Numbers).")
        if char_count > 2500:
            advice.append("Draft is nearing the 3,000-character LinkedIn ceiling. Consider tightening the middle section.")

        return AuditResult(
            slop_score=slop_score,
            slop_rating=rating,
            flagged_terms=flagged,
            hook=hook,
            character_count=char_count,
            word_count=word_count,
            reading_time_seconds=reading_time,
            advice=advice,
        )

    @classmethod
    def classify_hook(cls, text: str) -> Optional[HookClassification]:
        """Detect the hook formula of the first 2-3 lines of text."""
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        if not lines:
            return None

        # Inspect first 1-2 lines for hook classification
        opening = " ".join(lines[:2])

        for formula in HOOK_FORMULAS:
            if re.search(formula["pattern"], opening):
                return HookClassification(
                    formula_id=formula["id"],
                    formula_name=formula["name"],
                    confidence=0.85,
                    description=formula["description"],
                    example=formula["example"],
                )

        # Default fallback if no pattern matched
        return HookClassification(
            formula_id="GENERAL",
            formula_name="Direct Narrative",
            confidence=0.40,
            description="Informative direct opening statement.",
            example="We deployed our new protocol gateway yesterday.",
        )

    @classmethod
    def get_all_hook_formulas(cls) -> List[Dict[str, Any]]:
        """Return full catalog of 20 viral formulas for UI dropdowns and documentation."""
        return HOOK_FORMULAS
