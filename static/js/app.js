const form = document.getElementById('analysisForm');
const feedbackInput = document.getElementById('feedbackText');
const analyzeButton = document.getElementById('analyzeButton');
const characterCount = document.getElementById('characterCount');
const errorMessage = document.getElementById('errorMessage');
const emptyState = document.getElementById('emptyState');
const results = document.getElementById('results');
const themeSelect = document.getElementById('themeSelect');
let currentAspects = [];

const savedTheme = localStorage.getItem('aspectpulse-theme');
const availableThemes = ['violet', 'midnight', 'ocean', 'rose'];
setTheme(availableThemes.includes(savedTheme) ? savedTheme : 'violet');

themeSelect.addEventListener('change', () => {
  setTheme(themeSelect.value);
  renderVisualizations(currentAspects);
});

feedbackInput.addEventListener('input', () => {
  const count = feedbackInput.value.length;
  characterCount.textContent = `${count} ${count === 1 ? 'character' : 'characters'}`;
});

document.getElementById('exampleButton').addEventListener('click', () => {
  feedbackInput.value = 'The camera takes beautiful photos, but the battery drains too quickly and customer support was unhelpful.';
  document.getElementById('domainSelect').value = 'consumer_tech';
  feedbackInput.dispatchEvent(new Event('input'));
  feedbackInput.focus();
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = feedbackInput.value.trim();
  if (!text) {
    showError('Enter some customer feedback before running the analysis.');
    feedbackInput.focus();
    return;
  }

  setLoading(true);
  hideError();

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        domain: document.getElementById('domainSelect').value
      })
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'The analysis could not be completed.');
    }
    renderResults(data);
  } catch (error) {
    showError(error.message || 'Could not connect to the analysis service. Please try again.');
  } finally {
    setLoading(false);
  }
});

function renderResults(data) {
  const sentiment = data.overall_sentiment || {};
  const intent = data.intent || {};
  const aspects = Array.isArray(data.aspects) ? data.aspects : [];
  currentAspects = aspects;
  const insights = data.insights || {};
  const recommendations = Array.isArray(insights.recommendations) ? insights.recommendations : [];
  const sentimentLabel = sentiment.label || 'NEUTRAL';
  const urgencyValue = Math.max(0, Math.min(10, Number(intent.urgency_score) || 0));
  const urgency = urgencyValue.toFixed(1);
  const priority = (intent.priority || 'LOW').toUpperCase();

  const overallElement = document.getElementById('overallSentiment');
  overallElement.textContent = sentimentLabel;
  overallElement.className = `summary-value sentiment-${sentimentLabel.toLowerCase()}`;
  document.getElementById('overallConfidence').textContent =
    `${Math.round((sentiment.confidence || 0) * 100)}% model confidence`;
  document.getElementById('primaryIntent').textContent = intent.primary_intent || 'General feedback';
  document.getElementById('urgencyScore').textContent = `${urgency} / 10`;
  document.getElementById('urgencyPriority').textContent = `${priority} priority`;
  const urgencyMeter = document.querySelector('.urgency-meter');
  urgencyMeter.setAttribute('aria-valuenow', urgencyValue.toFixed(1));
  document.getElementById('urgencyMeterFill').style.width = `${urgencyValue * 10}%`;
  document.getElementById('urgencyMeterFill').className = `priority-${priority.toLowerCase()}`;
  document.getElementById('urgencyExplanation').textContent = urgencyValue >= 7.5
    ? 'Respond immediately'
    : urgencyValue >= 5.5
      ? 'Follow up promptly'
      : urgencyValue >= 3.5
        ? 'Address in the standard queue'
        : 'Monitor and acknowledge';

  const badge = document.getElementById('priorityBadge');
  badge.textContent = `${priority} PRIORITY`;
  badge.className = `priority-badge priority-${priority.toLowerCase()}`;

  document.getElementById('feedbackSummary').textContent =
    insights.summary || `The overall sentiment is ${sentimentLabel.toLowerCase()}, with ${aspects.length} distinct ${aspects.length === 1 ? 'aspect' : 'aspects'} detected.`;
  renderFeedbackSignals(insights, aspects);

  const aspectList = document.getElementById('aspectList');
  aspectList.replaceChildren();
  aspects.forEach((aspect) => aspectList.appendChild(createAspectCard(aspect)));
  document.getElementById('aspectCount').textContent =
    `${aspects.length} ${aspects.length === 1 ? 'aspect' : 'aspects'}`;
  document.getElementById('noAspects').hidden = aspects.length !== 0;
  renderVisualizations(aspects);

  const recommendationList = document.getElementById('recommendationList');
  recommendationList.replaceChildren();
  const hasRecommendations = recommendations.length > 0;
  const nextSteps = hasRecommendations
    ? recommendations
    : ['No immediate action is needed. Continue monitoring customer feedback.'];
  nextSteps.forEach((recommendation, index) => {
    const item = document.createElement('li');
    const label = document.createElement('span');
    label.className = 'step-label';
    label.textContent = !hasRecommendations
      ? 'Keep in view'
      : index === 0 && ['CRITICAL', 'HIGH'].includes(priority)
        ? 'Start here'
        : index === 0
          ? 'Recommended action'
          : 'Follow-up';
    const description = document.createElement('p');
    description.textContent = recommendation;
    item.append(label, description);
    recommendationList.appendChild(item);
  });

  emptyState.hidden = true;
  results.hidden = false;
}

