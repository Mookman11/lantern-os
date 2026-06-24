"""
Job Application Assistant Skill for Keystone OS (#1098)

Provides:
- Job posting analysis: extract requirements, responsibilities, signals
- Resume tailoring: reframe user background bullets to match the posting
- Document generation: build resume + cover letter HTML in the user workspace

All analysis uses only user-supplied background and the extracted posting text.
No experience is fabricated. (Σ₀ External Reality Rule)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class JobPostingAnalysis:
    """Structured extraction from a raw job posting."""
    company: str = ""
    role: str = ""
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    key_responsibilities: List[str] = field(default_factory=list)
    signals: List[str] = field(default_factory=list)  # tone / culture / tech signals
    raw_text_length: int = 0

    def to_dict(self) -> dict:
        return {
            "company": self.company,
            "role": self.role,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "key_responsibilities": self.key_responsibilities,
            "signals": self.signals,
            "raw_text_length": self.raw_text_length,
        }


@dataclass
class TailoringResult:
    """Tailored resume bullets + cover letter opening for a specific posting."""
    tailored_bullets: List[str]
    cover_letter_opening: str
    matched_skills: List[str]   # user skills that appear in the posting
    gap_skills: List[str]       # required skills the user didn't mention
    confidence: float           # 0-1; how many required skills matched / total required

    def to_dict(self) -> dict:
        return {
            "tailored_bullets": self.tailored_bullets,
            "cover_letter_opening": self.cover_letter_opening,
            "matched_skills": self.matched_skills,
            "gap_skills": self.gap_skills,
            "confidence": round(self.confidence, 2),
        }


# ── Job posting analysis ──────────────────────────────────────────────────────

# Heuristic keyword sets for extracting signals from raw posting text.
_REQUIRED_MARKERS = re.compile(
    r"^[*•\-]?\s*(required|must have|must[- ]be|you (will|must)|minimum|required qualifications?)[:\s]",
    re.I | re.M,
)
_PREFERRED_MARKERS = re.compile(
    r"^[*•\-]?\s*(preferred|nice[- ]to[- ]have|bonus|desirable|a plus)[:\s]",
    re.I | re.M,
)
_RESPONSIBILITIES_MARKERS = re.compile(
    r"^[*•\-]?\s*(responsibilities|you will|in this role|what you.ll do|job duties)[:\s]?",
    re.I | re.M,
)

# Common technical and soft-skill tokens to extract from posting text.
_SKILL_TOKENS = re.compile(
    r"\b("
    r"python|javascript|typescript|java|golang|go|rust|ruby|c\+\+|c#|swift|kotlin|scala|"
    r"node(?:\.js)?|react|vue|angular|nextjs|fastapi|flask|django|express|"
    r"sql|postgresql|postgres|mysql|mongodb|redis|elasticsearch|kafka|"
    r"aws|gcp|azure|docker|kubernetes|k8s|terraform|ci/cd|github actions|jenkins|"
    r"machine learning|ml|deep learning|llm|nlp|pytorch|tensorflow|"
    r"rest(?:ful)?|graphql|grpc|api|microservices|"
    r"leadership|collaboration|communication|agile|scrum|"
    r"product thinking|system design|distributed systems|"
    r"security|authentication|authorization|"
    r"data analysis|analytics|a/b testing|"
    r"react native|ios|android|mobile"
    r")\b",
    re.I,
)


def analyze_job_posting(text: str) -> JobPostingAnalysis:
    """
    Extract structured information from raw job posting text.
    Returns a JobPostingAnalysis; does not fabricate any content.

    Args:
        text: raw text of the job posting (copy-paste or fetched)
    """
    text = str(text or "").strip()
    if not text:
        return JobPostingAnalysis()

    analysis = JobPostingAnalysis(raw_text_length=len(text))

    # ── company / role from first ~5 lines ────────────────────────────────
    header_lines = [l.strip() for l in text.splitlines()[:8] if l.strip()]
    for line in header_lines:
        # "Senior Software Engineer at Acme Corp" or "Acme Corp — SWE"
        m = re.search(r"at\s+([A-Z][^\n,|–—]{2,40})", line)
        if m and not analysis.company:
            analysis.company = m.group(1).strip()
        # If line is short and title-cased, it's likely the role
        if not analysis.role and 3 <= len(line.split()) <= 8 and line == line.title():
            analysis.role = line

    # ── skill extraction ───────────────────────────────────────────────────
    all_skills = list({m.group(0).lower() for m in _SKILL_TOKENS.finditer(text)})

    # Classify required vs preferred based on section proximity (simplified heuristic)
    req_section = ""
    pref_section = ""
    for block in re.split(r"\n{2,}", text):
        if _REQUIRED_MARKERS.search(block):
            req_section += " " + block
        elif _PREFERRED_MARKERS.search(block):
            pref_section += " " + block

    req_skills_found = {m.group(0).lower() for m in _SKILL_TOKENS.finditer(req_section)}
    pref_skills_found = {m.group(0).lower() for m in _SKILL_TOKENS.finditer(pref_section)}
    other_skills = set(all_skills) - req_skills_found - pref_skills_found

    analysis.required_skills = sorted(req_skills_found or other_skills)[:12]
    analysis.preferred_skills = sorted(pref_skills_found)[:8]

    # ── responsibilities ───────────────────────────────────────────────────
    resp_bullets: List[str] = []
    for block in re.split(r"\n{2,}", text):
        if _RESPONSIBILITIES_MARKERS.search(block):
            for line in block.splitlines():
                line = line.strip().lstrip("*•-").strip()
                if 15 < len(line) < 200:
                    resp_bullets.append(line)
    analysis.key_responsibilities = resp_bullets[:6]

    # ── tone/culture signals ───────────────────────────────────────────────
    signal_patterns = [
        (r"\bfast[- ]paced\b", "fast-paced environment"),
        (r"\bremote\b|\bhybrid\b", "remote/hybrid work"),
        (r"\bstartup\b", "startup culture"),
        (r"\bopen[- ]source\b", "open-source contributor culture"),
        (r"\bwelfare|wellbeing|wellness\b", "employee wellness focus"),
        (r"\bmentorship|mentoring\b", "mentorship culture"),
        (r"\bdiversity|inclusive\b", "DEI commitment"),
        (r"\bequity|stock|rsu|esop\b", "equity compensation"),
    ]
    for pattern, label in signal_patterns:
        if re.search(pattern, text, re.I):
            analysis.signals.append(label)

    return analysis


# ── Tailoring ─────────────────────────────────────────────────────────────────

def tailor_highlights(
    analysis: JobPostingAnalysis,
    background: Dict,
) -> TailoringResult:
    """
    Given a posting analysis and user background, return tailored resume bullets
    and a cover letter opening.

    background dict keys (all optional):
        name, skills (list[str] or csv), experience (list[{title,company,dates,bullets[]}]),
        summary, email, location
    """
    user_skills_raw = background.get("skills") or []
    if isinstance(user_skills_raw, str):
        user_skills_raw = [s.strip() for s in user_skills_raw.split(",")]
    user_skills_lower = {s.lower() for s in user_skills_raw}

    # Match user skills against posting requirements
    required_lower = {s.lower() for s in analysis.required_skills}
    preferred_lower = {s.lower() for s in analysis.preferred_skills}
    all_posting_skills = required_lower | preferred_lower

    matched = sorted(user_skills_lower & all_posting_skills)
    gap = sorted(required_lower - user_skills_lower)

    confidence = (len(matched) / len(required_lower)) if required_lower else 0.5

    # Collect user experience bullets that mention matched skills or responsibilities
    tailored: List[str] = []
    experience = background.get("experience") or []
    for exp in experience:
        for bullet in (exp.get("bullets") or []):
            bl = bullet.lower()
            if any(sk in bl for sk in matched) or any(
                re.search(r"\b" + re.escape(resp.split()[0].lower()) + r"\b", bl)
                for resp in analysis.key_responsibilities[:3]
                if resp.split()
            ):
                tailored.append(bullet)

    # Limit to 6 most relevant; fall back to all bullets if no match
    if not tailored and experience:
        tailored = [b for exp in experience for b in (exp.get("bullets") or [])][:4]
    tailored = tailored[:6]

    # Cover letter opening
    role = analysis.role or "this role"
    company = analysis.company or "your company"
    skill_mention = f" with expertise in {', '.join(matched[:3])}" if matched else ""
    opening = (
        f"I am excited to apply for the {role} position at {company}. "
        f"My background{skill_mention} aligns well with the requirements described in the posting."
    )

    return TailoringResult(
        tailored_bullets=tailored,
        cover_letter_opening=opening,
        matched_skills=matched,
        gap_skills=gap,
        confidence=confidence,
    )


# ── Document output ───────────────────────────────────────────────────────────

def build_application_summary(
    name: str,
    analysis: JobPostingAnalysis,
    tailoring: TailoringResult,
) -> str:
    """
    Returns a plain-text application summary the user can paste into the chat
    or pass to generate_document. This is not the final doc — it's the plan step.

    Evidence rule: only user-supplied + extracted content is presented here.
    Matched skills are highlighted; gaps are flagged honestly.
    """
    lines = [
        f"# Application Summary for {analysis.role or 'the role'} at {analysis.company or 'the company'}",
        "",
        f"**Candidate:** {name}",
        f"**Skill match confidence:** {int(tailoring.confidence * 100)}% of required skills found in your background",
        "",
    ]

    if tailoring.matched_skills:
        lines += ["**Matched skills:**", ", ".join(tailoring.matched_skills), ""]

    if tailoring.gap_skills:
        lines += [
            "**Skills in the posting not mentioned in your background** (address in cover letter or omit):",
            ", ".join(tailoring.gap_skills),
            "",
        ]

    if tailoring.tailored_bullets:
        lines += ["**Tailored resume bullets (from your experience):**"]
        for b in tailoring.tailored_bullets:
            lines.append(f"- {b}")
        lines.append("")

    lines += [
        "**Suggested cover letter opening:**",
        tailoring.cover_letter_opening,
        "",
        "---",
        "Next step: call `generate_document` with template=resume or cover-letter to create the final documents.",
    ]

    return "\n".join(lines)
