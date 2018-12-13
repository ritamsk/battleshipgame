import logging
import asyncio
#import mqtt

from hbmqtt.client import MQTTClient, ConnectException
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1

packet=0
answer=''
def int_convert(inputint):
    '''
    converts the grid letters to numbers
    '''
    letterconversion = { 0 : "A",
                         1 : "B",
                         2 : "C",
                         3 : "D",
                         4 : "E",
                         5 : "F",
                         6 : "G",
                         7 : "H",
                         8 : "I",
                         9 : "J"}
    return letterconversion[inputint]


def print_board(player_board, opponent_board):
    '''
    prints the boards to the screen including scores and sunk ships
    '''
    alphabet = ["A","B","C","D","E","F","G","H","I","J"]
    ships = ["B","B","B","B","D","D","D","D","D","D","C","C","C","C","C","C","T","T","T","T"]
    #if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
     #   os.system('clear')
    #elif sys.plaform.startswith('win'):
     #   os.system('clr')
    ship = 0
    print("Tracking Board", end="                                    "), print("Your Board")
    for i in range(11): # prints the tracking board for the opponent to terminal
        line=""
        lin =""
        for j in range(11):
            if (i==0) and (j!=0):
                line+=" "+alphabet[j-1]+"  "
                lin += " " + alphabet[j - 1] + "  "
            elif (j==0) and (i!=0):
                line+="{:>2} |".format(i)
                lin += "{:>2} |".format(i)

            elif (i==0) and (j==0):
                line+="    "
                lin +="    "
            elif (j>0) and (i>0):
                tmp=int_convert(j-1) + str(i)
                #print(tmp)
                if tmp not in opponent_board:
                    line+="   |" # for an "invisible game"
                    # comment the above and uncomment the line below to test:
                     #line+=" "+opponent_board[i-1][j-1]+" |"

                else:
                    line+="   |"
                if tmp not in player_board:
                    lin += " ~ |"
                else:
                    lin += " "+ ships[player_board.index(tmp)]+" |"
                    ship+=1
        print(line, end = "    "), print(lin)
        print("   -----------------------------------------", end = "     "),
        print("   -----------------------------------------")


def client_answer(C, header, answer):
    yield from C.publish(header, answer)
    logger.info("messages published")
    #yield from C.disconnect()



logger = logging.getLogger(__name__)
def get_answer(C, header):

    global packet, answer
    print('here')
   # C = MQTTClient()
    #yield from C.connect('mqtt://127.0.0.1:8080')
    yield from C.subscribe([
        (header, QOS_1),

    ])
    logger.info("Subscribed")
    print(header)
    print(answer)
    while answer == '':
        message = yield from C.deliver_message()
        packet = message.publish_packet
        answer = packet.payload.data.decode('utf-8')
        print(answer)
    yield from C.unsubscribe(['$SYS/broker/uptime', '$SYS/broker/load/#'])







def test_coro1(C, header, answer):
        yield from C.connect('mqtt://127.0.0.1:8080')
        yield from C.publish(header, answer)
        logger.info("messages published")

def get_fullboard(C, header, topic, board):
    print('topic of full board:', header + topic +'returnboard/')
    (asyncio.get_event_loop().run_until_complete(client_answer(C, header + topic +'returnboard/', board)))
    while answer == '':
        (asyncio.get_event_loop().run_until_complete(get_answer(C, topic + 'returnboard/')))

if __name__ == '__main__':
    id = '1'
    topic = 'client/' + id +'/'
    formatter = "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    formatter = "%(message)s"
    #logging.basicConfig(level=logging.DEBUG, format=formatter)
    C = MQTTClient()
    header = 'bd/two/'
    while answer != 'good':
        print('Hi there! Do you wanna play a game? Please, enter a game session name')
        session_name = input()
        asyncio.get_event_loop().run_until_complete(test_coro1(C, header + topic, bytearray(session_name, encoding='utf-8')))
        asyncio.get_event_loop().run_until_complete(get_answer(C, header + topic))
    if answer == "good":
        answer = ''
        header = 'game/'
        asyncio.get_event_loop().run_until_complete(client_answer(C, header + topic, b'makerandompole'))
        while answer == '':
            asyncio.get_event_loop().run_until_complete(get_answer(C, topic))
        client_board = answer
        client_board_b = bytearray(answer, encoding='utf-8')
        answer = ''
        asyncio.get_event_loop().run_until_complete(client_answer(C, header + topic + 'returnboard/', client_board_b))
        while answer == '':
            asyncio.get_event_loop().run_until_complete(get_answer(C, topic + 'returnboard/'))
        client_full_board= answer.split('|')[:-1]
        print_board(client_full_board, client_full_board)
        answer = ''
        header = 'bot/'
        asyncio.get_event_loop().run_until_complete(client_answer(C, header + topic, b'starting'))
        while answer=='':
            asyncio.get_event_loop().run_until_complete(get_answer(C,  topic))
        # header = 'client'
        print(topic)
        bot_board = answer
        bot_board_b = bytearray(answer, encoding='utf-8')
        answer = ''
        header = 'game/'
        asyncio.get_event_loop().run_until_complete(client_answer(C, header + topic + 'returnboard/', bot_board_b))
        while answer == '':
            asyncio.get_event_loop().run_until_complete(get_answer(C, topic + 'returnboard/'))
        bot_full_board = answer.split('|')[:-1]
        # header = 'client'
        print(bot_full_board)
        print(client_full_board)
        header = 'game/'
        corect_coord = False
        answer = ''
        while len(bot_full_board)>0 and len(client_full_board)>0:
            answer = ''
            header = 'game/'
            print("Please enter a coordinate you want to shoot on the opponent board!")
            coordinate = input()
            asyncio.ensure_future(client_answer(C, header+topic+'checkshoot/', bytearray(coordinate + '//', encoding='utf-8') + bot_board_b))
            while answer == '':
                asyncio.get_event_loop().run_until_complete(get_answer(C, topic +'checkshoot/'))
            try:
                bot_full_board.remove(coordinate)
            except ValueError:
                "Do nothing"
            else:
                "Do something with variable b"
            print('bot', bot_full_board)
            print_board(client_full_board, client_full_board)

            if answer != 'bad coordinate' and answer!='hit':
                answer = ''
                header = 'bot/'
                asyncio.ensure_future(client_answer(C, header+topic+'shoot/', client_board_b))
                while answer == '':
                    asyncio.get_event_loop().run_until_complete(get_answer(C, topic + 'shoot/checkshoot/'))
                    bot_shoot = answer.split('/')[0]
                    try:
                       client_full_board.remove(bot_shoot)
                    except ValueError:
                        "Do nothing"
                    else:
                        "Do something with variable b"

                    print("client", client_full_board)
                   # while answer == 'hit':
                    #    asyncio.get_event_loop().run_until_complete(get_answer(C, topic + 'shoot/checkshoot/'))
        if len(bot_full_board)>0:
            print('game over, you loser')
        else:
            print('YOU WIN')




