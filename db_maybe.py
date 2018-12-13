import sqlite3
import logging
import time
import asyncio
#import mqtt
import os
logger = logging.getLogger(__name__)


#inside function
def creationgdb():
    conn = sqlite3.connect("D:\\gridgame\dbwithsessions.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE gamesession")
    cursor.execute("CREATE TABLE gamesession (gameID integer not null , gamename text, primary key (gameID)); ")
    conn.commit()

def db_answer(C, header, answer):
    print(header)
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



# api ?
def bot_session(C, header, message):
    # session with bot
    message = message.decode('utf-8')
    print(message)
    bd_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dbwithsessions.db")
    conn = sqlite3.connect(bd_file)
    cursor = conn.cursor()
    sessionname = str(message)
    print('bot')
    cursor.execute("select gameID from gamesession")
    results = cursor.fetchall()
    # making id
    if len(results) > 0:
        gameid = results[len(results) - 1][0] + 1
        print(gameid)
    else:
        gameid = 0
    botname = sessionname + str(gameid)
    cursor.execute("insert into gamesession values (?,?)", (gameid, botname))  # add session with bot
    conn.commit()
    conn.close()
    answer = b'good'
    db_answer(C, header, answer)


def two_players_session(C, header, message):
    message = message.decode('utf-8')
    print(message)
    conn = sqlite3.connect("D:\\gridgame\dbwithsessions.db")
    cursor = conn.cursor()
    sessionname = str(message)
    # find session name
    print('two players')

    print(sessionname)
    cursor.execute("SELECT * FROM gamesession WHERE gamename='%s'" % sessionname)
    results = cursor.fetchall()
    print(results)
    if len(results) == 0:
        answer =b'good'
        cursor.execute("select gameID from gamesession")
        results = cursor.fetchall()
        # making id
        if len(results) > 0:
            gameid = results[len(results) - 1][0] + 1
            print(gameid)
        else:
            gameid = 0

        cursor.execute("insert into gamesession values (?,?)", (gameid, sessionname))  # add session with bot

        conn.commit()
        conn.close()
        db_answer(C, header, answer)
        # calling game
    else:
        answer = b'bad'
        db_answer(C, header, answer)
        conn.commit()
        conn.close()
