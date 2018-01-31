#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Michael Morscher'
__description__ = 'Module that contains base functions for separating playtime into blocks'
__copyright__ = "Copyright 2018, block module"
__version__ = "0.1.1"
__maintainer__ = "Michael Morscher"
__email__ = "ich@morschi.com"
__status__ = "in development"

import logging
import datetime
import configuration
from database import Database

# create logging
log = logging.getLogger("steam")
log.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
log.addHandler(sh)


def block_finalize(database, id_user, id_app, block_start, block_duration, block_number, block_counter, block_total_game_time):
    """
    Finalize a block and add it to the database
    :param object database: database object
    :param integer id_user: steam user ID
    :param integer id_app: steam app ID
    :param  block_start: time when block starts
    :param  block_duration: duration of block
    :param  block_number: unique block ID
    :param  block_counter: amount of blocks found
    :param  block_total_game_time: total game time in blocks
    :return: block number, total game time in block
    :rtype: integer, integer
    """
    logger = logging.getLogger("steam.blocker.block_finalize")

    # check if any blocks were found otherwise abort
    if block_counter > 0:

        # increase block and playtime counters
        block_number += 1
        block_total_game_time += block_duration

        # add new block to database
        logger.info('Adding block {0} from {1} to {2} with {3} minutes duration.'
                    .format(block_number, block_start, block_start + datetime.timedelta(minutes=block_duration),
                            block_duration))
        database.block_add(id_user, id_app, block_start, block_duration)

    return block_number, block_total_game_time


def find_blocks_day_game(database, id_user, id_app, day):
    """
    Find all game blocks for a given game in a given day
    :param object database: database object
    :param integer id_user: steam user ID
    :param integer id_app: steam app ID
    :param str day: day that will be searched
    :return: block number, total game time in block
    :rtype: integer, integer
    """
    logger = logging.getLogger("steam.blocker.find_blocks_day_game")
    logger.info("Trying to find blocks for user {0} with game {1} on the {2}".format(id_user, id_app, day))

    # variables
    total_game_time_old = 0
    block_counter = 0
    block_detect = 0
    block_start = 0
    block_duration = 0
    block_number = 0
    block_total_game_time = 0

    for data in database.playtime_get_1day_game(id_user, id_app, day):
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
                block_number, block_total_game_time = block_finalize(database, id_user, id_app, block_start, block_duration, block_number, block_counter, block_total_game_time)
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
    block_number, block_total_game_time = block_finalize(database, id_user, id_app, block_start, block_duration, block_number, block_counter, block_total_game_time)

    logger.info("{0} blocks in time frame with a total of {1} minutes play time".format(block_number, block_total_game_time))
    return block_number, block_total_game_time


def find_blocks_day(database, id_user, day):
    """
    Find all blocks for a given user in a given day
    :param object database: database object
    :param integer id_user: steam user ID
    :param str day: day that should be searched
    :return:
    """
    logger = logging.getLogger("steam.blocker.find_blocks_day")
    logger.info("Trying to find blocks for user {0} for all games on the {1}".format(id_user, day))

    block_number = 0
    total_game_time = 0

    for data in database.playtime_get_1day_game_ids(id_user, day):
        temp_number, temp_game_time = find_blocks_day_game(database, id_user, data[0], day)
        block_number += temp_number
        total_game_time += temp_game_time

    logger.info("{0} blocks with a total game time of {1} minutes found!".format(block_number, total_game_time))

    # remove raw playtime entries from database - blocks have been found and already added to the database
    database.playtime_delete_1day(id_user, day)


if __name__ == "__main__":
    log.info("Execution started")

    # create database connection
    log.info("Connecting to database {0} on {1}".format(configuration.database_name.encode('utf8'),
                                                        configuration.database_host.encode('utf8')))
    database_connection = ''
    try:
        database_connection = Database(configuration.database_host, configuration.database_user, configuration.database_password,
                            configuration.database_name)
    except Exception, e:
        log.warning("Database connection not successful!")
        log.error("{0}".format(e))
        log.error("Aborting run...")
        exit(255)

    # retrieve list of all active users to check
    users = database_connection.user_get_list_active()

    for day in range(1, 32):

        for user in users:

            find_blocks_day(database_connection, user[0], "2016-09-{0:0=2d}".format(day))
            #find_blocks_day(user[0], "2016-10-{0:0=2d}".format(day))
            #find_blocks_day(user[0], "2017-11-{0:0=2d}".format(day))

    #print database.block_playtime_day_total(4, "2016-02-23")
    #print database.block_playtime_month(4, "2016-02")
    #print database.block_playtime_month(3, "2016-02")
    #print database.block_playtime_month(6, "2016-02")

    log.info("Execution stopped")
