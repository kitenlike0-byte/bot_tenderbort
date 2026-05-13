import re


def parse_transaction(text: str):
    """
    Примеры:
    -500 еда макароны
    +2000 зарплата
    """

    text = text.strip()

    match = re.match(r"([+-]?\d+)\s+(.+)", text)

    if not match:
        return None

    amount = int(match.group(1))
    rest = match.group(2)

    words = rest.split()

    category = words[0] if words else "прочее"
    description = " ".join(words[1:]) if len(words) > 1 else ""

    tx_type = "income" if amount > 0 else "expense"

    return {
        "amount": abs(amount),
        "type": tx_type,
        "category": category,
        "description": description
    }
    