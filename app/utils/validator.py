def validate_number(limit: int):
    def validator(value: str) -> bool:
        if value == "":
            return True
        if value.isdigit():
            return 0 <= int(value) <= limit
        return False

    return validator
