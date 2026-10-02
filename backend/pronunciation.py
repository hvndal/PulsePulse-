import re
from typing import List, Optional
from backend.models import PronunciationRule

class PronunciationEngine:
    """
    Manages custom phonetic dictionaries and IPA replacements.
    Applies overrides to script text before text-to-speech synthesis.
    """

    def __init__(self, global_rules: Optional[List[PronunciationRule]] = None):
        self.global_rules = global_rules or []

    def apply_rules(
        self,
        text: str,
        project_rules: Optional[List[PronunciationRule]] = None
    ) -> str:
        rules = list(self.global_rules)
        if project_rules:
            rules.extend(project_rules)

        if not rules:
            return text

        processed_text = text
        for rule in rules:
            pattern = re.compile(re.escape(rule.original_word), re.IGNORECASE)
            replacement = rule.replacement_phonetic
            if rule.is_ipa:
                replacement = f"[[ipa:{rule.replacement_phonetic}]]"
            processed_text = pattern.sub(replacement, processed_text)

        return processed_text
