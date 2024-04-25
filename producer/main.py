import asyncio
import json
import aio_pika

from aiohttp import ClientSession, web
from aio_pika import ExchangeType

TASK_NUMBER = 0


async def process_tasks(channel, routing_key__, n=1000):
    global TASK_NUMBER
   
    for i in range(int(n)):
        task = json.dumps({
            "task_number": f"{TASK_NUMBER}",
            "body": "something_in_body"
            }).encode()
        TASK_NUMBER += 1
        exchange = await channel.declare_exchange(
            "tasks_exchange", 
            ExchangeType.DIRECT,
            durable=True
        )
        await exchange.publish(
            aio_pika.Message(body=task),
            routing_key=routing_key__
        )


async def init_rmq(channel, routing_key__):
    # exchange = await channel.get_exchange("tasks_exchange")

    direct_tasks_exchange = await channel.declare_exchange(name='tasks_exchange',
                                                            type=ExchangeType.DIRECT,
                                                            durable=True)
    queue = await channel.declare_queue(name='tasks_ready_queue', 
                                        auto_delete=False,
                                        durable=True)
    await queue.bind(direct_tasks_exchange, routing_key=routing_key__)


async def make_tasks(request) -> None:
    connection = await aio_pika.connect_robust(
            "amqp://admin:admin@localhost/",
        )
    routing_key__ = "tasks_ready"
    async with connection:
        
        channel = await connection.channel()

        await init_rmq(channel, routing_key__)
        
        n = request.rel_url.query['n']
        await process_tasks(channel, routing_key__, n)
    
    return web.Response(text=json.dumps("OK", ensure_ascii=False))


async def main():
    app = web.Application()
    app.add_routes([web.get('/make_tasks', make_tasks)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8083)
    await site.start()

    while True:
        await asyncio.sleep(3600)
        make_tasks()


if __name__ == "__main__":
    asyncio.run(main())
