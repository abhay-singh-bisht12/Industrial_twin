import asyncio
import logging
from amqtt.broker import Broker

logger = logging.getLogger("mqtt_broker")

config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '127.0.0.1:1883',
        },
        'ws': {
            'type': 'ws',
            'bind': '127.0.0.1:9001',
        },
    },
    'sys_interval': 10,
    'auth': {
        'allow-anonymous': True,
        'plugins': ['auth_anonymous']
    }
}

async def start_broker():
    broker = Broker(config)
    await broker.start()
    logger.info("Embedded MQTT Broker started on 127.0.0.1:1883 and WS 9001")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(start_broker())
    except KeyboardInterrupt:
        print("MQTT Broker stopped.")