function renderFeedbackSignals(insights, aspects) {
  const signals = document.getElementById('feedbackSignals');
  signals.replaceChildren();
  const groups = [
    { label: 'What is working', values: insights.strengths || [], sentiment: 'positive' },
    { label: 'Needs attention', values: insights.friction_points || [], sentiment: 'negative' }
  ];

  groups.forEach(({ label, values, sentiment }) => {
    if (!values.length) return;
    const group = document.createElement('div');
    group.className = `signal-group sentiment-${sentiment}`;
    const heading = document.createElement('strong');
    heading.textContent = label;
    const chips = document.createElement('div');
    chips.className = 'signal-chips';
    values.forEach((value) => {
      const chip = document.createElement('span');
      chip.textContent = value;
      chips.appendChild(chip);
    });
    group.append(heading, chips);
    signals.appendChild(group);
  });

  if (!aspects.length) {
    const note = document.createElement('p');
    note.className = 'signal-empty';
    note.textContent = 'No specific product or service details were identified, so the suggestions focus on the overall feedback.';
    signals.appendChild(note);
  }
}

function renderVisualizations(aspects) {
  const counts = { POSITIVE: 0, NEUTRAL: 0, NEGATIVE: 0 };
  aspects.forEach((aspect) => {
    const label = (aspect.sentiment || 'NEUTRAL').toUpperCase();
    if (Object.hasOwn(counts, label)) counts[label] += 1;
  });

  const total = aspects.length;
  const sentimentBar = document.getElementById('sentimentBar');
  sentimentBar.replaceChildren();
  [
    ['POSITIVE', counts.POSITIVE],
    ['NEUTRAL', counts.NEUTRAL],
    ['NEGATIVE', counts.NEGATIVE]
  ].forEach(([label, count]) => {
    if (!total || !count) return;
    const segment = document.createElement('span');
    segment.className = `sentiment-segment sentiment-${label.toLowerCase()}`;
    segment.style.width = `${(count / total) * 100}%`;
    segment.setAttribute('aria-hidden', 'true');
    sentimentBar.appendChild(segment);
  });
  sentimentBar.setAttribute(
    'aria-label',
    `Sentiment across ${total} aspects: ${counts.POSITIVE} positive, ${counts.NEUTRAL} neutral, ${counts.NEGATIVE} negative`
  );

  const positiveEnd = total ? (counts.POSITIVE / total) * 360 : 0;
  const neutralEnd = total ? positiveEnd + (counts.NEUTRAL / total) * 360 : 0;
  const donut = document.getElementById('sentimentDonut');
  donut.style.setProperty('--positive-angle', '0deg');
  donut.style.setProperty('--neutral-angle', '0deg');
  donut.style.background = total ? '' : 'var(--neutral-bg)';
  requestAnimationFrame(() => {
    donut.style.setProperty('--positive-angle', `${positiveEnd}deg`);
    donut.style.setProperty('--neutral-angle', `${neutralEnd}deg`);
  });
  donut.setAttribute(
    'aria-label',
    `Sentiment distribution across ${total} aspects: ${counts.POSITIVE} positive, ${counts.NEUTRAL} neutral, ${counts.NEGATIVE} negative`
  );
  document.getElementById('donutTotal').textContent = total;

  const legend = document.getElementById('sentimentLegend');
  legend.replaceChildren();
  [
    ['POSITIVE', 'Positive', counts.POSITIVE],
    ['NEUTRAL', 'Neutral', counts.NEUTRAL],
    ['NEGATIVE', 'Negative', counts.NEGATIVE]
  ].forEach(([label, title, count]) => {
    const item = document.createElement('li');
    const marker = document.createElement('span');
    marker.className = `legend-marker sentiment-${label.toLowerCase()}`;
    marker.setAttribute('aria-hidden', 'true');
    const text = document.createElement('span');
    text.textContent = title;
    const value = document.createElement('strong');
    value.textContent = `${count} · ${total ? Math.round((count / total) * 100) : 0}%`;
    item.append(marker, text, value);
    legend.appendChild(item);
  });

  const chart = document.getElementById('polarityChart');
  chart.replaceChildren();
  aspects.forEach((aspect, index) => {
    const row = document.createElement('div');
    row.className = 'polarity-row';
    row.style.setProperty('--row-index', index);

    const name = document.createElement('span');
    name.className = 'polarity-name';
    name.textContent = aspect.aspect || 'Uncategorized';

    const track = document.createElement('div');
    track.className = 'polarity-track';
    track.setAttribute('aria-hidden', 'true');
    const marker = document.createElement('span');
    const score = Math.max(-100, Math.min(100, Number(aspect.net_score) || 0));
    const sentiment = (aspect.sentiment || 'NEUTRAL').toLowerCase();
    marker.className = `polarity-marker sentiment-${sentiment}`;
    marker.style.left = '50%';
    track.appendChild(marker);

    const value = document.createElement('span');
    value.className = `polarity-value sentiment-${sentiment}`;
    value.textContent = `${score > 0 ? '+' : ''}${Math.round(score)}`;

    row.append(name, track, value);
    chart.appendChild(row);
    requestAnimationFrame(() => {
      marker.style.left = `${(score + 100) / 2}%`;
    });
  });

  const hasData = total > 0;
  document.getElementById('noVisualizationData').hidden = hasData;
  document.querySelector('.visualization-grid').hidden = !hasData;
}

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  themeSelect.value = theme;
  localStorage.setItem('aspectpulse-theme', theme);
  document.querySelector('meta[name="theme-color"]').content =
    getComputedStyle(document.documentElement).getPropertyValue('--page').trim();
}

function createAspectCard(aspect) {
  const card = document.createElement('article');
  card.className = 'aspect-card';

  const details = document.createElement('div');
  details.className = 'aspect-details';
  const name = document.createElement('h4');
  name.textContent = aspect.aspect || 'Uncategorized';
  const cue = document.createElement('p');
  cue.textContent = aspect.clause || aspect.keyword || '';
  details.append(name, cue);

  const sentiment = (aspect.sentiment || 'NEUTRAL').toUpperCase();
  const result = document.createElement('div');
  result.className = 'aspect-result';
  const badge = document.createElement('span');
  badge.className = `sentiment-badge sentiment-${sentiment.toLowerCase()}`;
  badge.textContent = sentiment;
  const confidence = document.createElement('span');
  confidence.className = 'aspect-confidence';
  confidence.textContent = `${Math.round((aspect.confidence || 0) * 100)}% confidence`;
  result.append(badge, confidence);

  card.append(details, result);
  return card;
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function hideError() {
  errorMessage.textContent = '';
  errorMessage.hidden = true;
}

function setLoading(isLoading) {
  analyzeButton.disabled = isLoading;
  analyzeButton.classList.toggle('is-loading', isLoading);
  analyzeButton.querySelector('span').textContent = isLoading ? 'Analyzing…' : 'Analyze feedback';
}
