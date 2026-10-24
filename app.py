"""
Flask Web Application & REST API for Intelligent Customer Feedback & Aspect Analyzer.
"""

import os
import io
import csv
import json
import traceback
from flask import Flask, request, jsonify, send_from_directory, Response
from core import AspectExtractor, TransformerSentimentEngine, IntentAnalyzer, InsightsEngine, DOMAIN_TAXONOMIES

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["JSON_SORT_KEYS"] = False

# Lazy-loaded singleton engines
print("[App] Initializing NLP and Transformer pipelines...")
sentiment_engine = TransformerSentimentEngine()
aspect_extractor = AspectExtractor()
intent_analyzer = IntentAnalyzer()
print("[App] Pipelines ready.")

# Custom in-memory taxonomies
runtime_taxonomies = dict(DOMAIN_TAXONOMIES)


def analyze_single_feedback(text: str, domain: str = "auto", review_id: str = None, customer: str = None) -> dict:
    """Helper to run complete end-to-end ABSA analysis on a single text."""
    if not text or not text.strip():
        return {
            "id": review_id or "REV-000",
            "customer": customer or "Anonymous",
            "text": "",
            "overall_sentiment": {"label": "NEUTRAL", "confidence": 0.5, "net_score": 0.0},
            "aspects": [],
            "intent": {
                "primary_intent": "General Inquiry / Feedback",
                "urgency_score": 1.0,
                "priority": "LOW",
                "action_desc": "No action needed",
                "badge_color": "success"
            },
            "insights": {
                "summary": "Empty feedback.",
                "strengths": [],
                "friction_points": [],
                "recommendations": []
            },
            "annotated_spans": []
        }

    # 1. Overall sentiment
    overall_sentiment = sentiment_engine.predict_sentiment(text)

    # 2. Extract aspects
    raw_aspects = aspect_extractor.extract_aspects(text, domain=domain)

    # 3. Targeted aspect sentiment scoring
    analyzed_aspects = []
    for asp in raw_aspects:
        aspect_res = sentiment_engine.analyze_aspect_sentiment(asp)
        analyzed_aspects.append(aspect_res)

    # 4. Intent & Urgency
    intent_res = intent_analyzer.analyze(text, overall_sentiment["label"], analyzed_aspects)

    # 5. Executive Insights & Recommendations
    review_package = {
        "id": review_id or "REV-001",
        "customer": customer or "Customer",
        "text": text,
        "overall_sentiment": overall_sentiment,
        "aspects": analyzed_aspects,
        "intent": intent_res
    }
    insights_res = InsightsEngine.generate_single_review_insights(review_package)

    # 6. Build text highlight spans for rich UI
    annotated_spans = []
    for a in analyzed_aspects:
        if a.get("start") is not None and a.get("end") is not None:
            annotated_spans.append({
                "start": a["start"],
                "end": a["end"],
                "text": text[a["start"]:a["end"]],
                "aspect": a["aspect"],
                "sentiment": a["sentiment"],
                "color": "#10b981" if a["sentiment"] == "POSITIVE" else ("#ef4444" if a["sentiment"] == "NEGATIVE" else "#94a3b8")
            })

    review_package["insights"] = insights_res
    review_package["annotated_spans"] = annotated_spans
    return review_package


@app.route("/")
def index():
    """Serves the main web dashboard."""
    return send_from_directory("static", "index.html")


@app.route("/api/health", methods=["GET"])
def health():
    """Healthcheck endpoint."""
    return jsonify({
        "status": "healthy",
        "model": "distilbert-base-uncased-finetuned-sst-2-english",
        "framework": "PyTorch + Hugging Face Transformers",
        "version": "1.0.0"
    })


@app.route("/api/taxonomies", methods=["GET", "POST"])
def manage_taxonomies():
    """Get available domain taxonomies or register custom aspects."""
    global aspect_extractor, runtime_taxonomies
    if request.method == "POST":
        data = request.get_json() or {}
        dom_id = data.get("domain_id", "custom")
        aspect_name = data.get("aspect_name")
        keywords = data.get("keywords", [])

        if not aspect_name or not keywords:
            return jsonify({"error": "Missing aspect_name or keywords list"}), 400

        if dom_id not in runtime_taxonomies:
            runtime_taxonomies[dom_id] = {
                "name": data.get("domain_name", "Custom Domain"),
                "description": "User defined taxonomy",
                "aspects": {}
            }

        runtime_taxonomies[dom_id]["aspects"][aspect_name] = [k.strip().lower() for k in keywords if k.strip()]
        aspect_extractor = AspectExtractor(custom_taxonomies=runtime_taxonomies)

        return jsonify({
            "status": "success",
            "message": f"Aspect '{aspect_name}' added to domain '{dom_id}'.",
            "taxonomies": runtime_taxonomies
        })

    return jsonify(runtime_taxonomies)


@app.route("/api/sample-datasets", methods=["GET"])
def get_sample_datasets():
    """Returns bundled real-world customer review datasets."""
    datasets = {}
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if os.path.exists(data_dir):
        for f in os.listdir(data_dir):
            if f.endswith(".json"):
                key = f.replace("sample_", "").replace(".json", "")
                try:
                    with open(os.path.join(data_dir, f), "r", encoding="utf-8") as fp:
                        datasets[key] = json.load(fp)
                except Exception as e:
                    print(f"Error loading {f}: {e}")
    return jsonify(datasets)


