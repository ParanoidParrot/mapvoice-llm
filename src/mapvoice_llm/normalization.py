import re

ABBREVIATIONS = {
    r"\bRd\b": "Road",
    r"\bSt\b": "Street",
    r"\bJn\b": "Junction",
    r"\bNH\b": "National Highway",
    r"\bFt\b": "Feet",
}

SMALL_NUMBERS = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    20: "twenty",
    30: "thirty",
    40: "forty",
    50: "fifty",
    60: "sixty",
    70: "seventy",
    80: "eighty",
    90: "ninety",
    100: "one hundred",
    200: "two hundred",
    300: "three hundred",
    400: "four hundred",
    500: "five hundred",
    600: "six hundred",
    700: "seven hundred",
    800: "eight hundred",
    900: "nine hundred",
}


def number_to_words(value: int) -> str:
    if value in SMALL_NUMBERS:
        return SMALL_NUMBERS[value]

    if 10 < value < 100:
        tens = (value // 10) * 10
        ones = value % 10
        if tens in SMALL_NUMBERS and ones in SMALL_NUMBERS:
            return f"{SMALL_NUMBERS[tens]} {SMALL_NUMBERS[ones]}"

    return str(value)


def expand_distances(text: str) -> str:
    def meters(match: re.Match) -> str:
        value = int(match.group(1))
        return f"{number_to_words(value)} meters"

    text = re.sub(r"\b(\d+)\s*m\b", meters, text, flags=re.IGNORECASE)
    text = re.sub(r"\b(\d+(?:\.\d+)?)\s*km\b", r"\1 kilometers", text, flags=re.IGNORECASE)
    return text


def expand_abbreviations(text: str) -> str:
    result = text
    for pattern, replacement in ABBREVIATIONS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def normalize_navigation_text(text: str) -> str:
    text = text.strip()
    text = expand_abbreviations(text)
    text = expand_distances(text)
    text = re.sub(r"\s+", " ", text)
    return text
