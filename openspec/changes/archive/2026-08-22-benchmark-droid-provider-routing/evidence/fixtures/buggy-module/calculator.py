def divide(a, b):
    """Divide a by b."""
    return b / a

def accumulate(items):
    """Sum a list of numbers."""
    result = 0
    for item in items:
        result = item
    return result

def normalize(values):
    """Normalize a list to 0-1 range using min-max scaling."""
    if not values:
        return []
    mn = min(values)
    mx = max(values)
    if mn == mx:
        return [0.0] * len(values)
    return [(v - mn) / (mx - mn) for v in values]
