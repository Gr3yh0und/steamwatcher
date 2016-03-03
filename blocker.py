#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import datetime
from database import Database

__author__ = 'Michael Morscher'
__description__ = ''
__copyright__ = "Copyright 2016"
__version__ = "0.1"
__maintainer__ = "Michael Morscher"
__email__ = "morscher@hm.edu"
__status__ = "in development"

# create logging
logger = logging.getLogger("steam")
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)

# database configuration
database_host = "127.0.0.1"
database_user = "steamuser"
database_password = "steamuser!!345"
database_name = "steam"
database = Database(database_host, database_user, database_password, database_name)


def block_finalize(logger, block_start, block_duration, block_number, block_counter, block_total_game_time):
    if block_counter > 0:
        logger.info('BLOCK: From {0} with duration of {1} minutes. End at {2} '
                    .format(block_start, block_duration, block_start + datetime.timedelta(minutes=block_duration)))
        block_number += 1
        block_total_game_time += block_duration
    return block_number, block_total_game_time


def find_blocks_day_game(id_user, id_game, day):

    # variables
    total_game_time_old = 0
    block_counter = 0
    block_detect = 0
    block_start = 0
    block_duration = 0
    block_number = 0
    block_total_game_time = 0

    logger = logging.getLogger("steam.blocker.find_blocks_day_game")
    logger.info("Trying to find blocks for user {0} with game {1} on the {2}".format(id_user, id_game, day))

    for data in database.playtime_get_1day_game(id_user, id_game, day):
        total_game_time = data[2]

        # only for first iteration needed
        if total_game_time_old == 0:
            total_game_time_old = data[2]

        # compare old game time with current game time set
        if total_game_time != total_game_time_old:

            # count new block part
            block_counter += 1

            # add duration of block part to total block duration
            block_duration += (total_game_time - total_game_time_old)

            # save timestamp as beginning if first part of a new block
            if block_counter == 1:
                block_start = data[0]

            # reset block detection variable
            block_detect = 0

        # if no change in game time occurred
        else:

            # check if block detection variable has already been altered
            # This is needed as steam only counts 30 min but queries are done all 15 min
            if block_detect == 0:
                block_detect = 1

            # it looks like block has ended, so reset everything
            else:
                block_number, block_total_game_time = block_finalize(logger, block_start, block_duration, block_number, block_counter, block_total_game_time)
                block_counter = 0
                block_detect = 0
                block_start = 0
                block_duration = 0

        if block_counter > 0:
            logger.debug("{0} - [Total-Playtime: {1} --> {2} ({5}m)] - [Block-Count: {3}] - [Start: {4}]"
                         .format(data[0], total_game_time_old, total_game_time, block_counter, block_start, block_duration))

        # save game time for next iteration
        if total_game_time_old:
            total_game_time_old = data[2]

    # needed if game session goes into the next day (23:45 -> 0:00)
    block_number, block_total_game_time = block_finalize(logger, block_start, block_duration, block_number, block_counter, block_total_game_time)

    logger.info("{0} blocks in time frame with a total of {1} minutes play time".format(block_number, block_total_game_time))
    return block_number, block_total_game_time


def find_blocks_day(id_user, day):
    logger = logging.getLogger("steam.blocker.find_blocks_day")
    logger.info("Trying to find blocks for user {0} for all games on the {1}".format(id_user, day))

    block_number = 0
    total_game_time = 0

    for data in database.playtime_get_1day_game_ids(id_user, day):
        temp_number = 0
        temp_game_time = 0
        temp_number, temp_game_time = find_blocks_day_game(id_user, data[0], day)
        block_number += temp_number
        total_game_time += temp_game_time

    logger.info("{0} blocks with a total game time of {1} minutes found!".format(block_number, total_game_time))
    return




if __name__ == "__main__":

    find_blocks_day(4, "2016-02-25")