@app.route("/api/analyze", methods=["POST"])
def analyze_single():
    """Analyzes a single piece of customer feedback."""
    try:
        data = request.get_json() or {}
        text = data.get("text", "")
        domain = data.get("domain", "auto")

        if not text:
            return jsonify({"error": "Please provide 'text' to analyze"}), 400

        result = analyze_single_feedback(
            text=text,
            domain=domain,
            review_id=data.get("id"),
            customer=data.get("customer")
        )
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze-batch", methods=["POST"])
def analyze_batch():
    """Analyzes a batch of customer reviews and produces aggregated analytics."""
    try:
        items_to_analyze = []
        domain = "auto"

        # Check if multipart form upload with CSV or JSON file
        if "file" in request.files:
            file = request.files["file"]
            filename = file.filename.lower()
            content = file.read().decode("utf-8", errors="ignore")

            if filename.endswith(".csv"):
                reader = csv.DictReader(io.StringIO(content))
                for idx, row in enumerate(reader):
                    # Find review text column
                    text_col = None
                    for c in ["text", "review", "feedback", "comment", "content", "body"]:
                        if c in [k.lower() for k in row.keys()]:
                            for actual_k in row.keys():
                                if actual_k.lower() == c:
                                    text_col = actual_k
                                    break
                            break
                    if not text_col and row:
                        text_col = list(row.keys())[0] # Fallback to first column

                    items_to_analyze.append({
                        "id": row.get("id", f"CSV-{idx+1}"),
                        "customer": row.get("customer", row.get("name", f"Customer #{idx+1}")),
                        "text": row.get(text_col, ""),
                        "category": row.get("category", "General")
                    })
            elif filename.endswith(".json"):
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    items_to_analyze = parsed
                elif isinstance(parsed, dict) and "reviews" in parsed:
                    items_to_analyze = parsed["reviews"]
        else:
            # JSON payload
            data = request.get_json() or {}
            domain = data.get("domain", "auto")
            raw_reviews = data.get("reviews", [])

            # Or preset key like 'tech', 'saas', 'ecommerce'
            preset = data.get("preset")
            if preset:
                preset_path = os.path.join(os.path.dirname(__file__), "data", f"sample_{preset}.json")
                if os.path.exists(preset_path):
                    with open(preset_path, "r", encoding="utf-8") as fp:
                        raw_reviews = json.load(fp)

            for idx, r in enumerate(raw_reviews):
                if isinstance(r, str):
                    items_to_analyze.append({
                        "id": f"REV-{idx+1}",
                        "customer": f"Customer #{idx+1}",
                        "text": r
                    })
                elif isinstance(r, dict):
                    items_to_analyze.append(r)

        if not items_to_analyze:
            return jsonify({"error": "No reviews found to analyze"}), 400

        # Run analysis on all reviews
        analyzed_reviews = []
        for idx, item in enumerate(items_to_analyze):
            txt = item.get("text", "")
            r_id = item.get("id", f"REV-{idx+1}")
            cust = item.get("customer", f"Customer #{idx+1}")
            res = analyze_single_feedback(text=txt, domain=domain, review_id=r_id, customer=cust)
            if "rating" in item:
                res["rating"] = item["rating"]
            if "category" in item:
                res["category"] = item["category"]
            analyzed_reviews.append(res)

        # Generate portfolio-level analytics and quadrant matrix
        analytics = InsightsEngine.generate_batch_analytics(analyzed_reviews)

        return jsonify({
            "status": "success",
            "count": len(analyzed_reviews),
            "reviews": analyzed_reviews,
            "analytics": analytics
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/export", methods=["POST"])
def export_results():
    """Exports batch analysis results into CSV."""
    try:
        data = request.get_json() or {}
        reviews = data.get("reviews", [])
        fmt = data.get("format", "csv").lower()

        if fmt == "json":
            return Response(
                json.dumps(reviews, indent=2),
                mimetype="application/json",
                headers={"Content-Disposition": "attachment;filename=absa_feedback_analysis.json"}
            )

        # CSV Export
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Review ID", "Customer", "Review Text", "Overall Sentiment", "Net Sentiment Score",
            "Urgency Score", "Priority", "Primary Intent", "Detected Aspects", "Strengths",
            "Friction Points", "Action Recommendations"
        ])

        for r in reviews:
            aspect_summary = "; ".join([f"{a['aspect']} ({a['sentiment']})" for a in r.get("aspects", [])])
            insights = r.get("insights", {})
            writer.writerow([
                r.get("id", ""),
                r.get("customer", ""),
                r.get("text", "").replace("\n", " "),
                r.get("overall_sentiment", {}).get("label", ""),
                r.get("overall_sentiment", {}).get("net_score", 0.0),
                r.get("intent", {}).get("urgency_score", ""),
                r.get("intent", {}).get("priority", ""),
                r.get("intent", {}).get("primary_intent", ""),
                aspect_summary,
                ", ".join(insights.get("strengths", [])),
                ", ".join(insights.get("friction_points", [])),
                " | ".join(insights.get("recommendations", []))
            ])

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=absa_feedback_analysis.csv"}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n==================================================================")
    print(f"  Intelligent Customer Feedback & Aspect Analyzer (Transformers)")
    print(f"  Server running at: http://localhost:{port}")
    print(f"==================================================================\n")
    app.run(host="127.0.0.1", port=port, debug=False)
