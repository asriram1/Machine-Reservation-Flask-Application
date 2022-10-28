from datetime import datetime
global timeformat
timeformat = '%Y-%m-%d %H:%M:%S'


class Transaction:
    def __init__(self):
        self.id = -1
        self.resid = -1
        self.userid = -1
        self.price = 0.00
        self.type = ''
        self.time = ''
        return

    def __repr__(self):
        return f'Transaction object, id={self.id}, userid={self.userid}, price={self.price}, resid={self.resid}'

    def initfromvalues(self, tid: int, userid: int, price: float, resid: -1, typestr: str, timeval: str):
        self.id = tid
        self.userid = userid
        self.resid = resid
        self.price = price
        self.type = typestr
        self.time = timeval
        return

    def initfromjson(self, jsonstr: dict) -> None:
        transidkey = 'id'
        useridkey = 'user_id'
        pricekey = 'amount'
        residkey = 'reservation_id'
        timekey = 'datetime_stamp'
        typekey = 'type'

        tid = self.id
        userid = self.userid
        amount = self.price
        resid = self.resid
        time = self.time
        typeval = self.type

        if transidkey in jsonstr:
            try:
                tid = int(jsonstr[transidkey])
            except TypeError:
                tid = None
            except ValueError:
                tid = None

        if useridkey in jsonstr:
            try:
                userid = jsonstr[useridkey]
            except ValueError:
                userid = None

        if pricekey in jsonstr:
            try:
                price = float(jsonstr[pricekey])
            except ValueError:
                price = None

        if residkey in jsonstr:
            try:
                resid = int(jsonstr[residkey])
            except ValueError:
                resid = None

        if timekey in jsonstr:
            timeval = jsonstr[timekey]

        if typekey in jsonstr:
            typeval = jsonstr[typekey]

        self.initfromvalues(tid, userid, price, resid, typeval, timeval)
        return
