from typing import List
from typing import Any
from dataclasses import dataclass
import json
@dataclass
class Child:
    Type: int
    ParentId: int
    Children: List[object]
    Id: int
    EnabledOnline: bool
    Name: str
    Guid: str

    @staticmethod
    def from_dict(obj: Any) -> 'Child':
        _Type = int(obj.get("Type"))
        _ParentId = int(obj.get("ParentId"))
        _Children = [.from_dict(y) for y in obj.get("Children")]
        _Id = int(obj.get("Id"))
        _EnabledOnline = 
        _Name = str(obj.get("Name"))
        _Guid = str(obj.get("Guid"))
        return Child(_Type, _ParentId, _Children, _Id, _EnabledOnline, _Name, _Guid)

@dataclass
class Root:
    Type: int
    ParentId: int
    Children: List[Child]
    Id: int
    EnabledOnline: bool
    Name: str
    Guid: str

    @staticmethod
    def from_dict(obj: Any) -> 'Root':
        _Type = int(obj.get("Type"))
        _ParentId = int(obj.get("ParentId"))
        _Children = [Child.from_dict(y) for y in obj.get("Children")]
        _Id = int(obj.get("Id"))
        _EnabledOnline = 
        _Name = str(obj.get("Name"))
        _Guid = str(obj.get("Guid"))
        return Root(_Type, _ParentId, _Children, _Id, _EnabledOnline, _Name, _Guid)

# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Root.from_dict(jsonstring)
