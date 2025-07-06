from dataclasses import dataclass

@dataclass
class Service:
    id: int
    name: str
    url: str
    description: str
    category: str
