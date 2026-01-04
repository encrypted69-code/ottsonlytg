"""
Text Utility Functions
Provides text transformation utilities for bot messages
"""


def toSmallCaps(text):
    """
    Converts regular text to Unicode small-caps style while preserving HTML tags.
    
    Example:
        "TELEGRAM FONTS" → "ᴛᴇʟᴇɢʀᴀᴍ ꜰᴏɴᴛꜱ"
        "<b>Hello</b>" → "<b>ʜᴇʟʟᴏ</b>"
    
    Args:
        text (str): Input text to convert
        
    Returns:
        str: Text converted to Unicode small-caps with HTML tags preserved
        
    Note:
        - A-Z and a-z are converted to small-caps Unicode characters
        - Numbers, emojis, symbols, and punctuation remain unchanged
        - HTML tags are preserved and not converted
        - No external libraries required - pure Unicode mapping
    """
    # Unicode small-caps character mapping
    # Maps both uppercase and lowercase to their small-caps equivalents
    small_caps_map = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
        'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
        'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
        'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ',
        'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ',
        'F': 'ꜰ', 'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ',
        'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ',
        'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 'ꜱ', 'T': 'ᴛ',
        'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ'
    }
    
    # Convert each character, but skip characters inside HTML tags
    result = []
    inside_tag = False
    
    for char in text:
        if char == '<':
            # Entering an HTML tag
            inside_tag = True
            result.append(char)
        elif char == '>':
            # Exiting an HTML tag
            inside_tag = False
            result.append(char)
        elif inside_tag:
            # Inside a tag, keep character as-is
            result.append(char)
        else:
            # Outside tags, apply small-caps conversion
            result.append(small_caps_map.get(char, char))
    
    return ''.join(result)


# ============================================
# EXAMPLE USAGE (For Reference)
# ============================================
if __name__ == "__main__":
    # Test the function
    test_texts = [
        "Welcome To OTTOnly!",
        "TELEGRAM FONTS",
        "Buy OTT Subscriptions At Unbeatable Prices.",
        "Payment Successful! 💰",
        "Order ID: NET1234"
    ]
    
    print("=" * 60)
    print("Unicode Small-Caps Converter Test")
    print("=" * 60)
    
    for text in test_texts:
        converted = toSmallCaps(text)
        print(f"\nOriginal:  {text}")
        print(f"Converted: {converted}")
    
    print("\n" + "=" * 60)
