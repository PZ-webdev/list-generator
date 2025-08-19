from dataclasses import dataclass


@dataclass
class Branch:
    id: str
    name: str
    number: str
    input: str
    output: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Branch':
        return Branch(
            id=data.get("id", ""),
            name=data.get("name", ""),
            number=data.get("number", ""),
            input=data.get("input", ""),
            output=data.get("output", "")
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'number': self.number,
            'input': self.input,
            'output': self.output
        }
