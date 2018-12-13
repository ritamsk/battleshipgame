from random import randint
import asyncio
import logging
import time
logger = logging.getLogger(__name__)
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1

logger = logging.getLogger(__name__)


def char_convert(inputchar):
    '''
    converts the grid letters to numbers
    '''
    letterconversion = {"A": 1,
                        "B": 2,
                        "C": 3,
                        "D": 4,
                        "E": 5,
                        "F": 6,
                        "G": 7,
                        "H": 8,
                        "I": 9,
                        "J": 10}
    return letterconversion[inputchar.upper()]


def int_convert(inputint):
    '''
    converts the grid letters to numbers
    '''
    letterconversion = { 1: "A",
                         2 : "B",
                         3 : "C",
                        4 : "D",
                         5 : "E",
                        6 : "F",
                         7 : "G",
                         8 : "H",
                        9 : "I",
                        10 : "J"}
    return letterconversion[inputint]

def random_coord():
    '''
    creates a random coordinate
    '''
    return ["A","B","C","D","E","F","G","H","I","J"][randint(0,9)]+str(randint(1,10))


def bot_answer(C,  header, answer):
  #  C = MQTTClient()
   # yield from C.connect('mqtt://127.0.0.1:8080')
    yield from C.publish(header, answer)
    logger.info("messages published")
    #yield from C.disconnect()

answer=''

def get_answer(C, header, topic='', tmpanswer=''):
    global packet, answer
    print(topic)
   # C = MQTTClient()
    #yield from C.connect('mqtt://127.0.0.1:8080')
    yield from C.subscribe([
        (header + topic, QOS_1),

    ])
    logger.info("Subscribed")
    while True:
        print(answer)
        message = yield from C.deliver_message()
        packet = message.publish_packet
        answer = packet.payload.data
        if answer != '':
            print(answer)
            if tmpanswer!='':
                tmpanswer=bytearray(tmpanswer + '/', encoding='utf-8')
                asyncio.ensure_future(bot_answer(C, topic, tmpanswer+answer))
            else:
                asyncio.ensure_future(bot_answer(C, topic, answer))

            yield from C.unsubscribe([header])
            logger.info("UnSubscribed")
           # yield from C.disconnect()
            break


def test_coro(C, header, answer):
    yield from C.publish(header, answer)
    logger.info("messages published")
    yield from C.disconnect()



def uptime_coro():
    global answer
    try:
        while True:
            answer = ''
            C = MQTTClient()

            yield from C.connect('mqtt://127.0.0.1:8080')
            # Subscribe to '$SYS/broker/uptime' with QOS=1
            yield from C.subscribe([
                ('bot/#', QOS_1)

            ])
            logger.info("Subscribed")
            message = yield from C.deliver_message()
            packet = message.publish_packet
            str = packet.payload.data.decode('utf-8')
            header = packet.variable_header.topic_name.split('/')[1:-1]
            topic = ''
            for s in header:
                topic += s + '/'
            answer = ''
            if str ==  'starting':
                    asyncio.ensure_future(bot_answer(C, 'game/bot/'+ topic, b'makerandompole'))
                    asyncio.ensure_future(get_answer(C, 'bot/', topic))
                    print('here3')
                    answer=''
            answer = ''
            coord = 0
            if header[len(header) - 1] == 'shoot':
                coord = random_coord()
                send = bytearray(coord + '//' + str, encoding='utf-8')
                asyncio.ensure_future(bot_answer(C, 'game/bot/' + topic + 'checkshoot/', send))
                asyncio.ensure_future(get_answer(C, 'bot/', topic + 'checkshoot/', coord))
                answer = answer.encode('utf-8')

            answer = ''


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

