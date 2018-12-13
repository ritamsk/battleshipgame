import asyncio
import logging
import time
logger = logging.getLogger(__name__)
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1
import game_logic

def game_answer(C, header, answer):
    formatter = "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    formatter = "%(message)s"
    logging.basicConfig(level=logging.DEBUG, format=formatter)
    it = asyncio.get_event_loop().create_future()
    asyncio.ensure_future(test_coro(C, header, answer))
    print('ok')


def test_coro(C, header, answer):
    yield from C.publish(header, answer)
    logger.info("messages published")
    yield from C.disconnect()

def uptime_coro():

    try:

        while True:
            C = MQTTClient()

            yield from C.connect('mqtt://127.0.0.1:8080')
            # Subscribe to '$SYS/broker/uptime' with QOS=1
            yield from C.subscribe([
                ('game/#', QOS_1)

            ])
            logger.info("Subscribed")
            message = yield from C.deliver_message()
            packet = message.publish_packet
            str = packet.payload.data.decode('utf-8')
            header = packet.variable_header.topic_name.split('/')[1:-1]
            print(header)
            topic=''
            for s in header:
                topic+=s+'/'
            print("%d: %s => %s" % (1, packet.variable_header.topic_name, str))
            if str =='makerandompole':
                print("%d: %s => %s" % (1, topic, str))
                randomboard =bytearray( game_logic.random_board_api(), encoding='utf-8')
                print(randomboard)
                game_answer(C, topic, randomboard)

            elif header[len(header)-1] == 'checkshoot':
                coordinate=str.split('//')[0]
                correct_coord = game_logic.coord_chek_api(coordinate)
                if correct_coord:
                    pole=str.split('//')[1].split('|')
                    print(coordinate, pole)
                    print("%d: %s => %s" % (1, topic, str))
                    shoot = game_logic.shoot_api(coordinate, pole)
                    print(shoot)
                    game_answer(C, topic, shoot)
                else:
                    game_answer(C, topic, b'bad coordinate' )

            elif header[len(header) - 1] == 'returnboard':
                print('str', str)
                board = str.split('|')
                board = game_logic.create_board_api(board)
                fullboard=b''
                for ship in board:
                    fullboard += bytearray(ship+'|', encoding='utf-8')
                print(fullboard)
                game_answer(C, topic, fullboard)

               # maybedb.two_players_session(C, packet.variable_header.topic_name, packet.payload.data)

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

