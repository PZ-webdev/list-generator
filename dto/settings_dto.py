class SettingsDTO:
    def __init__(self, mappings):
        self.mappings = mappings

    def to_dict(self):
        return {"mappings": self.mappings}

    @staticmethod
    def from_dict(data):
        return SettingsDTO(mappings=data.get("mappings", []))
