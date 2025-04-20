import json
from functools import lru_cache

class AccommodationService:
    def __init__(self, data_file="accommodations.json"):
        self.data_file = data_file
        self.data = self._load_data()

    @lru_cache(maxsize=1)
    def _load_data(self):
        with open(self.data_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_plan(self, plan_id: str):
        """Busca un plan por ID en la lista de planes nutricionales."""
        planes = self.data.get("planes_nutricionales", [])
        return next((p for p in planes if str(p["id"]) == str(plan_id)), None)

    def create_plan_link(self, plan_id: str) -> str:
        """Genera el enlace para un plan nutricional dado el ID."""
        plan = self.get_plan(plan_id)
        if not plan:
            return f"Plan con ID {plan_id} no encontrado."
        return f"[Ver plan: {plan['name']}](https://nutriplanner-ia.vercel.app/accommodation/{plan_id})"
