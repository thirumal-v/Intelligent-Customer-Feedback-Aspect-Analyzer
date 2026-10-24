"""
Core Aspect-Based Sentiment Analysis and Customer Feedback Intelligence Package.
"""

from core.aspect_engine import AspectExtractor
from core.sentiment_engine import TransformerSentimentEngine
from core.intent_engine import IntentAnalyzer
from core.insights_engine import InsightsEngine
from core.config import DOMAIN_TAXONOMIES

__all__ = [
    "AspectExtractor",
    "TransformerSentimentEngine",
    "IntentAnalyzer",
    "InsightsEngine",
    "DOMAIN_TAXONOMIES"
]
