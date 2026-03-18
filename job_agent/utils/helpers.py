
import json
import os
from datetime import datetime
import random
import string


def load_json(filepath):
    """Load JSON data from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}


def save_json(filepath, data):
    """Save JSON data to file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False


def generate_id(prefix=""):
    """Generate a unique ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    
    if prefix:
        return f"{prefix}_{timestamp}_{random_part}"
    return f"{timestamp}_{random_part}"


def format_currency(amount, currency="USD"):
    """Format currency amount"""
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }
    symbol = symbols.get(currency, "$")
    return f"{symbol}{amount:,}"


def parse_experience_range(exp_string):
    """Parse experience range string like '1-3' or '3+'"""
    try:
        if "+" in exp_string:
            min_exp = int(exp_string.replace("+", ""))
            return min_exp, 99
        elif "-" in exp_string:
            parts = exp_string.split("-")
            return int(parts[0]), int(parts[1])
        else:
            exp = int(exp_string)
            return exp, exp
    except:
        return 0, 10


def truncate_string(text, max_length=100):
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."