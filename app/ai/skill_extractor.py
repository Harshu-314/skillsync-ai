"""
app/ai/skill_extractor.py

Extracts skills from free text by exact phrase matching against a
known skill taxonomy (name + aliases), using spaCy's PhraseMatcher.

Why PhraseMatcher over a trained NLP pipeline or embeddings:
    We already have a controlled vocabulary (the skills table). This
    is "does any of these known phrases appear in this text" — not
    open-ended entity recognition, and not a fuzzy semantic-similarity
    problem (that's Sprint 6's job, comparing resume skills against
    job-demand skills). PhraseMatcher gives fast, deterministic,
    word-boundary-aware matching without needing a trained model
    (en_core_web_sm) or embeddings — spacy.blank("en") is sufficient
    since only tokenization is needed, not POS tagging or NER.

Pure function, no Flask/DB dependency: takes a text string and a list
of already-loaded Skill objects, returns a list of Skill objects.
This makes it trivially unit-testable in isolation and reusable
anywhere (not just the resume upload flow) without pulling in Flask
request/app context.
"""

import json

import spacy
from spacy.matcher import PhraseMatcher

from app.models.skill import Skill

# Built once per call (not module-level) since spacy.blank("en") is
# cheap (no trained pipeline loaded) — module-level caching would be
# a premature optimization for this project's scale and would add
# state that complicates testing (e.g. a newly seeded skill wouldn't
# be picked up without a process restart).


def extract_skills(text: str, skills: list[Skill]) -> list[Skill]:
    """
    Finds which skills from the given taxonomy appear in the given
    text, matching on each skill's canonical name and its aliases.

    Args:
        text: The text to search (e.g. a resume's raw_text).
        skills: The full skill taxonomy to match against — the
            caller is responsible for fetching this (via
            SkillRepository.get_all()), keeping this function free
            of any database access.

    Returns:
        A list of matched Skill objects, each appearing at most once
        even if the skill (or one of its aliases) appears multiple
        times in the text. Order follows first-occurrence position in
        the text. Returns an empty list if no skills matched or if
        text is empty — this is a valid, non-error outcome.
    """
    if not text or not text.strip() or not skills:
        return []

    nlp = spacy.blank("en")
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    # Maps spaCy's internal match_id (an integer hash of the string
    # label we register below) back to the actual Skill object, so
    # a match can be resolved back to full skill data, not just an id.
    match_id_to_skill: dict[int, Skill] = {}

    for skill in skills:
        phrases = [skill.name] + _parse_aliases(skill.aliases)
        patterns = [nlp.make_doc(phrase) for phrase in phrases if phrase.strip()]
        if not patterns:
            continue

        label = str(skill.id)
        matcher.add(label, patterns)
        match_id_to_skill[nlp.vocab.strings[label]] = skill

    doc = nlp(text)
    matches = matcher(doc)

    # PhraseMatcher does not guarantee matches are returned in text-
    # position order — sort explicitly so "first-occurrence order" in
    # the docstring above is actually guaranteed, not assumed.
    matches = sorted(matches, key=lambda m: m[1])

    # Deduplicate: a skill (or one of its aliases) may appear many
    # times in a resume, but should only be recorded once. Preserve
    # first-occurrence order by iterating matches in (now guaranteed)
    # position order and skipping anything already seen.
    seen_skill_ids: set[int] = set()
    matched_skills: list[Skill] = []

    for match_id, _start, _end in matches:
        skill = match_id_to_skill.get(match_id)
        if skill and skill.id not in seen_skill_ids:
            seen_skill_ids.add(skill.id)
            matched_skills.append(skill)

    return matched_skills


def _parse_aliases(aliases_json: str | None) -> list[str]:
    """
    Parses a Skill's aliases field (a JSON array string, or None)
    into a plain list of strings. Malformed JSON is treated as "no
    aliases" rather than raising — extraction should degrade
    gracefully on bad seed data, not crash the whole request.

    Args:
        aliases_json: The raw aliases column value.

    Returns:
        A list of alias strings, possibly empty.
    """
    if not aliases_json:
        return []
    try:
        parsed = json.loads(aliases_json)
        if isinstance(parsed, list):
            return [str(alias) for alias in parsed]
        return []
    except (json.JSONDecodeError, TypeError):
        return []
