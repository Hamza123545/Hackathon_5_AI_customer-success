import re
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def format_response_for_channel(message: str, channel: str, context: Dict[str, Any] = {}) -> Any:
    """
    Formats the raw agent response for the specific channel.
    """
    channel = channel.lower()
    
    if channel == "email":
        # Create a simple HTML wrapper
        # context might contain 'customer_name'
        customer_name = context.get("customer_name", "Customer")
        html_content = f"""
        <html>
        <body>
            <p>Dear {customer_name},</p>
            <p>{message.replace(chr(10), '<br>')}</p>
            <br>
            <p>Best regards,</p>
            <p><strong>Customer Success Team</strong></p>
        </body>
        </html>
        """
        # Return dict for Gmail API or just the body? 
        # The channel handler will likely expect a body.
        return html_content

    elif channel == "whatsapp":
        # Whatsapp text formatting: *bold*, _italics_
        # Ensure it's not too long. If > 1600 chars (Twilio limit is 1600), truncate or split?
        # Agent prompt should limit length, but here we enforce hard limit safety.
        # Twilio manages splitting usually, but let's be safe.
        clean_text = message.replace("**", "*").replace("__", "_")
        if len(clean_text) > 1500:
             clean_text = clean_text[:1497] + "..."
        return clean_text

    elif channel == "web_form":
        # Web usually expects JSON
        return {
            "text": message,
            "format": "markdown" # Frontend can render markdown
        }
    
    else:
         # Default fallback
         return message

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Basic rule-based sentiment/urgency analysis.
    In a real system, call an NLP model or LLM.
    """
    text_lower = text.lower()
    
    score = 0.0
    is_urgent = False
    flagged = False
    
    # Simple keyword lists
    positive_words = ["thanks", "thank you", "great", "awesome", "helpful", "good"]
    negative_words = ["bad", "terrible", "awful", "useless", "broken", "angry", "hate"]
    urgent_words = ["urgent", "immediately", "asap", "emergency", "now"]
    profanity = ["damn", "hell"] # Placeholder list
    
    # Calculate score
    for word in positive_words:
        if word in text_lower:
            score += 0.2
    
    for word in negative_words:
        if word in text_lower:
            score -= 0.3
            
    for word in urgent_words:
        if word in text_lower:
            is_urgent = True
            score -= 0.1 # Urgency usually implies stress
            
    for word in profanity:
        if word in text_lower:
            flagged = True
            score -= 0.5
            
    # Clamp score
    score = max(min(score, 1.0), -1.0)
    
    return {
        "score": round(score, 2),
        "is_urgent": is_urgent,
        "flagged": flagged
    }
