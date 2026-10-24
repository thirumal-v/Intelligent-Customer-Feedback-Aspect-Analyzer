"""
Customer Intent, Urgency Scoring, and Actionability Detection Engine.
"""

import re
from typing import Dict, Any, List
from core.config import INTENT_MARKERS


class IntentAnalyzer:
    def __init__(self):
        self.markers = INTENT_MARKERS

    def analyze(self, text: str, overall_sentiment: str, aspects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classifies customer intent, calculates urgency index (1-10),
        and assigns an operational action priority (CRITICAL, HIGH, MEDIUM, LOW).
        """
        text_lower = text.lower()
        detected_intents = []
        intent_scores = {}

        for intent_name, keywords in self.markers.items():
            score = 0
            matched_terms = []
            for kw in keywords:
                pattern = r'\b' + re.escape(kw) + r'\b'
                matches = list(re.finditer(pattern, text_lower))
                if matches:
                    score += len(matches)
                    matched_terms.append(kw)

            if score > 0:
                detected_intents.append({
                    "intent": intent_name,
                    "matched_markers": matched_terms,
                    "strength": score
                })
                intent_scores[intent_name] = score

        # Default fallback intent if none matched
        if not detected_intents:
            if overall_sentiment == "POSITIVE":
                primary_intent = "Praise / Delight"
            elif overall_sentiment == "NEGATIVE":
                primary_intent = "Customer Support Issue"
            else:
                primary_intent = "General Inquiry / Feedback"
        else:
            # Sort by priority and match strength
            # Churn and Bug carry higher business priority
            priority_weights = {
                "Churn Risk / Escalation": 2.5,
                "Billing / Refund Request": 2.0,
                "Bug / Technical Issue": 1.8,
                "Customer Support Issue": 1.5,
                "Feature Request": 1.2,
                "Praise / Delight": 1.0,
                "General Inquiry / Feedback": 0.8
            }
            sorted_intents = sorted(
                detected_intents,
                key=lambda x: x["strength"] * priority_weights.get(x["intent"], 1.0),
                reverse=True
            )
            primary_intent = sorted_intents[0]["intent"]

        # Calculate Urgency Score (1 to 10)
        urgency = 2.0 # Baseline

        # Intent urgency contributions
        if "Churn Risk / Escalation" in intent_scores:
            urgency += 4.5
        if "Billing / Refund Request" in intent_scores:
            urgency += 3.0
        if "Bug / Technical Issue" in intent_scores:
            urgency += 2.5
        if "Customer Support Issue" in intent_scores:
            urgency += 1.5
        if "Praise / Delight" in intent_scores:
            urgency -= 1.0

        # Negative aspect density
        neg_aspects = [a for a in aspects if a.get("sentiment") == "NEGATIVE"]
        urgency += min(len(neg_aspects) * 0.8, 2.5)

        # Text intensity cues: exclamation points, all-caps words
        exclamation_count = text.count("!")
        if exclamation_count >= 2:
            urgency += min(exclamation_count * 0.4, 1.5)

        caps_words = [w for w in text.split() if w.isupper() and len(w) > 2 and w not in {"NOT", "AND", "THE", "BUT"}]
        if len(caps_words) >= 2:
            urgency += 1.2

        # Overall sentiment modifier
        if overall_sentiment == "NEGATIVE":
            urgency += 1.0
        elif overall_sentiment == "POSITIVE":
            urgency = min(urgency, 3.0)

        urgency_score = round(max(1.0, min(10.0, urgency)), 1)

        # Operational Priority
        if urgency_score >= 7.5:
            priority = "CRITICAL"
            action_desc = "Immediate Escalation / Retain At-Risk Customer"
            badge_color = "danger"
        elif urgency_score >= 5.5:
            priority = "HIGH"
            action_desc = "Fast-track Resolution / Technical Support"
            badge_color = "warning"
        elif urgency_score >= 3.5:
            priority = "MEDIUM"
            action_desc = "Product Backlog / Standard Queue"
            badge_color = "info"
        else:
            priority = "LOW"
            action_desc = "Acknowledge / Community & Praise"
            badge_color = "success"

        return {
            "primary_intent": primary_intent,
            "all_intents": detected_intents,
            "urgency_score": urgency_score,
            "priority": priority,
            "action_desc": action_desc,
            "badge_color": badge_color
        }
