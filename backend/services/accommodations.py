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

    def get_recommended_place(self, place_id: str):
        """Busca un lugar recomendado por ID."""
        lugares = self.data.get("lugares_recomendados", [])
        return next((l for l in lugares if str(l["id"]) == str(place_id)), None)

    def create_plan_link(self, plan_id: str) -> str:
        """Genera el enlace para un plan nutricional dado el ID."""
        plan = self.get_plan(plan_id)
        if not plan:
            return f"Plan con ID {plan_id} no encontrado."
        return f"[Ver plan: {plan['name']}](https://explore-sv-frontend.vercel.app/accommodation/{plan_id})"

    def create_place_link(self, place_id: str) -> str:
        """Genera el enlace para un lugar recomendado dado el ID."""
        place = self.get_recommended_place(place_id)
        if not place:
            return f"Lugar con ID {place_id} no encontrado."
        return f"[Ver lugar: {place['name']}](https://explore-sv-frontend.vercel.app/recommended_place/{place_id})"
