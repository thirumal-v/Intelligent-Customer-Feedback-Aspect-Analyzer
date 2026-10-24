# AspectPulse

AspectPulse analyzes a customer review and presents its overall sentiment, detected product or service aspects, customer intent, urgency, and suggested next steps in a single-page interface.

Choose between Violet, Midnight, Ocean, and Rose themes from the page header. The selected theme is saved in the browser. Feedback visualizations animate when results load, while respecting reduced-motion preferences.

## Run locally

Use Python 3.10 or newer. Install the project dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the web app:

```powershell
python run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The sentiment model is downloaded by Hugging Face the first time it is initialized, so the initial startup may take longer.

## Use the app

1. Paste customer feedback into the input.
2. Choose an industry or leave it set to **Auto-detect**.
3. Select **Analyze feedback** to see the prediction and aspect breakdown.
4. Optionally change the page theme from the header.

The interface is intentionally limited to this single prediction workflow. The Flask service also keeps its JSON analysis endpoint available:

```http
POST /api/analyze
Content-Type: application/json
```

```json
{
  "text": "The camera takes beautiful photos, but the battery drains too quickly.",
  "domain": "consumer_tech"
}
```

## Project structure

```text
app.py                     Flask routes and analysis orchestration
run.py                     Local development launcher
core/                      Aspect, sentiment, intent, and insight engines
data/                      Sample review datasets
static/index.html          Single-page prediction interface
static/css/style.css       Interface styles
static/js/app.js           Prediction form and result rendering
requirements.txt           Python dependencies
```
