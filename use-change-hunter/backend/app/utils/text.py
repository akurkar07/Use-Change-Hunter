import re


def normalize_address(address: str) -> str:
    """Normalize address string for consistency"""
    clean = re.sub(r'\s+', ' ', address.strip())
    return clean.upper()


def extract_numbers(text: str) -> list:
    """Extract all numbers from text"""
    return re.findall(r'\d+\.?\d*', text)
