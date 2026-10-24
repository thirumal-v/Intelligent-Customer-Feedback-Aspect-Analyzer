"""
Configuration and Domain Taxonomies for Aspect-Based Sentiment Analysis (ABSA).
"""

# Pre-defined domain aspect ontologies with keywords and synonyms
DOMAIN_TAXONOMIES = {
    "ecommerce": {
        "name": "E-Commerce & Retail",
        "description": "Online shopping, product quality, packaging, delivery, and customer service",
        "aspects": {
            "Product Quality": [
                "quality", "material", "durability", "build", "sturdy", "flimsy", "fabric",
                "texture", "finish", "craftsmanship", "authentic", "counterfeit", "condition"
            ],
            "Pricing & Value": [
                "price", "cost", "value", "worth", "expensive", "cheap", "affordable",
                "overpriced", "bargain", "discount", "deal", "pricing", "money"
            ],
            "Shipping & Delivery": [
                "delivery", "shipping", "package", "packaging", "courier", "arrival", "transit",
                "box", "tracking", "late", "delayed", "fast delivery", "damaged box", "arrived"
            ],
            "Customer Support": [
                "customer service", "support", "agent", "representative", "helpdesk", "response",
                "rep", "chat", "assistance", "staff", "unhelpful", "helpful", "polite", "rude"
            ],
            "Returns & Refunds": [
                "return", "refund", "replacement", "exchange", "warranty", "policy", "claim",
                "reimbursement", "cancelled", "cancel"
            ],
            "Sizing & Fit": [
                "size", "fit", "sizing", "large", "small", "tight", "loose", "dimension",
                "measurements", "fitting", "true to size"
            ]
        }
    },
    "saas": {
        "name": "SaaS & Software",
        "description": "Cloud applications, software tools, platforms, and digital services",
        "aspects": {
            "UI & User Experience": [
                "ui", "ux", "interface", "design", "layout", "intuitive", "confusing",
                "cluttered", "navigation", "ease of use", "user-friendly", "modern", "look and feel"
            ],
            "Performance & Speed": [
                "speed", "performance", "system speed", "app speed", "lag", "latency", "loading time",
                "responsive", "sluggish", "freeze", "crash", "uptime", "downtime", "page load"
            ],
            "Features & Functionality": [
                "feature", "functionality", "tool", "capabilities", "integration", "export",
                "import", "automation", "dashboard", "reporting", "analytics", "options", "api"
            ],
            "Reliability & Stability": [
                "bug", "error", "glitch", "crash", "broken", "issue", "reliable", "stable",
                "sync", "syncing", "fail", "failure", "data loss"
            ],
            "Customer Support": [
                "support", "ticket", "help", "agent", "documentation", "guide", "tutorial",
                "representative", "response time", "turnaround", "resolution"
            ],
            "Pricing & Subscription": [
                "pricing", "subscription", "plan", "tier", "billing", "renewal", "expensive",
                "charge", "fee", "cost", "value for money", "trial"
            ],
            "Onboarding & Setup": [
                "onboarding", "setup", "installation", "configuration", "learning curve",
                "getting started", "documentation", "walkthrough"
            ]
        }
    },
    "consumer_tech": {
        "name": "Consumer Electronics & Hardware",
        "description": "Smartphones, laptops, headphones, smart home gadgets",
        "aspects": {
            "Battery & Power": [
                "battery", "charge", "charging", "battery life", "drain", "power", "charger",
                "endurance", "mah", "runtime", "overheating", "standby"
            ],
            "Display & Screen": [
                "screen", "display", "brightness", "resolution", "oled", "amoled", "colors",
                "refresh rate", "glare", "viewing angle", "hdr", "bezel", "touchscreen"
            ],
            "Camera & Audio": [
                "camera", "photo", "lens", "video", "sensor", "low light", "sound", "audio",
                "speaker", "mic", "microphone", "bass", "clarity", "volume", "headphones"
            ],
            "Build & Aesthetics": [
                "design", "build", "weight", "lightweight", "heavy", "materials", "aluminum",
                "premium", "plastic", "durability", "scratch", "ergonomics", "grip"
            ],
            "Software & OS": [
                "software", "os", "firmware", "update", "bloatware", "smooth", "features",
                "ecosystem", "connectivity", "bluetooth", "wifi", "pairing"
            ],
            "Value & Price": [
                "price", "cost", "expensive", "worth", "affordable", "flagship", "budget", "deal"
            ]
        }
    },
    "hospitality": {
        "name": "Hospitality & Restaurants",
        "description": "Hotels, dining, resorts, vacations, and travel experiences",
        "aspects": {
            "Food & Beverages": [
                "food", "dish", "meal", "taste", "flavor", "delicious", "bland", "fresh",
                "drink", "cocktail", "breakfast", "dinner", "menu", "portion", "coffee"
            ],
            "Staff & Service": [
                "staff", "service", "waiter", "waitress", "server", "reception", "concierge",
                "friendly", "attentive", "rude", "hospitality", "polite", "courteous"
            ],
            "Ambiance & Atmosphere": [
                "ambiance", "atmosphere", "vibe", "music", "noise", "loud", "decor",
                "lighting", "view", "cozy", "crowded", "romantic", "setting"
            ],
            "Cleanliness & Hygiene": [
                "clean", "dirty", "cleanliness", "hygiene", "smell", "odor", "bathroom",
                "restroom", "bedding", "towel", "spotless", "stain"
            ],
            "Amenities & Comfort": [
                "room", "bed", "mattress", "pillow", "pool", "spa", "wifi", "gym", "ac",
                "air conditioning", "heating", "shower", "comfort", "spacious"
            ],
            "Value & Pricing": [
                "price", "bill", "expensive", "cost", "worth", "overpriced", "value",
                "hidden fees", "rates", "tip"
            ],
            "Wait Time & Speed": [
                "wait", "queue", "delay", "check-in", "check-out", "slow service",
                "prompt", "fast", "reservation"
            ]
        }
    },
    "fintech": {
        "name": "FinTech & Banking",
        "description": "Digital banking, payments, crypto, investment apps",
        "aspects": {
            "Transaction & Payments": [
                "transfer", "payment", "transaction", "send money", "wire", "deposit",
                "withdrawal", "checkout", "processing", "instant", "failed payment"
            ],
            "Security & Authentication": [
                "security", "2fa", "fraud", "scam", "biometric", "login", "password",
                "verification", "safe", "secure", "locked account"
            ],
            "Fees & Transparency": [
                "fee", "charge", "hidden fee", "interest rate", "rate", "cost", "transparent",
                "commission", "penalty", "conversion rate"
            ],
            "App Usability & UX": [
                "app", "interface", "navigation", "easy", "glitch", "crash", "sync",
                "account view", "statements", "cards"
            ],
            "Customer Support": [
                "support", "bank rep", "dispute", "chargeback", "agent", "call center",
                "help", "unresponsive", "chat support"
            ]
        }
    }
}

