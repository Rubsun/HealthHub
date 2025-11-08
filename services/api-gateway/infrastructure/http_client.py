import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class HTTPClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def get(self, path: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}{path}"
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout calling {self.base_url}{path}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {self.base_url}{path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling {self.base_url}{path}: {e}")
            return None

    async def post(self, path: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}{path}"
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout calling {self.base_url}{path}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {self.base_url}{path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling {self.base_url}{path}: {e}")
            return None

    async def put(self, path: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}{path}"
                response = await client.put(url, json=data, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout calling {self.base_url}{path}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {self.base_url}{path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling {self.base_url}{path}: {e}")
            return None

    async def delete(self, path: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}{path}"
                response = await client.delete(url, headers=headers)
                response.raise_for_status()
                return response.json() if response.content else None
        except httpx.TimeoutException:
            logger.error(f"Timeout calling {self.base_url}{path}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {self.base_url}{path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling {self.base_url}{path}: {e}")
            return None



