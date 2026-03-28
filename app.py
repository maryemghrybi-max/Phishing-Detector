from flask import Flask, render_template, request
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

app = Flask(__name__)

# ===== النموذج العام المتاح =====
MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

# ===== HTML Template =====
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Phishing Detector</title>
</head>
<body>
    <h1>Phishing Detector</h1>
    <form method="POST">
        <textarea name="message" placeholder="Enter message to check">{{ message }}</textarea>
        <button type="submit">Check</button>
    </form>
    {% if result %}
        <h2>Result: {{ result }}</h2>
        <p>Confidence: {{ confidence }}%</p>
    {% endif %}
</body>
</html>
"""

# تحميل النموذج والمحول
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# انشاء Pipeline للتصنيف
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# ===== قائمة كلمات Phishing سريعة =====
PHISHING_KEYWORDS = ["click here", "free", "price", "urgent", "win", "bank", "account", "password", "verify"]

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""
    result = None
    confidence = None

    if request.method == "POST":
        message = request.form.get("message", "")
        if message.strip():

            # ===== فلترة كلمات Phishing أولاً =====
            if any(word.lower() in message.lower() for word in PHISHING_KEYWORDS):
                result = "Phishing Alert"
                confidence = 99
            else:
                output = classifier(message)[0]  # {'label': 'POSITIVE', 'score': 0.9998}
                label = output["label"]
                score = output["score"] * 100
                result = "Safe Message" if label == "POSITIVE" else "Phishing Alert"
                confidence = round(score, 2)

    return render_template(HTML_TEMPLATE, message=message, result=result, confidence=confidence)

app.run(host="0.0.0.0", port=5000, debug=True)
if __name__ == "__main__":
    app.run()