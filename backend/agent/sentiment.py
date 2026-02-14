import re

def analyze_sentiment(text: str) -> float:
    """
    Analyzes the sentiment of a text string.
    Returns a score between -1.0 (negative) and 1.0 (positive).
    
    For MVP, we use a simple keyword-based approach.
    """
    text = text.lower()
    
    positive_words = ["happy", "good", "great", "excellent", "awesome", "thanks", "thank you", "helpful", "resolved", "appreciate"]
    negative_words = ["angry", "bad", "terrible", "awful", "worst", "hate", "frustrated", "annoying", "broken", "fail", "slow", "useless", "stupid"]
    
    score = 0.0
    
    # Simple counting
    for word in positive_words:
        if word in text:
            score += 0.2
            
    for word in negative_words:
        if word in text:
            score -= 0.3 # Negative words weigh more
            
    # Cap score
    return max(min(score, 1.0), -1.0)
