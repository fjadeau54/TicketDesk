from datetime import datetime

DATE_FMT = "%Y-%m-%d"

def parse_date(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    # on laisse simple pour l’instant, sans gestion d’erreur poussée
    datetime.strptime(value, DATE_FMT)
    return value
