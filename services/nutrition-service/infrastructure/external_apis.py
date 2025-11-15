import logging
from typing import Optional, Dict, Any, List
import httpx

from infrastructure.settings import settings

logger = logging.getLogger(__name__)


class OpenFoodFactsAPI:
    def __init__(self):
        self.base_url = settings.openfoodfacts_api_url
        self.timeout = 10.0

    async def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/product/{barcode}.json"
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == 1 and data.get("product"):
                    product = data["product"]
                    return {
                        "name": product.get("product_name", ""),
                        "barcode": barcode,
                        "calories_per_100g": product.get("nutriments", {}).get("energy-kcal_100g"),
                        "proteins": product.get("nutriments", {}).get("proteins_100g"),
                        "carbs": product.get("nutriments", {}).get("carbohydrates_100g"),
                        "fats": product.get("nutriments", {}).get("fat_100g"),
                    }
                return None
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching product {barcode} from OpenFoodFacts")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching product {barcode}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching product {barcode} from OpenFoodFacts: {e}")
            return None

    async def search_product(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/cgi/search.pl"
                params = {
                    "search_terms": query,
                    "page_size": limit,
                    "json": 1
                }
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                products = []
                if data.get("products"):
                    for product in data["products"][:limit]:
                        products.append({
                            "name": product.get("product_name", ""),
                            "barcode": product.get("code", ""),
                            "calories_per_100g": product.get("nutriments", {}).get("energy-kcal_100g"),
                            "proteins": product.get("nutriments", {}).get("proteins_100g"),
                            "carbs": product.get("nutriments", {}).get("carbohydrates_100g"),
                            "fats": product.get("nutriments", {}).get("fat_100g"),
                        })
                return products
        except httpx.TimeoutException:
            logger.error(f"Timeout searching products for query: {query}")
            return []
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching products: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []

