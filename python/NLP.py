import spacy
import PyPDF2
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Load the spaCy language model
nlp = spacy.load('en_core_web_trf')

# Define the event keywords and related terms# Define the event keywords and related terms as a dictionary
event_keywords_and_related = {
    "earnings report": ["financial report", "earnings statement"],
    "interest rate": ["rate change", "Fed policy"],
    "options activity": ["trading options", "call and put options"],
    "derivative trading": ["options trading", "futures trading"],
    "algorithmic trading": ["algo trading", "automated trading"],
    "market manipulation": ["manipulative practices", "market abuse"],
    "liquidity event": ["funding event", "capital injection"]
}


# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    pdf_text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()
    return pdf_text

# Function to detect events in the text
def perform_event_detection(text, from_pdf=False):
    detected_events = []
    event_sentences = {}

    # Iterate through the event keywords
    for keyword, related_terms in event_keywords_and_related.items():
        # Add the keyword itself to the list of related terms
        related_terms.append(keyword)

        # Use re.search to find matches in the text with case-insensitive flag
        for term in related_terms:
            if re.search(rf'\b{re.escape(term)}\b', text, re.IGNORECASE):
                detected_events.append(keyword)

                # Find the sentences containing the event keyword
                event_sentences[keyword] = []
                sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
                for sentence in sentences:
                    if term in sentence:
                        event_sentences[keyword].append(sentence.strip())
                        print(f"Detected event sentence: {sentence.strip()}")  # Debug statement

    if not detected_events:
        detected_events.append("None Found")

    return detected_events, event_sentences

# Function to perform volatility analysis
def perform_volatility_analysis(text, from_pdf=False):
    # Initialize a set to store unique sentences containing the word "volatility"
    volatility_sentences = set()

    # Use spaCy for sentence tokenization
    doc = nlp(text)

    # Check each sentence for the word "volatility" (case-insensitive)
    for sentence in doc.sents:
        if re.search(r'\bvolatility\b', sentence.text, re.IGNORECASE):
            volatility_sentences.add(sentence.text)  # Add unique sentences to the set

    # Debug: Print the unique sentences with the word "volatility"
    print("Sentences with the Word 'Volatility':")
    for sentence in volatility_sentences:
        print(sentence)

    if not volatility_sentences:
        volatility_sentences.add("None Found")

    # Return the list of unique sentences with the word "volatility"
    return list(volatility_sentences)

# Function to identify M&A-related information in the text
def identify_mergers_and_acquisitions(text, from_pdf=False):
    # Initialize a list to store detected M&A information
    mergers_and_acquisitions = set()  # Use a set to store unique entries

    # Define keywords related to M&A
    m_and_a_keywords = [
        "merger", "acquisition", "takeover", "buyout", "M&A", "deal",
        "acquire", "merged with", "acquiring", "acquired by", "consolidation",
        "buy", "purchase", "combine", "transaction", "acquired"
    ]

    # Use spaCy for sentence tokenization
    doc = nlp(text)

    # Check each sentence for M&A-related keywords (case-insensitive)
    for sentence in doc.sents:
        for keyword in m_and_a_keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', sentence.text, re.IGNORECASE):
                mergers_and_acquisitions.add(sentence.text.strip())  # Use a set to store unique entries

    if not mergers_and_acquisitions:
        mergers_and_acquisitions.add("No M&A Information Found")

    return list(mergers_and_acquisitions)  # Convert the set back to a list for the response


analyzer = SentimentIntensityAnalyzer()

# Function to perform sentiment analysis
def perform_sentiment_analysis(text, from_pdf=False):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)
    compound_score = sentiment_scores['compound']
    
    if compound_score >= 0.05:
        sentiment = "Positive"
    elif compound_score <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    
    return sentiment

# Function to perform risk assessment
def perform_risk_assessment(text, from_pdf=False):
    # Basic risk assessment logic (you can customize this further)
    risk_score = 0
    keywords = text.lower().split()  # Convert text to lowercase and split into words

    # Check for risky keywords related to positions or strategies
    risky_keywords = [
        "high risk", "leveraged", "short", "naked", "exposure", "margin call", "volatility",
        "options", "derivatives", "speculative", "aggressive", "unhedged", "complex",
        "uncertainty", "volatile market", "high leverage"
    ]

    for keyword in risky_keywords:
        if keyword in keywords:
            risk_score += 1
            print(f"Added 1 point for keyword: {keyword}")  # Print the added points

    # Determine risk level based on the risk score
    if risk_score >= 5:
        risk_level = "Very High Risk"
    elif risk_score >= 3:
        risk_level = "High Risk"
    elif risk_score >= 1:
        risk_level = "Moderate Risk"
    else:
        risk_level = "Low Risk"

    return risk_level

# Function to perform named entity recognition (NER) analysis
def perform_ner_analysis(text, from_pdf=False):
    # Create a new Doc object from the text
    doc = nlp(text)
    named_entities = []

    # Define a custom sentence splitting pattern that handles hyphens
    def custom_sentence_splitter(text):
        sentence_endings = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        sentences = []
        current_sentence = ""
        for sentence in sentence_endings:
            if sentence.endswith('-'):
                current_sentence += sentence.rstrip('-')
            else:
                current_sentence += sentence
                sentences.append(current_sentence.strip())
                current_sentence = ""
        return sentences

    # Process the custom sentence splitting logic
    custom_sentences = custom_sentence_splitter(text)

    # Iterate through the named entities and assign them to sentences
    for ent in doc.ents:
        # Find the sentence containing the named entity
        entity_sentence = None
        for sentence in custom_sentences:
            if ent.text in sentence:
                entity_sentence = sentence
                break
        named_entities.append({
            "text": ent.text,
            "label": ent.label_,
            "sentence": entity_sentence  # Include the associated sentence
        })

    # Group named entities by sentence
    grouped_entities = {}
    for entity in named_entities:
        sentence = entity["sentence"]
        if sentence:
            if sentence in grouped_entities:
                grouped_entities[sentence].append(entity)
            else:
                grouped_entities[sentence] = [entity]

    return grouped_entities
@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    data = request.form.to_dict()
    pdf_text = ""
    uploaded_file = None

    if 'file' in request.files:
        uploaded_file = request.files['file']

        if uploaded_file.filename.endswith('.pdf'):
            pdf_text = extract_text_from_pdf(uploaded_file)

    if not data['text']:
        data['text'] = ""

    # Perform analysis tasks on the PDF text if available
    if pdf_text:
        detected_events, event_sentences = perform_event_detection(pdf_text)
        sentiment_result = perform_sentiment_analysis(pdf_text)
        risk_level = perform_risk_assessment(pdf_text)
        named_entities_result = perform_ner_analysis(pdf_text)
        volatility_result = perform_volatility_analysis(pdf_text)
        m_and_a_info = identify_mergers_and_acquisitions(pdf_text)
    else:
        detected_events, event_sentences = perform_event_detection(data['text'])
        sentiment_result = perform_sentiment_analysis(data['text'])
        risk_level = perform_risk_assessment(data['text'])
        named_entities_result = perform_ner_analysis(data['text'])
        volatility_result = perform_volatility_analysis(data['text'])
        m_and_a_info = identify_mergers_and_acquisitions(data['text'])

    analysis_results = {
        "detected_events": detected_events,
        "event_sentences": event_sentences,
        "volatility_mentions": volatility_result,
        "sentiment": sentiment_result,
        "risk_level": risk_level,
        "m_and_a_info": m_and_a_info,
        "named_entities": named_entities_result
    }

    return jsonify(analysis_results)


if __name__ == '__main__':
    app.run(debug=True)