# Customer Intent Rules and Markers
INTENT_MARKERS = {
    "Bug / Technical Issue": [
        "crash", "crashes", "bug", "glitch", "freeze", "frozen", "error", "broken",
        "not working", "doesn't work", "fails", "failed", "blank screen", "lag", "issue"
    ],
    "Feature Request": [
        "would be great if", "please add", "feature request", "wish it had", "missing",
        "hope you add", "could you support", "should have", "need an option", "suggest"
    ],
    "Churn Risk / Escalation": [
        "canceling", "cancelling", "cancel my subscription", "switching to", "uninstalled",
        "leaving", "waste of money", "rip off", "scam", "never buying again", "worst",
        "terrible experience", "unacceptable", "disgusted", "lawsuit", "refund or else"
    ],
    "Billing / Refund Request": [
        "refund", "charged twice", "overcharged", "billing error", "money back",
        "unauthorized charge", "cancel plan", "chargeback", "invoice issue"
    ],
    "Customer Support Issue": [
        "no response", "ignored", "rude agent", "waiting for days", "useless support",
        "ticket closed", "never replied", "unhelpful support"
    ],
    "Praise / Delight": [
        "love this", "amazing", "best", "exceptional", "superb", "exceeded expectations",
        "highly recommend", "game changer", "fantastic", "kudos", "brilliant", "flawless"
    ],
    "General Inquiry / Feedback": [
        "wondering", "how do I", "is it possible", "question", "curious"
    ]
}

# Discourse markers for clause segmentation
CONTRASTIVE_MARKERS = [
    " but ", " however, ", " however ", " although ", " though ", " except ",
    " while ", " whereas ", " yet ", " on the other hand, ", " on the other hand ",
    " despite ", " in spite of ", " even though ", " still "
]

SENTENCE_SPLIT_REGEX = r'(?<=[.!?;\n])\s+'
