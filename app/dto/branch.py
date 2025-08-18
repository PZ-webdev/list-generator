from dataclasses import dataclass


@dataclass
class Branch:
    id: str
    name: str
    number: str
    input: str
    output: str
    is_old_pigeon: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> 'Branch':
        return Branch(
            id=data.get("id", ""),
            name=data.get("name", ""),
            number=data.get("number", ""),
            input=data.get("input", ""),
            output=data.get("output", ""),
            is_old_pigeon=data.get("is_old_pigeon", "")
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'number': self.number,
            'input': self.input,
            'output': self.output,
            'is_old_pigeon': self.is_old_pigeon
        }
