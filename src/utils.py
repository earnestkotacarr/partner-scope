"""
Utility functions for Partner Scope.
"""
import re
from typing import Optional
from urllib.parse import urlparse


def clean_company_name(name: str) -> str:
    """
    Clean and normalize company name.

    Args:
        name: Company name

    Returns:
        Cleaned company name
    """
    # TODO: Remove common suffixes (Inc, LLC, Corp, Ltd, etc.)
    # TODO: Remove extra whitespace
    # TODO: Standardize casing
    # TODO: Handle special characters

    if not name:
        return ""

    # Basic cleaning
    name = name.strip()
    name = re.sub(r'\s+', ' ', name)

    return name


def extract_domain_from_url(url: str) -> str:
    """
    Extract domain from URL.

    Args:
        url: URL string

    Returns:
        Domain name (e.g., 'example.com')
    """
    # TODO: Handle various URL formats
    # TODO: Remove www prefix
    # TODO: Handle None/empty values

    if not url:
        return ""

    try:
        if not url.startswith(('http://', 'https://')):
            url = f'http://{url}'
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain.lower()
    except Exception:
        return ""


def extract_email_from_text(text: str) -> Optional[str]:
    """
    Extract email address from text.

    Args:
        text: Text containing potential email

    Returns:
        Email address if found, None otherwise
    """
    # TODO: Use regex to find email patterns
    # TODO: Validate email format
    # TODO: Return first valid email found

    if not text:
        return None

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)

    return matches[0] if matches else None


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)].strip() + suffix


def format_phone_number(phone: str) -> str:
    """
    Format phone number consistently.

    Args:
        phone: Phone number string

    Returns:
        Formatted phone number
    """
    # TODO: Remove non-numeric characters
    # TODO: Format based on length (US format, international, etc.)
    # TODO: Handle extensions

    if not phone:
        return ""

    # Remove non-numeric characters
    digits = re.sub(r'\D', '', phone)

    # Format US phone numbers
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return original if can't format


def safe_get(dictionary: dict, *keys, default=None):
    """
    Safely get nested dictionary value.

    Args:
        dictionary: Dictionary to search
        *keys: Nested keys to access
        default: Default value if key not found

    Returns:
        Value at nested key path or default
    """
    # TODO: Traverse nested dictionaries safely
    # TODO: Handle missing keys gracefully
    # TODO: Return default if any key is missing

    result = dictionary
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
    return result
