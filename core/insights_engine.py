"""
Executive Insights, Actionable Recommendations, and Aspect Quadrant Matrix Generator.
"""

from typing import List, Dict, Any
from collections import defaultdict


class InsightsEngine:
    @staticmethod
    def generate_single_review_insights(review_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates executive summary and targeted action items for an individual customer review.
        """
        aspects = review_data.get("aspects", [])
        overall_sentiment = review_data.get("overall_sentiment", {})
        intent_data = review_data.get("intent", {})

        pos_aspects = [a["aspect"] for a in aspects if a["sentiment"] == "POSITIVE"]
        neg_aspects = [a["aspect"] for a in aspects if a["sentiment"] == "NEGATIVE"]
        neu_aspects = [a["aspect"] for a in aspects if a["sentiment"] == "NEUTRAL"]

        recommendations = []

        if intent_data.get("priority") == "CRITICAL":
            recommendations.append("URGENT: Initiate high-priority customer outreach within 2 hours to prevent churn or public escalation.")
        
        if "Churn Risk / Escalation" in intent_data.get("primary_intent", ""):
            recommendations.append("Offer retention compensation, expedited refund, or dedicated account manager support.")

        if "Bug / Technical Issue" in intent_data.get("primary_intent", ""):
            recommendations.append("Log a priority defect ticket with engineering. Collect client environment and reproduction details.")

        for neg in neg_aspects:
            if "Shipping" in neg or "Delivery" in neg:
                recommendations.append(f"Audit carrier performance and tracking accuracy regarding '{neg}'.")
            elif "Support" in neg or "Staff" in neg:
                recommendations.append(f"Review support agent communication logs and response SLAs for '{neg}'.")
            elif "Pricing" in neg or "Billing" in neg:
                recommendations.append(f"Verify billing transparency or review discount incentives for '{neg}'.")
            elif "UI" in neg or "Performance" in neg:
                recommendations.append(f"Feed UX friction feedback for '{neg}' into upcoming sprint planning.")
            elif "Quality" in neg or "Battery" in neg or "Display" in neg:
                recommendations.append(f"Alert QA and hardware/product reliability team regarding '{neg}'.")

        if pos_aspects and not neg_aspects:
            recommendations.append("Request a public testimonial, 5-star marketplace review, or refer-a-friend incentive.")

        if not recommendations:
            recommendations.append("Standard feedback logged into product analytics. No immediate escalation needed.")

        # Construct summary sentence
        if pos_aspects and neg_aspects:
            summary = f"Mixed sentiment: Customer praised {', '.join(pos_aspects[:2])}, but expressed strong dissatisfaction with {', '.join(neg_aspects[:2])}."
        elif pos_aspects:
            summary = f"Highly positive review emphasizing outstanding performance in {', '.join(pos_aspects[:3])}."
        elif neg_aspects:
            summary = f"Critical negative feedback highlighting significant pain points in {', '.join(neg_aspects[:3])}."
        else:
            summary = f"Neutral or informational customer observation with no distinct aspect friction."

        return {
            "summary": summary,
            "strengths": list(set(pos_aspects)),
            "friction_points": list(set(neg_aspects)),
            "neutral_aspects": list(set(neu_aspects)),
            "recommendations": recommendations[:4]
        }

    @staticmethod
    def generate_batch_analytics(reviews_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates multiple analyzed customer reviews into portfolio-level aspect scorecards,
        Net Aspect Sentiment Scores (NASS), and 2x2 priority quadrant matrices.
        """
        total_reviews = len(reviews_results)
        if total_reviews == 0:
            return {}

        aspect_stats = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0, "total": 0, "clauses": []})
        intent_counts = defaultdict(int)
        overall_counts = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
        total_urgency = 0.0

        for r in reviews_results:
            overall_lbl = r.get("overall_sentiment", {}).get("label", "NEUTRAL")
            overall_counts[overall_lbl] += 1

            intent_lbl = r.get("intent", {}).get("primary_intent", "General")
            intent_counts[intent_lbl] += 1

            total_urgency += r.get("intent", {}).get("urgency_score", 3.0)

            for asp in r.get("aspects", []):
                name = asp["aspect"]
                sent = asp["sentiment"]
                aspect_stats[name]["total"] += 1
                if sent == "POSITIVE":
                    aspect_stats[name]["positive"] += 1
                elif sent == "NEGATIVE":
                    aspect_stats[name]["negative"] += 1
                else:
                    aspect_stats[name]["neutral"] += 1
                if len(aspect_stats[name]["clauses"]) < 3:
                    aspect_stats[name]["clauses"].append(asp.get("clause", ""))

        # Calculate Net Aspect Sentiment Score (NASS) and Quadrant Positioning
        aspect_scorecards = []
        frequencies = [data["total"] for data in aspect_stats.values()]
        avg_frequency = (sum(frequencies) / len(frequencies)) if frequencies else 1

        for name, data in aspect_stats.items():
            tot = data["total"]
            pos = data["positive"]
            neg = data["negative"]
            neu = data["neutral"]
            
            # Net Sentiment Score: -100 to +100
            nass = round(((pos - neg) / tot) * 100, 1) if tot > 0 else 0.0

            # Quadrant logic:
            # X-axis: Frequency (Relative to avg_frequency)
            # Y-axis: Net Sentiment Score (-100 to +100)
            is_high_freq = tot >= avg_frequency
            is_positive = nass >= 0

            if is_high_freq and not is_positive:
                quadrant = "Critical Firefighting"
                quadrant_desc = "High impact friction driving churn. Requires immediate fix."
                color = "#ef4444"
            elif is_high_freq and is_positive:
                quadrant = "Core Brand Pillar"
                quadrant_desc = "Primary strength driving satisfaction. Highlight in marketing."
                color = "#10b981"
            elif not is_high_freq and not is_positive:
                quadrant = "Emerging Friction"
                quadrant_desc = "Niche or emerging complaints. Monitor closely."
                color = "#f59e0b"
            else:
                quadrant = "Hidden Delighter"
                quadrant_desc = "High satisfaction feature with low awareness. Promote wider."
                color = "#6366f1"

            aspect_scorecards.append({
                "aspect": name,
                "total_mentions": tot,
                "mention_rate": round((tot / total_reviews) * 100, 1),
                "positive": pos,
                "neutral": neu,
                "negative": neg,
                "net_sentiment_score": nass,
                "quadrant": quadrant,
                "quadrant_desc": quadrant_desc,
                "quadrant_color": color,
                "sample_clauses": data["clauses"]
            })

        # Sort scorecards by total mentions descending
        aspect_scorecards.sort(key=lambda x: x["total_mentions"], reverse=True)

        # Strategic Action Items
        top_danger_aspects = [a for a in aspect_scorecards if a["quadrant"] == "Critical Firefighting"]
        top_strengths = [a for a in aspect_scorecards if a["quadrant"] == "Core Brand Pillar"]

        strategic_actions = []
        for a in top_danger_aspects[:3]:
            strategic_actions.append({
                "title": f"Mitigate Dissatisfaction in {a['aspect']}",
                "priority": "HIGH",
                "impact": f"{a['negative']} negative reviews ({a['mention_rate']}% of all feedback)",
                "action": f"Assemble cross-functional team to address core issues in {a['aspect']}. Net sentiment currently at {a['net_sentiment_score']}%."
            })

        for a in top_strengths[:2]:
            strategic_actions.append({
                "title": f"Leverage {a['aspect']} in Product Messaging",
                "priority": "MEDIUM",
                "impact": f"{a['positive']} positive mentions ({a['net_sentiment_score']}% net score)",
                "action": f"Feature {a['aspect']} prominently in landing pages and sales enablement materials."
            })

        return {
            "total_reviews": total_reviews,
            "overall_sentiment_distribution": {
                "positive": overall_counts["POSITIVE"],
                "neutral": overall_counts["NEUTRAL"],
                "negative": overall_counts["NEGATIVE"],
                "positive_pct": round((overall_counts["POSITIVE"] / total_reviews) * 100, 1),
                "neutral_pct": round((overall_counts["NEUTRAL"] / total_reviews) * 100, 1),
                "negative_pct": round((overall_counts["NEGATIVE"] / total_reviews) * 100, 1)
            },
            "intent_distribution": dict(intent_counts),
            "average_urgency": round(total_urgency / total_reviews, 1),
            "aspect_scorecards": aspect_scorecards,
            "strategic_actions": strategic_actions
        }
