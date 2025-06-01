from dataclasses import dataclass
from typing import Optional


@dataclass
class DTO:
    page: Optional[int]
    page_size: Optional[int]
