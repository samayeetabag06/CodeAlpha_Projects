import json
import math
import re
from collections import Counter

# Standard English Stop Words (Pure Python - No NLTK download needed)
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", 
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", 
    "below", "between", "both", "but", "by", "can", "cannot", "could", "did", "do", 
    "does", "doing", "don't", "down", "during", "each", "few", "for", "from", 
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", 
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", 
    "its", "itself", "let's", "me", "more", "most", "my", "myself", "no", "nor", 
    "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", 
    "ourselves", "out", "over", "own", "same", "she", "should", "so", "some", "such", 
    "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", 
    "these", "they", "this", "those", "through", "to", "too", "under", "until", 
    "up", "very", "was", "wasn't", "we", "were", "weren't", "what", "when", "where", 
    "which", "while", "who", "whom", "why", "with", "won't", "would", "you", "your", 
    "yours", "yourself", "yourselves"
}

def simple_stem(word: str) -> str:
    """Basic rule-based suffix normalization (stemming)."""
    for suffix in ["ing", "ly", "ed", "ies", "es", "s"]:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]
    return word

def preprocess_text(text: str) -> list[str]:
    """Tokenizes, cleans, removes stopwords, and stems words."""
    # Convert to lowercase and extract words
    tokens = re.findall(r"\b[a-z]{2,}\b", text.lower())
    # Remove stopwords and apply stemming
    cleaned_tokens = [simple_stem(w) for w in tokens if w not in STOP_WORDS]
    return cleaned_tokens

class FAQChatbot:
    def __init__(self, data_path: str = "faqs.json", threshold: float = 0.20):
        self.data_path = data_path
        self.threshold = threshold
        self.faqs = []
        self.vocabulary = []
        self.idf_scores = {}
        self.faq_vectors = []
        self.load_and_train()

    def load_and_train(self):
        """Loads FAQs and calculates TF-IDF matrix for all questions."""
        with open(self.data_path, "r", encoding="utf-8") as f:
            self.faqs = json.load(f)

        tokenized_questions = [
            preprocess_text(faq["question"]) for faq in self.faqs
        ]

        # Build vocabulary
        vocab_set = set(token for q in tokenized_questions for token in q)
        self.vocabulary = sorted(list(vocab_set))

        # Calculate IDF (Inverse Document Frequency)
        total_docs = len(tokenized_questions)
        for term in self.vocabulary:
            doc_count = sum(1 for q in tokenized_questions if term in q)
            # Smooth IDF formula
            self.idf_scores[term] = math.log((1 + total_docs) / (1 + doc_count)) + 1.0

        # Build TF-IDF vectors for each FAQ
        self.faq_vectors = [
            self._compute_tfidf_vector(q) for q in tokenized_questions
        ]

    def _compute_tfidf_vector(self, tokens: list[str]) -> list[float]:
        """Converts a tokenized query into a normalized TF-IDF vector."""
        if not tokens:
            return [0.0] * len(self.vocabulary)

        counts = Counter(tokens)
        total_terms = len(tokens)
        vector = []

        for term in self.vocabulary:
            tf = counts.get(term, 0) / total_terms
            idf = self.idf_scores.get(term, 1.0)
            vector.append(tf * idf)

        return vector

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Computes Cosine Similarity between two numerical vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def get_response(self, user_query: str) -> dict:
        """Matches user question with the most relevant FAQ."""
        processed_query = preprocess_text(user_query)

        if not processed_query:
            return {
                "answer": "Could you please rephrase your question with more specific details?",
                "matched_question": None,
                "confidence": 0.0
            }

        user_vector = self._compute_tfidf_vector(processed_query)

        # Calculate similarity against all FAQs
        similarities = [
            self._cosine_similarity(user_vector, faq_vec)
            for faq_vec in self.faq_vectors
        ]

        best_score = max(similarities)
        best_index = similarities.index(best_score)

        if best_score >= self.threshold:
            return {
                "answer": self.faqs[best_index]["answer"],
                "matched_question": self.faqs[best_index]["question"],
                "confidence": round(best_score, 2)
            }
        else:
            return {
                "answer": "I'm sorry, I couldn't find an exact match for that question. You can ask about tracking, refunds, shipping times, or payment methods.",
                "matched_question": None,
                "confidence": round(best_score, 2)
            }