import json
from functools import lru_cache
from typing import List, Dict

class SupportService:
    def __init__(self, data_file: str = "doctores.json"):
        self.data_file = data_file
        self.data = self._load_data()

    @lru_cache(maxsize=1)
    def _load_data(self) -> List[Dict]:
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all(self) -> List[Dict]:
        return self.data