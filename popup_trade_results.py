#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2019/6/30
# Function: 

from tkinter import ttk, Label, Button, StringVar, LEFT, Frame, \
    messagebox, OptionMenu, IntVar,ACTIVE, DoubleVar
import config
from popup_login import MyDialog
import datetime
from datepicker import Datepicker

def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


class PopupTradeResults(MyDialog):
    def __init__(self, parent, trade_records, title=u"收益统计"):
        self.trade_records = trade_records
        self.end = datetime.datetime.now()
        self.beg = self.end - datetime.timedelta(days=1)
        datetime.datetime.combine(self.beg, datetime.time.min)

        MyDialog.__init__(self, parent, title, modal=True)

    def cmd_money_change(self, event):
        self.money.get()
        self.update_trades()

    def cmd_recent1(self):
        self.end = datetime.datetime.now()
        self.beg = self.end - datetime.timedelta(days=1)
        datetime.datetime.combine(self.beg, datetime.time.min)
        self.update_trades()

    def cmd_recent7(self):
        self.end = datetime.datetime.now()
        self.beg = self.end - datetime.timedelta(days=7)
        datetime.datetime.combine(self.beg, datetime.time.min)
        self.update_trades()

    def cmd_recent30(self):
        self.end = datetime.datetime.now()
        self.beg = self.end - datetime.timedelta(days=30)
        datetime.datetime.combine(self.beg, datetime.time.min)
        self.update_trades()

    def cmd_search(self):
        if not (self.dpk_end.current_date and self.dpk_beg.current_date):
            # messagebox.showerror(u"提示", "请先选择筛选日期")
            # return
            pass
        else:
            self.end = self.dpk_end.current_date
            datetime.datetime.combine(self.end, datetime.time.max)
            self.beg = self.dpk_beg.current_date
            datetime.datetime.combine(self.beg, datetime.time.min)
        self.update_trades()

    def update_trades(self):
        self.tree.delete(*self.tree.get_children())
        index = 0
        select_money = self.money.get()
        total_profit = 0
        for trade_group in self.trade_records:
            trades = trade_group.get("trades", [])
            for trade in trades:
                sell_time = trade.get("sell_time", None)
                if not (sell_time and trade.get("is_sell", 0)):
                    continue

                if not (sell_time <= self.end and sell_time>=self.beg):
                    continue

                if select_money != u"所有":
                    if trade['money'] != select_money:
                        continue

                total_profit += trade.get("profit", 0)
                trade_pair = "{}/{}".format(trade["coin"], trade['money'])
                self.tree.insert("", index, values=(index + 1,
                                                    trade_pair,
                                                    trade["sell_time"].strftime("%y-%m-%d %H:%M:%S") if trade.get(
                                                        "sell_time", None) else "",
                                                    round(trade["cost"], 6),
                                                    round(trade.get("profit", 0), 6),
                                                    round(trade.get("profit_percent", 0) * 100, 3)))
                index += 1

        self.trades_num.set(index)
        self.total_profit.set(round(total_profit, 6))


    def setup_ui(self):
        frame = Frame(self)
        self.lst_money = [u"所有", "USDT", "BTC", "ETH"]
        for k,v in config.PLATFORMS.items():
            for money in v["trade_pairs"].keys():
                self.lst_money.append(money)

        self.lst_money = list(set(self.lst_money))
        self.money = StringVar()
        self.money.set(u"所有")
        Label(frame, text=u"计价货币:", width=8).grid(row=0, column=0)
        self.opt_money = OptionMenu(frame, self.money, *self.lst_money, command=self.cmd_money_change)
        self.opt_money.grid(row=0, column=1)

        Button(frame, text=u"近1天", command=self.cmd_recent1, width=8, font=("", 10, 'bold')).grid(row=0, column=2)
        Button(frame, text=u"近7天", command=self.cmd_recent7, width=8, font=("", 10, 'bold')).grid(row=0, column=3)
        Button(frame, text=u"近1月", command=self.cmd_recent30, width=8, font=("", 10, 'bold')).grid(row=0, column=4)

        Label(frame, text=u"筛选日期:", width=8).grid(row=1, column=0)
        self.dpk_beg = Datepicker(master=frame, entrywidth=12)
        self.dpk_beg.grid(row=1, column=1)
        Label(frame, text=u"----", width=2).grid(row=1, column=2)
        self.dpk_end = Datepicker(master=frame, entrywidth=12)
        self.dpk_end.grid(row=1, column=3)
        Button(frame, text=u"筛 选", command=self.cmd_search, width=8, font=("", 10, 'bold')).grid(row=1, column=4)

        columns = (
            u"序号", u"交易对", u"结单时间", u"持仓成本", u"结单收益", u"盈利比%")
        self.tree = ttk.Treeview(frame, show="headings", columns=columns, height=15)  # 表格
        for name in columns:
            if name == u"序号":
                self.tree.column(name, width=30, anchor="center")
            elif name in [u"结单时间"]:
                self.tree.column(name, width=130, anchor="center")
            else:
                self.tree.column(name, width=90, anchor="center")
            self.tree.heading(name, text=name, command=lambda _col=name:treeview_sort_column(self.tree, _col, False))

        self.tree.grid(row=2, column=0, columnspan=5)
        frame.pack(padx=5, pady=5)

        frame2 = Frame(self)
        Label(frame2, text=u"累计盈利:", width=8).grid(row=3, column=0)
        self.total_profit = DoubleVar()
        self.total_profit.set(0)
        Label(frame2, textvariable=self.total_profit, width=14, font=("", 12, 'bold')).grid(row=3, column=1)

        Label(frame2, text=u"成交单数:", width=8).grid(row=3, column=2)
        self.trades_num = IntVar()
        self.trades_num.set(0)
        Label(frame2, textvariable=self.trades_num, width=5, font=("", 12, 'bold')).grid(row=3, column=3)

        frame2.pack(pady=10)
        self.update_trades()

        # f = Frame(self)
        # # 创建"确定"按钮,位置绑定self.on_ok处理方法
        # w = Button(f, text=u"确定", width=10, command=self.on_ok, default=ACTIVE)
        # w.pack(side=LEFT, padx=5, pady=5)
        # # 创建"确定"按钮,位置绑定self.on_ok处理方法
        # w = Button(f, text=u"取消", width=10, command=self.on_cancel)
        # w.pack(side=LEFT, padx=5, pady=5)
        # self.bind("<Return>", self.on_ok)
        # self.bind("<Escape>", self.on_ok)
        # f.pack()


    # 该方法可对用户输入的数据进行校验
    def validate(self):
        return True

    # 该方法可处理用户输入的数据
    def process_input(self):
        return True




if __name__ == '__main__':
    pass