# -*- encoding: UTF-8 -*-

import data_fetcher
import utils
import strategy.enter as enter
from strategy import turtle_trade
from strategy import backtrace_ma250
from strategy import breakthrough_platform
from strategy import parking_apron
from strategy import low_atr
import notify
import logging
import db


def process():
    logging.info("************************ process start ***************************************")
    utils.prepare()
    data_fetcher.run()

    check_exit()

    stocks = utils.get_stocks()
    m_filter = check_enter(end_date=None)
    results = list(filter(m_filter, stocks))

    logging.info('选股结果：{0}'.format(results))
    notify.notify('选股结果：{0}'.format(results))
    logging.info("************************ process   end ***************************************")


def check_enter(end_date=None):
    def end_date_filter(code_name):
        data = utils.read_data(code_name)
        result = backtrace_ma250.check(code_name, data, end_date=end_date)
        # result = parking_apron.check(code_name, data, end_date=end_date)
        # result = low_atr.check_low_increase(code_name, data, end_date=end_date)
        # result = enter.check_ma(code_name, data, end_date=end_date) \
        #     and breakthrough_platform.check(code_name, data, end_date=end_date)
        if result:
            message = turtle_trade.calculate(code_name, data)
            logging.info("{0} {1}".format(code_name, message))
            notify.notify("{0} {1}".format(code_name, message))
        return result

    # low_atr.check_low_increase(code_name, name, data)
    # and enter.check_breakthrough(stock, data, end_date=end_date) \

    return end_date_filter


def check_exit():
    t_shelve = db.ShelvePersistence()
    file = t_shelve.open()
    for key in file:
        code_name = file[key]['code_name']
        data = utils.read_data(code_name)
        if turtle_trade.check_exit(code_name, data):
            notify.notify("{0} 达到退出条件".format(code_name))
            logging.info("{0} 达到退出条件".format(code_name))
            del file[key]
        elif turtle_trade.check_stop(code_name, data, file[key]):
            notify.notify("{0} 达到止损条件".format(code_name))
            logging.info("{0} 达到止损条件".format(code_name))
            del file[key]

    file.close()

