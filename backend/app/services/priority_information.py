"""Detect sparse descriptions without evidence for a base priority."""
import re

POLICY_VERSION = "en-sparse-priority-v3"

# On the development pilot, weak descriptions with known priorities have at
# most 16 words and complete descriptions start at 24. Use the midpoint as a
# scope for review, with exceptions for short but informative descriptions.
MAX_SPARSE_WORDS = 20
WORDS = re.compile(r"\b\w+\b")
NO_DISRUPTION = re.compile(
    r"\b(?:can (?:still )?work normally|work(?: task)? (?:is |remains? )?unaffected|"
    r"(?:does not|doesn't) (?:affect my work|slow me down)|no impact on (?:my )?work)\b|"
    r"\b(?:i|we) can work$"
)
WORKING_ALTERNATIVE = re.compile(
    r"\b(?:can (?:still )?(?:work|finish|continue|complete|print)\b.{0,40}\b(?:using|via)\b|"
    r"(?:backup|spare|borrowed|alternative|workaround|usb mouse|web version)\b.{0,28}\b(?:works|lets me|allows me)\b|"
    r"(?:works|working|can work) (?:over|via|using) (?:wi-fi|ethernet|a cable|the browser)|"
    r"(?:colleague|teammate) (?:sends|shares|provides)\b)"
)
UNSUCCESSFUL = re.compile(r"\b(?:no|never|not|cannot|can't|doesn't|tried|trying|failed|fails)\b")
UNCERTAIN = re.compile(r"\b(?:not sure|don't know|cannot confirm|can't say|cannot say)\b")
CONDITIONAL = re.compile(r"\b(?:if|unless|provided that|as long as|once (?:i|we|it|you|they|the))\b")
BLOCKED_WORK = re.compile(
    r"\b(?:(?:cannot|can't|unable to) (?:work|finish|complete|continue|process|send)\b|"
    r"(?:task|work|inspection|processing|team|service|validation)\b[^.!?;,\n]{0,24}?\b(?:blocked|stopped|down|cannot be completed)|"
    r"(?:orders|parcels|deliveries) are waiting|(?:contract|submission|report) due today|"
    r"(?:nobody can take orders|no orders can be taken))\b"
)
NEGATED_BLOCKAGE = re.compile(r"\b(?:not|never|no longer|isn't|aren't|wasn't|weren't)\b")
NO_ALTERNATIVE = re.compile(
    r"\b(?:no (?:working |other |approved )?(?:workaround|alternative|fallback|backup|spare|replacement|route|way|other connection)|"
    r"only this (?:program|tool|application) is (?:permitted|allowed))\b"
)


def needs_priority_information(description: str) -> bool:
    text = description.casefold().replace("’", "'")
    if len(WORDS.findall(text)) > MAX_SPARSE_WORDS:
        return False
    # Keep comma-separated conditions attached to the claim they qualify.
    for segment in re.split(r"[.!?;\n]+|\b(?:but|however)\b", text):
        if CONDITIONAL.search(segment):
            continue
        for clause in segment.split(","):
            clause = clause.strip()
            if NO_DISRUPTION.search(clause) and not UNCERTAIN.search(clause):
                return False
            if WORKING_ALTERNATIVE.search(clause) and not UNSUCCESSFUL.search(clause):
                return False
    blocked = any(not NEGATED_BLOCKAGE.search(match.group()) for match in BLOCKED_WORK.finditer(text))
    return not (blocked and NO_ALTERNATIVE.search(text))
