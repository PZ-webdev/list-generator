from dataclasses import dataclass


@dataclass
class Branch:
    id: str
    name: str
    input: str
    output: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Branch':
        return cls(
            id=str(data['id']),
            name=data['name'],
            input=data['input'],
            output=data['output']
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'input': self.input,
            'output': self.output
        }
