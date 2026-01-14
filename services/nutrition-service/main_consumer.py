import asyncio
import logging

from infrastructure.consumers import run_consumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting nutrition-service consumer process...")
    asyncio.run(run_consumer())

