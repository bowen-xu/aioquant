# -*- coding:utf-8 -*-

"""
三角套利策略
"""

from aioquant.configure import config
from aioquant import const
from aioquant.tasks import LoopRunTask, SingleTask
from aioquant.trade import Trade
from aioquant.utils import logger
from aioquant.order import Order, ORDER_TYPE_MARKET
from aioquant.market import MarketSubscribe, Orderbook
from aioquant.utils.decorator import async_method_locker


class Strategy29:

    def __init__(self):
        self._a_orderbook_ok = False
        self._a_orderbook = None
        self._b_orderbook_ok = False
        self._b_orderbook = None
        self._c_orderbook_ok = False
        self._c_orderbook = None

        # 交易对象A (ETH/USDT)
        params = {
            "strategy": config.strategy,
            "platform": config.A["platform"],
            "symbol": config.A["symbol"],
            "account": config.A["account"],
            "access_key": config.A["access_key"],
            "secret_key": config.A["secret_key"],
            "order_update_callback": self.on_event_order_update_callback,
            "init_callback": self.on_event_init_callback,
            "error_callback": self.on_event_error_callback
        }
        self._a_trader = Trade(**params)

        # 交易对象B (BTC/USDT)
        params = {
            "strategy": config.strategy,
            "platform": config.B["platform"],
            "symbol": config.B["symbol"],
            "account": config.B["account"],
            "access_key": config.B["access_key"],
            "secret_key": config.B["secret_key"],
            "order_update_callback": self.on_event_order_update_callback,
            "init_callback": self.on_event_init_callback,
            "error_callback": self.on_event_error_callback
        }
        self._b_trader = Trade(**params)

        # 交易对象C (ETH/BTC)
        params = {
            "strategy": config.strategy,
            "platform": config.C["platform"],
            "symbol": config.C["symbol"],
            "account": config.C["account"],
            "access_key": config.C["access_key"],
            "secret_key": config.C["secret_key"],
            "order_update_callback": self.on_event_order_update_callback,
            "init_callback": self.on_event_init_callback,
            "error_callback": self.on_event_error_callback
        }
        self._c_trader = Trade(**params)

        # 订阅行情
        MarketSubscribe(const.MARKET_TYPE_ORDERBOOK, config.A["platform"], config.A["platform"], self.on_event_orderbook_update)
        MarketSubscribe(const.MARKET_TYPE_ORDERBOOK, config.B["platform"], config.B["platform"], self.on_event_orderbook_update)
        MarketSubscribe(const.MARKET_TYPE_ORDERBOOK, config.C["platform"], config.C["platform"], self.on_event_orderbook_update)

        # 定时任务
        LoopRunTask.register(self.check_orderbook, 60)  # 定时每隔60秒检查一次订单薄

    @async_method_locker("on_event_init_callback", wait=False, timeout=5)
    async def on_event_init_callback(self, success: bool, **kwargs):
        """初始化回调"""
        logger.info("success:", success, "kwargs:", kwargs, caller=self)
        # 1. 判断A,B,C是否都初始化成功
        # 2. 如果失败了，推送消息通知，同时标记程序不能再继续往下执行了

    @async_method_locker("on_event_error_callback", wait=False, timeout=5)
    async def on_event_error_callback(self, error, **kwargs):
        """错误回调"""
        logger.info("error:", error, "kwargs:", kwargs, caller=self)
        # 1. 推送报错信息 。。。
        # 2. 标记错误，是否对程序有影响，是否需要对程序做出必要调整。。。

    async def on_event_orderbook_update(self, orderbook: Orderbook):
        """订单薄更新回调"""

        if orderbook.platform == config.A["platform"] and orderbook.symbol == config.A["symbol"]:
            self._a_orderbook_ok = True
            self._a_orderbook = orderbook
        elif orderbook.platform == config.B["platform"] and orderbook.symbol == config.B["symbol"]:
            self._b_orderbook_ok = True
            self._b_orderbook = orderbook
        elif orderbook.platform == config.C["platform"] and orderbook.symbol == config.C["symbol"]:
            self._c_orderbook_ok = True
            self._c_orderbook = orderbook

        # 判断maker和taker订单薄是否准备就绪
        if not self._a_orderbook_ok or not self._b_orderbook_ok or not self._c_orderbook_ok:
            logger.warn("orderbook not ok.", caller=self)
            return

        # A同时进行买入和卖出ETH的检查
        SingleTask.run(self.a_do_action_buy)
        SingleTask.run(self.a_do_action_sell)

    @async_method_locker("a_do_action_buy", wait=False, timeout=5)
    async def a_do_action_buy(self):
        """A市场用USDT买入ETH"""
        # 1. 当前是否存在未完成的一次三角套利循环；
        # 2. 是否满足买入条件
        # 3. 挂单，需要计算挂单价格、数量；
        # 4. 记录挂单的订单id，订单价格，订单量
        # 5. 挂单失败之后处理。。。

    @async_method_locker("a_do_action_sell", wait=False, timeout=5)
    async def a_do_action_sell(self):
        """A市场把ETH卖出成USDT"""
        # 1. 当前是否存在未完成的一次三角套利循环；
        # 2. 是否满足买入条件
        # 3. 挂单，需要计算挂单价格、数量；
        # 4. 记录挂单的订单id，订单价格，订单量
        # 5. 挂单失败之后处理。。。

    @async_method_locker("on_event_order_update_callback", wait=True, timeout=5)
    async def on_event_order_update_callback(self, order: Order):
        """订单成交"""
        # 1. 订单是否成交？完全成交或部分成交？
        # 2. 如果是A订单成交，根据成交量，判断是否立即进行对冲追单；使用协程并发执行对冲追单；
        #       SingleTask.run(self._b_trader.create_order, b_price, b_quantity, order_type=ORDER_TYPE_MARKET)
        #       SingleTask.run(self._c_trader.create_order, c_price, c_quantity, order_type=ORDER_TYPE_MARKET)
        # 3. 如果是B,C订单成交，进入检查程序，检查此次三角套利是否完成；
        # 4. 如果B,C对冲追单失败，如何处理？发出警报？

    @async_method_locker("check_orderbook", wait=False, timeout=2)
    async def check_orderbook(self, *args, **kwargs):
        """检查订单薄"""
        pass
        # 1. 检查A,B,C订单薄是否正常
        # 2. 如果存在行情异常，停止三角套利；
        # 3. 推送报警消息。。停止程序。。
