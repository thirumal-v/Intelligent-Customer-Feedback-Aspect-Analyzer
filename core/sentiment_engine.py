"""
Transformer-Powered Sentiment Engine using Hugging Face DistilBERT with Aspect-Targeted Context Scoring.
"""

import math
import os
from typing import List, Dict, Any, Union

# The sentiment pipeline uses PyTorch; avoid Transformers probing an unrelated TensorFlow/Keras install.
os.environ.setdefault("USE_TF", "0")

from transformers import pipeline


class TransformerSentimentEngine:
    _instance = None
    _pipeline = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TransformerSentimentEngine, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        if self._pipeline is None:
            print(f"[TransformerSentimentEngine] Initializing Hugging Face pipeline with model '{model_name}'...")
            try:
                self._pipeline = pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    device=-1, # CPU inference
                    truncation=True,
                    max_length=512
                )
                print("[TransformerSentimentEngine] Model loaded successfully.")
            except Exception as e:
                print(f"[TransformerSentimentEngine] Error loading model {model_name}: {e}")
                self._pipeline = None

    def predict_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Runs transformer inference on text and determines POSITIVE, NEUTRAL, or NEGATIVE
        along with confidence and net sentiment score (-100 to +100).
        """
        if not text or not text.strip():
            return {
                "label": "NEUTRAL",
                "score": 0.5,
                "net_score": 0.0,
                "pos_prob": 0.5,
                "neg_prob": 0.5
            }

        # Handle very short / neutral strings
        cleaned = text.strip()
        
        try:
            if self._pipeline:
                raw_res = self._pipeline(cleaned[:512])[0]
                label = raw_res["label"].upper() # 'POSITIVE' or 'NEGATIVE'
                score = float(raw_res["score"])
            else:
                # Fallback if pipeline failed
                label = "POSITIVE" if "good" in cleaned.lower() else "NEGATIVE"
                score = 0.8
        except Exception as e:
            print(f"[predict_sentiment] Inference error: {e}")
            label = "NEUTRAL"
            score = 0.5

        # SST-2 is binary (POSITIVE / NEGATIVE). If confidence is near the boundary (e.g. 0.50 - 0.62)
        # or if the text contains neutral statements without strong polarity cues, treat as NEUTRAL.
        is_neutral = False
        if score < 0.65:
            is_neutral = True
            final_label = "NEUTRAL"
            net_score = (score - 0.5) * 40 * (1 if label == "POSITIVE" else -1)
            pos_prob = score if label == "POSITIVE" else (1.0 - score)
            neg_prob = 1.0 - pos_prob
        else:
            final_label = label
            if label == "POSITIVE":
                net_score = round(score * 100, 1)
                pos_prob = round(score, 4)
                neg_prob = round(1.0 - score, 4)
            else:
                net_score = round(-score * 100, 1)
                neg_prob = round(score, 4)
                pos_prob = round(1.0 - score, 4)

        return {
            "label": final_label,
            "confidence": round(score, 4),
            "net_score": net_score,
            "pos_prob": pos_prob,
            "neg_prob": neg_prob
        }

    def analyze_aspect_sentiment(self, aspect_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs aspect-targeted sentiment analysis by contextualizing the aspect clause.
        """
        clause = aspect_info.get("clause", "")
        aspect_name = aspect_info.get("aspect", "")
        keyword = aspect_info.get("keyword", "")
        opinion_cues = aspect_info.get("opinion_cues", [])

        # Construct aspect-focused prompt representation for transformer
        # Targeted framing helps DistilBERT resolve sentiment specifically for the aspect clause
        targeted_text = f"Regarding {keyword}: {clause}"
        res = self.predict_sentiment(clause if len(clause.split()) > 2 else targeted_text)

        # Refine with opinion cues if there's an explicit opinion keyword
        positive_cues = {"good", "great", "excellent", "superb", "amazing", "stunning", "fantastic", "awesome", "love", "loved", "fast", "smooth", "helpful", "polite"}
        negative_cues = {"bad", "terrible", "horrible", "awful", "poor", "slow", "sluggish", "lag", "buggy", "broken", "flimsy", "expensive", "rude", "useless", "worst"}

        has_pos = any(c.lower() in positive_cues for c in opinion_cues)
        has_neg = any(c.lower() in negative_cues for c in opinion_cues)

        final_label = res["label"]
        confidence = res["confidence"]
        net_score = res["net_score"]

        # Negation check: e.g. "not bad" -> positive/neutral, "not good" -> negative
        lower_clause = clause.lower()
        if "not bad" in lower_clause or "not terrible" in lower_clause:
            final_label = "POSITIVE"
            confidence = 0.75
            net_score = 65.0
        elif "not good" in lower_clause or "not great" in lower_clause or "not worth" in lower_clause:
            final_label = "NEGATIVE"
            confidence = 0.92
            net_score = -85.0
        elif has_neg and not has_pos and res["label"] == "POSITIVE" and res["confidence"] < 0.75:
            final_label = "NEGATIVE"
            confidence = 0.85
            net_score = -80.0
        elif has_pos and not has_neg and res["label"] == "NEGATIVE" and res["confidence"] < 0.75:
            final_label = "POSITIVE"
            confidence = 0.85
            net_score = 80.0

        return {
            "aspect": aspect_name,
            "domain": aspect_info.get("domain", "General"),
            "keyword": keyword,
            "clause": clause,
            "start": aspect_info.get("start"),
            "end": aspect_info.get("end"),
            "sentiment": final_label,
            "confidence": confidence,
            "net_score": net_score,
            "opinion_cues": opinion_cues
        }

    def analyze_batch_reviews(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Runs batch prediction efficiently on multiple customer feedbacks.
        """
        results = []
        if not self._pipeline:
            return [self.predict_sentiment(t) for t in texts]

        # Batch in chunks of 32 for CPU efficiency
        batch_size = 32
        for i in range(0, len(texts), batch_size):
            chunk = [t[:512] for t in texts[i:i+batch_size]]
            try:
                preds = self._pipeline(chunk)
                for p in preds:
                    lbl = p["label"].upper()
                    scr = float(p["score"])
                    if scr < 0.65:
                        lbl = "NEUTRAL"
                        net_score = 0.0
                    else:
                        net_score = round(scr * 100 if lbl == "POSITIVE" else -scr * 100, 1)
                    results.append({
                        "label": lbl,
                        "confidence": round(scr, 4),
                        "net_score": net_score
                    })
            except Exception as e:
                print(f"[analyze_batch_reviews] Chunk error: {e}")
                for t in chunk:
                    results.append(self.predict_sentiment(t))

        return results
