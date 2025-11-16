import asyncio
import logging
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from infrastructure.settings import settings
from infrastructure.consumers import setup_consumers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    broker = RabbitBroker(settings.rabbitmq_url)
    app = FastStream(broker)
    setup_consumers(app)
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())



