import logging
import asyncio
import db_maybe
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1
#import mqtt

#
# This sample shows how to subscbribe a topic and receive data from incoming messages
# It subscribes to '$SYS/broker/uptime' topic and displays the first ten values returned
# by the broker.
#

logger = logging.getLogger(__name__)


@asyncio.coroutine
def uptime_coro():

    try:
        while True:
            C = MQTTClient()

            yield from C.connect('mqtt://127.0.0.1:8080')
            # Subscribe to '$SYS/broker/uptime' with QOS=1
            yield from C.subscribe([
                ('bd/#', QOS_1),

            ])
            logger.info("Subscribed")
            message = yield from C.deliver_message()
            packet = message.publish_packet
            get_request = packet.payload.data
            header = packet.variable_header.topic_name.split('/')
            if  get_request == b'bot':
                print("%d: %s => %s" % (1, packet.variable_header.topic_name, str))
                db_maybe.bot_session(C, packet.variable_header.topic_name, packet.payload.data)
            if header[1] == 'two':
                print("%d: %s => %s" % (1, packet.variable_header.topic_name, str))
                db_maybe.two_players_session(C, packet.variable_header.topic_name, packet.payload.data)

        yield from C.unsubscribe(['$SYS/broker/uptime', '$SYS/broker/load/#'])
        logger.info("UnSubscribed")
        yield from C.disconnect()
    except ClientException as ce:
        logger.error("Client exception: %s" % ce)

    yield from C.unsubscribe(['$SYS/broker/uptime', '$SYS/broker/load/#'])
    logger.info("UnSubscribed")

    yield from C.disconnect()




if __name__ == '__main__':
    formatter = "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)
    asyncio.get_event_loop().run_until_complete(uptime_coro())
    asyncio.get_event_loop().run_forever()
    print('smthng')
