# -*- coding:utf-8 -*-

"""
三角套利策略
"""

import sys
from aioquant import quant


def start_strategy():
    from strategy.strategy29 import Strategy29
    Strategy29()


if __name__ == "__main__":
    config_file = sys.argv[1]
    quant.start(config_file, start_strategy)
