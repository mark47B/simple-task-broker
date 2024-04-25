import logging
import asyncio
import time

import aio_pika


logger = logging.getLogger(__name__)

async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    connection = await aio_pika.connect_robust(
        "amqp://admin:admin@rabbitmq/"
    )

    queue_name = "tasks_ready_queue"

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, auto_delete=False, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print("--------------------")
                    print(message.body)
                    print("--------------------")
                    if queue.name in message.body.decode():
                        break


if __name__ == '__main__':
    time.sleep(5)
    try:
        asyncio.run(
            main()
        )
    except asyncio.CancelledError:
        logger.info('Main task cancelled')
    except Exception:
        logger.exception('Something unexpected happened')
    finally:
        logger.info("Shutdown complete")
