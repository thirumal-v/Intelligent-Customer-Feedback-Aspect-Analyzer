"""
Aspect extraction and contextual clause segmentation engine.
"""

import re
from typing import List, Dict, Any, Tuple
from core.config import DOMAIN_TAXONOMIES, CONTRASTIVE_MARKERS, SENTENCE_SPLIT_REGEX


class AspectExtractor:
    def __init__(self, custom_taxonomies: Dict[str, Any] = None):
        self.taxonomies = dict(DOMAIN_TAXONOMIES)
        if custom_taxonomies:
            self.taxonomies.update(custom_taxonomies)

    def split_into_clauses(self, text: str) -> List[Dict[str, Any]]:
        """
        Splits text into fine-grained rhetorical clauses, recognizing both sentence
        boundaries and contrastive discourse markers ('but', 'however', 'although', etc.).
        Returns list of clause dicts with text and character offsets.
        """
        clauses = []
        # First split into sentence-like blocks
        sentence_spans = []
        last_end = 0
        for match in re.finditer(SENTENCE_SPLIT_REGEX, text):
            sentence_spans.append((last_end, match.start()))
            last_end = match.end()
        if last_end < len(text):
            sentence_spans.append((last_end, len(text)))

        if not sentence_spans:
            sentence_spans = [(0, len(text))]

        for s_start, s_end in sentence_spans:
            s_text = text[s_start:s_end].strip()
            if not s_text:
                continue

            # Check for contrastive markers within the sentence
            marker_pattern = '|'.join(re.escape(m) for m in CONTRASTIVE_MARKERS)
            marker_matches = list(re.finditer(marker_pattern, s_text, flags=re.IGNORECASE))

            if not marker_matches:
                clauses.append({
                    "text": s_text,
                    "start": s_start,
                    "end": s_end
                })
            else:
                c_start = 0
                for m in marker_matches:
                    part = s_text[c_start:m.start()].strip()
                    if part:
                        clauses.append({
                            "text": part,
                            "start": s_start + c_start,
                            "end": s_start + m.start()
                        })
                    c_start = m.start()
                last_part = s_text[c_start:].strip()
                if last_part:
                    clauses.append({
                        "text": last_part,
                        "start": s_start + c_start,
                        "end": s_start + len(s_text)
                    })

        return clauses

    def extract_aspects(self, text: str, domain: str = "auto") -> List[Dict[str, Any]]:
        """
        Identifies aspects in the text, their category, matched keywords, exact offsets,
        the surrounding clause, and detected opinion modifiers.
        """
        text_lower = text.lower()
        clauses = self.split_into_clauses(text)
        detected_aspects = []

        # Determine taxonomies to search
        taxonomies_to_search = {}
        if domain in self.taxonomies:
            taxonomies_to_search = {domain: self.taxonomies[domain]}
        else:
            # Auto or all: search all domains, prioritizing matches
            taxonomies_to_search = self.taxonomies

        seen_aspect_terms = set()

        for dom_key, dom_data in taxonomies_to_search.items():
            for aspect_name, keywords in dom_data["aspects"].items():
                for kw in sorted(keywords, key=lambda k: len(k), reverse=True):
                    pattern = r'\b' + re.escape(kw) + r'\b'
                    for match in re.finditer(pattern, text_lower):
                        start_pos, end_pos = match.span()
                        matched_term = text[start_pos:end_pos]
                        
                        # Prevent overlapping duplicates on the same text span
                        span_key = (start_pos, end_pos)
                        if span_key in seen_aspect_terms:
                            continue

                        # Find matching clause
                        matching_clause = None
                        for c in clauses:
                            if c["start"] <= start_pos and end_pos <= c["end"]:
                                matching_clause = c
                                break

                        clause_text = matching_clause["text"] if matching_clause else text

                        # Extract surrounding opinion cues
                        opinion_cues = self._extract_opinion_words(clause_text, kw)

                        detected_aspects.append({
                            "aspect": aspect_name,
                            "domain": dom_data.get("name", dom_key),
                            "keyword": matched_term,
                            "start": start_pos,
                            "end": end_pos,
                            "clause": clause_text,
                            "opinion_cues": opinion_cues
                        })
                        seen_aspect_terms.add(span_key)

        # Open-domain fallback / candidate aspect discovery:
        # Detect noun phrases / compound attributes if few or no taxonomy aspects found
        if len(detected_aspects) < 2:
            open_aspects = self._extract_open_domain_candidates(text, seen_aspect_terms, clauses)
            detected_aspects.extend(open_aspects)

        # De-duplicate identical aspect entries within same clause
        unique_aspects = []
        seen_aspect_clause_pairs = set()
        for asp in detected_aspects:
            pair = (asp["aspect"], asp["clause"])
            if pair not in seen_aspect_clause_pairs:
                seen_aspect_clause_pairs.add(pair)
                unique_aspects.append(asp)

        return unique_aspects

    def _extract_opinion_words(self, clause: str, keyword: str) -> List[str]:
        """
        Extracts descriptive adjectives, adverbs, and sentiment markers near the aspect keyword.
        """
        opinion_lexicon = {
            "good", "great", "excellent", "superb", "amazing", "stunning", "fantastic",
            "awesome", "love", "loved", "fast", "speedy", "smooth", "intuitive", "helpful",
            "polite", "flawless", "durable", "sturdy", "affordable", "cheap", "clear",
            "crisp", "sharp", "bright", "vibrant", "reliable", "comfortable", "delicious",
            "bad", "terrible", "horrible", "awful", "poor", "slow", "sluggish", "laggy",
            "lag", "buggy", "broken", "flimsy", "expensive", "overpriced", "confusing",
            "rude", "unhelpful", "useless", "clunky", "dim", "blurry", "dull", "dirty",
            "noisy", "loud", "bland", "worst", "hate", "hated", "unreliable", "delayed",
            "late", "damaged", "scratched", "leaking", "disappointing", "frustrating"
        }
        words = re.findall(r'\b[a-zA-Z-]+\b', clause.lower())
        cues = [w for w in words if w in opinion_lexicon and w != keyword.lower()]
        
        # Also capture common bigrams like "very slow", "super fast", "not good", "too expensive"
        modifiers = ["very", "extremely", "super", "really", "not", "too", "pretty", "insanely", "utterly"]
        for i in range(len(words) - 1):
            if words[i] in modifiers and words[i+1] in opinion_lexicon:
                phrase = f"{words[i]} {words[i+1]}"
                if phrase not in cues:
                    cues.append(phrase)

        return cues

    def _extract_open_domain_candidates(self, text: str, seen_spans: set, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Discovers emergent/custom aspect candidates using syntactical patterns
        (e.g., 'the [adj] [noun]', '[noun] is [adj]').
        """
        candidates = []
        # Pattern: "the [word] is/was [word]" or "[word] [noun] is [adj]"
        pattern = r'\b(the\s+)?([a-zA-Z]{3,15})\s+(is|was|are|were|feels|felt|seems)\s+([a-zA-Z]+)\b'
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            full_match = match.group(0)
            target = match.group(2).capitalize()
            adj = match.group(4).lower()
            start, end = match.start(2), match.end(2)

            # Skip common non-aspect stopwords
            if target.lower() in {"it", "this", "that", "there", "what", "which", "he", "she", "they", "i", "we"}:
                continue

            if (start, end) not in seen_spans:
                # Find matching clause
                matching_clause = None
                for c in clauses:
                    if c["start"] <= start and end <= c["end"]:
                        matching_clause = c
                        break
                clause_text = matching_clause["text"] if matching_clause else full_match

                candidates.append({
                    "aspect": f"{target} (Emergent Aspect)",
                    "domain": "Discovered Aspect",
                    "keyword": target,
                    "start": start,
                    "end": end,
                    "clause": clause_text,
                    "opinion_cues": [adj]
                })
                seen_spans.add((start, end))

        return candidates
