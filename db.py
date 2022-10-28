import sqlite3
import os.path
from datetime import datetime, timedelta
from math import ceil
import random, string


class DBCls:
    # Database Class
    def __init__(self):
        self.__Name = 'reservation.db'
        self.__Fdr = 'Database'
        self.__opnDB()
        self.__TFrmt = '%Y-%m-%d %H:%M:%S'
        pass

    def __gPth(self):
        # get database config file path
        basedir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(basedir, self.__Fdr, self.__Name)

    def __opnDB(self):
        # open Database
        if not os.path.exists(self.__gPth()):
            self.__conn = self.mkdb()
        else:
                    # check_same_thread is extremely important for flask integration
                    # there may be some concurrency problems, but this is the only way
                    # that a DB connection can be defined in one thread and used in another
            self.__conn = sqlite3.connect(self.__gPth(), check_same_thread=False)
        return

    def mkdb(self):
        # create database since old one is not found.
        print(f'A reservations database was not found.\nA new one will be created\n')
        if not os.path.exists(self.__Fdr):
            os.mkdir(self.__Fdr)

        dbexists = os.path.exists(self.__gPth())
        dbconn = sqlite3.connect(self.__gPth(), check_same_thread=False)

        if not dbexists:
            userstmt = """ CREATE TABLE Users (
                                ID INTEGER PRIMARY KEY NOT NULL,
                                Username TEXT NOT NULL UNIQUE,
                                Password TEXT NOT NULL,
                                IsActive INTEGER NOT NULL CHECK (IsActive IN (0, 1)),
                                IsFacilityManager INTEGER NOT NULL CHECK (IsFacilityManager IN (0, 1)),
                                ActiveToken TEXT
                            ); """
            dbconn.execute(userstmt)
            self.popusertable(dbconn)

            mchstmt = """ CREATE TABLE Machines (
                        ID INTEGER PRIMARY KEY NOT NULL,
                        MType INTEGER NOT NULL
                    ); """
            dbconn.execute(mchstmt)
            self.popmt(dbconn)

            mpstmt = """ CREATE TABLE ResItemInfo (
                        IType INTEGER PRIMARY KEY NOT NULL,
                        Name TEXT,
                        IsMachine INTEGER NOT NULL CHECK (IsMachine IN (0, 1)),
                        Duration_Hrs Double NOT NULL,
                        Price DOUBLE NOT NULL
                    ); """
            dbconn.execute(mpstmt)
            self.popmpt(dbconn)

            # datetime is needed to create an automatic local timestamp
            # because values will be passed as local times
            trstmt = """ CREATE TABLE Transactions (
                        TxType VARCHAR NOT NULL CHECK (TxType in ('Create', 'Cancel', 'AddFunds')),
                        TxTime DateTime NOT NULL DEFAULT (datetime('now', 'localtime')),
                        CustomerID INTEGER NOT NULL,
                        Amount DOUBLE NOT NULL,
                        Serial Integer
                    ); """
            dbconn.execute(trstmt)

            rsstmt = """ CREATE TABLE ResStatus (
                        Serial INTEGER PRIMARY KEY NOT NULL,
                        IsActive INTEGER NOT NULL CHECK (IsActive IN (0, 1))
                    );  """
            dbconn.execute(rsstmt)

            rmstmt = """ CREATE TABLE ResMachines (
                        Serial INTEGER NOT NULL,
                        MachineID INTEGER NOT NULL,
                        TimeStart TEXT,
                        TimeEnd TEXT
                    ); """
            dbconn.execute(rmstmt)

            # This is something I initially overlooked
            # without this, only the first table will be created in the local file
            # All of the others will be created in memory
            # Because of that, everything will work fine during a run
            # where the DB was created,
            # but the next run with the DB already existing
            # would throw an error because there would only be one table in it
            # That's probably extremely basic for someone who works with SQLite3,
            # but it's an epiphany for me late at night
            dbconn.commit()

        return dbconn

    @staticmethod
    def popmt(dbconn):
        # insert values into machine table

        # yes, this could be done a lot better
        # because the ID is derived from the type
        # i.e. [TypeDigit][MachineCount],
        # but this is "simpler"
        insstmt = """
            INSERT INTO Machines (ID, MType)
            VALUES
            (101, 1),
            (102, 1),
            (103, 1),
            (104, 1),
            (105, 1),
            (106, 1),
            (107, 1),
            (108, 1),
            (109, 1),
            (110, 1),
            (111, 1),
            (112, 1),
            (113, 1),
            (114, 1),
            (115, 1),
            (201, 2),
            (202, 2),
            (301, 3),
            (302, 3),
            (401, 4),
            (402, 4),
            (501, 5),
            (601, 6)
        """
        dbconn.execute(insstmt)
        # have to commit after every DB modification so these transactions are saved
        dbconn.commit()
        pass

    @staticmethod
    def popmpt(dbconn):
        # insert values into ResItemInfo table
        insstmt = """
                INSERT INTO ResItemInfo (IType, Name, IsMachine, Duration_Hrs, Price)
                VALUES
                (1, 'Workshop', 0, 1, 99),
                (2, 'Mini Microvac', 1, 1, 2000),
                (3, 'Irradiator', 1, 1, 2200),
                (4, 'Polymer Extruder', 1, 1, 500),
                (5, 'High Velocity Crusher', 1, 0.5, 10000),
                (6, '1.21 Gigawatt Lightning Harvester', 1, 1, 8800)
            """
        dbconn.execute(insstmt)
        # have to commit after every DB modification so these transactions are saved
        dbconn.commit()
        pass

    @staticmethod
    def popusertable(dbconn):
        # populating with a facility manager test account
        # so normal users aren't created with facility manager credentials
        # but the instructors can do testing with facility manager info
        insstmt = """
                        INSERT INTO Users (Username, Password, IsActive, IsFacilityManager)
                        VALUES ('TESTFM', 'ABC123', 1, 1), ('TESTCLIENT', 'DEF456', 1, 0)
                    """
        dbconn.execute(insstmt)
        # have to commit after every DB modification so these transactions are saved
        dbconn.commit()
        return

    def ismvald(self, itype):
        # check if the machine item type is valid
        cmd = f"""
            SELECT * FROM ResItemInfo
            Where IType = {itype}
        """
        cur = self.__conn.cursor()
        cur.execute(cmd)
        return cur.fetchone() is not None

    def login(self, uname, pw):
        # check if the machine item type is valid
        cmd = f"""
                    SELECT * FROM Users
                    WHERE Username = '{uname}' AND Password = '{pw}'
                """
        cur = self.__conn.cursor()
        cur.execute(cmd)
        return cur.fetchone() is not None

    def register(self, uname, pw, isfm, isactive):
        if self.userexists(uname):
                # username already registered
            return False
        else:
            cmd = f"""
                        INSERT INTO Users
                        (Username, Password, IsActive, IsFacilityManager)
                        VALUES 
                        ('{uname}', '{pw}', {int(isactive)}, {int(isfm)})
                    """
            cur = self.__conn.cursor()
            cur.execute(cmd)
            if cur.rowcount != 1:
                # update failed, no need to commit changes
                return False
            else:
                # insert was successful
                self.__conn.commit()
                return True

    def isuserfacilitymanager(self, uname: str) -> bool:
        cmd = f"""
                    SELECT IsFacilityManager FROM Users
                    WHERE Username = '{uname}'
                """
        cur = self.__conn.cursor()
        cur.execute(cmd)
        result = cur.fetchone()
        if result is None:
            return False
        else:
            return result[0] == 1

    def userexists(self, uname: str) -> bool:
        cmd = f"""
                    SELECT * FROM Users
                    WHERE Username = '{uname}'
                """
        cur = self.__conn.cursor()
        cur.execute(cmd)
        return cur.fetchone() is not None

    def generatetoken(self, uname: str) -> str:
        newtoken = self.randomstring(12)
        settokensuccess = self.settoken(uname, newtoken)
        if not settokensuccess:
            # getting token failed
            return ''
        else:
            return newtoken

    @staticmethod
    def randomstring(strlen: int) -> str:
        # taken from https://pynative.com/python-generate-random-string/
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(strlen))

    def settoken(self, uname: str, newtoken: str) -> bool:
            # if an empty string is passed, set newtoken to Null instead
            # empty strings are only used to revoke tokens
        if newtoken == '':
            newtokenval = 'NULL'
        else:
            newtokenval = f"'{newtoken}'"
        cmd = f"UPDATE Users Set ActiveToken = {newtokenval} WHERE Username = '{uname}'"
        return self.runupdatecommand(cmd)

    def runupdatecommand(self, cmd: str) -> bool:
        # defining this centrally because it just makes sense
        # and I always forget to commit if the update is successful
        cur = self.__conn.cursor()
        cur.execute(cmd)
        if cur.rowcount != 1:
            return False
        else:
            self.__conn.commit()
            return True

    def runtransaction(self, cmdlist: list) -> bool:
        cur = self.__conn.cursor()
        cur.execute('BEGIN TRANSACTION;')

        for cmd in cmdlist:
            try:
                rslt = cur.execute(cmd)
                success = (rslt.rowcount == 1)
            except sqlite3.Error:
                success = False
            if not success:
                # something went wrong,
                # rollback and return False
                cur.execute('ROLLBACK;')
                return False
        # everything completed successfully,
        # commit transaction and return True
        cur.execute('COMMIT;')
        self.__conn.commit()
        return True

    def revoketoken(self, uname: str) -> bool:
        return self.settoken(uname, '')

    def istokenvalid(self, uname: str, token: str) -> bool:
        cmd = f"SELECT ActiveToken from USERS WHERE Username = '{uname}'"
        cur = self.__conn.cursor()
        result = cur.execute(cmd).fetchone()
        if result is None:
            return False
        else:
            return result[0] == token

    def getprofiledict(self, uname: str, restrictresults: bool) -> dict:
        cmd = f"""
                    SELECT IsActive, 
                    CASE When IsFacilityManager = '1' Then 'Facility Manager' Else 'Client' End as Type FROM Users
                    WHERE Username = '{uname}'
                """
        cur = self.__conn.cursor()
        cur.execute(cmd)
        result = cur.fetchone()
        if result is None:
            return None
        else:
            retdict = {}
            names = list(map(lambda x: x[0], cur.description))
            for name, value in zip(names, result):
                retdict[name] = value
            balance = self.getbalance(uname)
            retdict['Funds'] = balance
            return retdict
        pass

    def changeusername(self, uname: str, newuname: str) -> bool:
        # need to check that the existing username exists
        # and the new username doesn't exist
        if not self.userexists(uname) or self.userexists(newuname):
            return False
        else:
            cmd = f"""
                        UPDATE Users
                        SET Username = '{newuname}'
                        WHERE Username = '{uname}'
                    """
            return self.runupdatecommand(cmd)

    def setstatus(self, uname, newstatus: str) -> bool:
        if not self.userexists(uname) or newstatus not in (True, False):
            return False
        else:
            if newstatus:
                newstatusval = 1
            else:
                newstatusval = 0
            cmd = f"""
                        UPDATE Users
                        SET IsActive = '{newstatusval}'
                        WHERE Username = '{uname}'
                    """
            return self.runupdatecommand(cmd)

    def setfacilitymanager(self, uname, newvalue: str) -> bool:
        if not self.userexists(uname) or newvalue not in ('0', '1'):
            return False
        else:
            cmd = f"""
                        UPDATE Users
                        SET IsFacilityManager = '{newvalue}'
                        WHERE Username = '{uname}'
                    """
            return self.runupdatecommand(cmd)

    def gettranslistcmd(self, user: str, starttime: datetime, endtime: datetime) -> str:
        cmd = "SELECT Serial as 'TransactionID', Username, Amount as 'Price' " \
              "FROM Transactions " \
              "JOIN Users on Users.ID = Transactions.CustomerID"
        whereclause = ''
        if user is not None:
            userid = self.getuserid(user)
            whereclause = f" WHERE CustomerID = '{userid}'"
        if starttime is not None:
            try:
                timecond = f"TXTime >= '{starttime}' AND TXTime <= '{endtime}'"
                if whereclause == '':
                    whereclause = f' WHERE {timecond}'
                else:
                    whereclause += f' AND {timecond}'
            except ValueError:
                # invalid time format, just don't pass time
                pass
        return cmd + whereclause

    def gettranslist(self, user: str, starttime: datetime, endtime: datetime) -> list:
        cmd = self.gettranslistcmd(user, starttime, endtime)
        if cmd == '':
            return None
        cur = self.__conn.cursor()
        cur.execute(cmd)
        result = cur.fetchall()
        if result is None:
            return None
        else:
            retlist = []
            names = list(map(lambda x: x[0], cur.description))
            for record in result:
                recorddict = {}
                for name, value in zip(names, record):
                    recorddict[name] = value
                    # this looks kind of stupid, but this implementation
                    # uses serial as a universal identifier
                    # and doesn't have separate TransactionID and ResID values
                    # because of this, appropriately returning ResList means returning a list
                    # containing the same ResID value
                recorddict['ResList'] = [recorddict['TransactionID']]
                retlist.append(recorddict)
            return retlist

    def getuserid(self, uname):
        if not self.userexists(uname):
            return -1
        else:
            cmd = f"""
                    SELECT ID
                    FROM Users
                    WHERE Username = '{uname}'
                """
            cur = self.__conn.cursor()
            result = cur.execute(cmd).fetchone()
            if result is None:
                return -1
            else:
                return int(result[0])

    def makeres(self, uname: str, stime: datetime, etime: datetime, machineid: int) -> bool:
        userid = self.getuserid(uname)

        rescreatestatus = self.canresbecreated(userid, stime, etime, machineid)
        if type(rescreatestatus) is str:
            return rescreatestatus

        resprice = self.getresprice(machineid, stime, etime)
        resserial = self.getnextserial()
        if resserial < 1:
            return 'Unable to get an ID for the reservation'
        cmdlist = [
            f'INSERT INTO ResStatus (Serial, IsActive) VALUES ({resserial}, 1);',
            f"""INSERT INTO ResMachines
                    (Serial, MachineID, TimeStart, TimeEnd)
                    VALUES 
                    ({resserial}, {machineid}, '{stime.strftime(self.__TFrmt)}', '{etime.strftime(self.__TFrmt)}');""",
            f"""INSERT INTO Transactions (TxType, CustomerID, Amount, Serial)
                    VALUES 
                    ('Create', {userid}, {resprice}, {resserial});"""
        ]
        createresult = self.runtransaction(cmdlist)
        if type(createresult) is bool:
            return createresult
        else:
            return 'Unable to create result'

    def canresbecreated(self, userid: int, stime: datetime, etime: datetime, machineid: int) -> bool:
        if userid < 0:
            return 'Cannot create a result for a negative userid'
        elif not self.ismvald(machineid):
            return f'Machine ID {machineid} is not valid'
        elif etime <= stime:
            return 'End time must be after start time'
        elif stime <= datetime.now():
            return 'Start time must be in the future'
        else:
            # not really building out this business logic because I don't need to
            # this is just implemented to help develop the front-end classes
            return True

    def getnextserial(self) -> int:
        cmd = f"""
                SELECT MAX(Serial)
                FROM ResStatus
            """
        cur = self.__conn.cursor()
        result = cur.execute(cmd).fetchone()
        if result is None:
            return -1
        elif result[0] is None:
            # no records in the DB, return 1
            return 1
        else:
            return int(result[0]) + 1

    def editres(self, **kwargsdict) -> bool:
        serialkey = 'ResID'
        stimekey = 'TimeStart'
        etimekey = 'TimeEnd'
        machineidkey = 'MachineID'

        serial = kwargsdict[serialkey]
        if not self.isresactive(serial):
            return False

        stime = None
        etime = None
        machineid = None
        if stimekey in kwargsdict:
            stime = kwargsdict[stimekey]
        if etimekey in kwargsdict:
            etime = kwargsdict[etimekey]
        if machineidkey in kwargsdict:
            machineid = kwargsdict[machineidkey]

        curstime, curetime, curmachineid = self.getcurresinfo(serial)
        if curstime is None or curetime is None or curmachineid is None:
            return False

        # not going to implement calculating a price difference here and applying it
        # if the reservation time or machine IDs changed,
        # but that's something that would be needed in a full implementation
        cmdprefix = 'UPDATE ResMachines'
        cmdsuffix = f' WHERE Serial = {serial}'

        setclause = ''
        if stime is not None:
            setclause = f" SET TimeStart = '{stime.strftime(self.__TFrmt)}'"
        if etime is not None:
            if setclause == '':
                setclause = f" SET TimeEnd = '{etime.strftime(self.__TFrmt)}'"
            else:
                setclause += f", TimeEnd = '{etime.strftime(self.__TFrmt)}'"
        if machineid is not None:
            if setclause == '':
                setclause = f" SET MachineID = {machineid}"
            else:
                setclause += f", MachineID = {machineid}"

        return self.runupdatecommand(cmdprefix + setclause + cmdsuffix)

    def getcurresinfo(self, serial: int) -> (datetime, datetime, int):
        cmd = f'SELECT TimeStart, TimeEnd, MachineID FROM ResMachines WHERE Serial = {serial}'
        cur = self.__conn.cursor()
        cur.execute(cmd)
        result = cur.fetchone()
        if result is None:
            return None, None, None

        try:
            starttime = datetime.strptime(result[0], self.__TFrmt)
            endtime = datetime.strptime(result[1], self.__TFrmt)
        except ValueError:
            return None, None, None
        return starttime, endtime, int(result[2])

    def cancelres(self, resid: int) -> bool:
        userid = self.getuseridforres(resid)
        if userid < 1:
            return False
        if not self.isresactive(resid):
            return False

        refundamount = self.getcancelrefund(resid)
        if refundamount is None:
            return False
        cmdlist = [
            f'UPDATE ResStatus SET IsActive = 0 WHERE Serial = {resid}',
            f'INSERT INTO Transactions (TxType, CustomerID, Amount, Serial) '
            f"VALUES ('Cancel', {userid}, {refundamount}, {resid});"
        ]
        return self.runtransaction(cmdlist)

    def getuseridforres(self, resid: int) -> int:
        cmd = f"SELECT CustomerID FROM Transactions WHERE Serial = '{resid}'"
        cur = self.__conn.cursor()
        cur.execute(cmd)
        result = cur.fetchone()
        if result is None:
            return -1
        return int(result[0])

    def isresactive(self, resid: int) -> bool:
        cmd = f"""
                    SELECT * FROM ResStatus
                    Where Serial = '{resid}' AND IsActive = 1
                """
        cur = self.__conn.cursor()
        cur.execute(cmd)
        return cur.fetchone() is not None

    def getcancelrefund(self, resid: int) -> float:
        cmd = f"SELECT Amount FROM Transactions WHERE Serial = {resid} AND TxType = 'Create'"
        cur = self.__conn.cursor()
        result = cur.execute(cmd).fetchone()
        if result is None:
            return None
        price = float(result[0])

        cmd = f'SELECT TimeStart FROM ResMachines WHERE Serial = {resid}'
        cur = self.__conn.cursor()
        result = cur.execute(cmd).fetchone()
        if result is None:
            return None

        restime = datetime.strptime(result[0], self.__TFrmt)
        daysbeforeres = (datetime.now() - restime).days

        if daysbeforeres >= 7:
            return 0.75 * price
        elif daysbeforeres >= 2:
            return 0.25 * price
        else:
            return 0.00

    def getreservationlist(self, targetunamepattern: str, stime: datetime, etime: datetime, machidlist: list) -> list:
        reservationpatternclause = self.getreservationpatternclause(targetunamepattern, stime, etime, machidlist)
        cmd = f"""
                    SELECT RM.Serial as 'ResID', 
                            RM.TimeStart as 'Time_Start', RM.TimeEnd as 'Time_End', 
                            ResItemInfo.Name as 'MachineType' 
                    FROM ResMachines as RM
                    JOIN ResStatus on ResStatus.Serial = RM.Serial
                    JOIN Transactions on Transactions.Serial = RM.Serial
                    JOIN Users on Users.ID = Transactions.CustomerID
                    JOIN ResItemInfo on ResItemInfo.IType = RM.MachineID {reservationpatternclause}
                """
        cur = self.__conn.cursor()
        try:
            result = cur.execute(cmd).fetchall()
        except sqlite3.OperationalError:
            result = None

        if result is None:
            return None
        else:
            retlist = []
            machinekey = 'Machine'
            names = list(map(lambda x: x[0], cur.description))
            for record in result:
                recorddict = {machinekey: {}}
                for name, value in zip(names, record):
                    if name == 'ResID':
                        recorddict[name] = value
                    else:
                        recorddict[machinekey][name] = value
                retlist.append(recorddict)
            return retlist

    def getreservationpatternclause(self, targetunamepattern: str,
                                    stime: datetime, etime: datetime, machidlist: list) -> str:
        patternclause = ''
        if targetunamepattern != '':
            patternclause = f"Username LIKE '{targetunamepattern}'"
        if stime is not None and etime is not None:
            timeclause = f"TimeStart between '{stime.strftime(self.__TFrmt)}' and '{etime.strftime(self.__TFrmt)}'"
            if patternclause == '':
                patternclause = timeclause
            else:
                patternclause += f' AND {timeclause}'
        if len(machidlist) > 0:
            machclause = f"MachineID in ({', '.join(machidlist)})"
            if patternclause == '':
                patternclause = machclause
            else:
                patternclause += f' AND {machclause}'

        if patternclause != '':
            return f' WHERE {patternclause}'
        else:
            return ''

    def getresprice(self, machineid: int, starttime: datetime, endtime: datetime) -> float:

        cmd = f"""
                    SELECT Price, Duration_Hrs
                    FROM ResItemInfo
                    WHERE IType = {machineid}
                """
        cur = self.__conn.cursor()
        result = cur.execute(cmd).fetchone()
        price = float(result[0])
        priceduration = float(result[1])
        # want to round this up so the next half hour block
        # but prices are quoted in hour blocks, so that needs to be multiplied by 2
        timediff_hours = ceil((endtime - starttime).seconds/1800) / 2
        baseprice = timediff_hours * price / priceduration
        if (starttime - datetime.now()).days >= 14:
            # apply 25% discount
            return baseprice * 0.75
        else:
            return baseprice

    def addfunds(self, uname, addamount):
        if not self.userexists(uname):
            return False
        else:
            userid = self.getuserid(uname)
            cmd = f"""
                        INSERT INTO TRANSACTIONS
                        (TxType, CustomerID, AMOUNT, Serial)
                        VALUES 
                        ('AddFunds', '{userid}', -{round(addamount, 2)}, NULL)
                    """
            return self.runupdatecommand(cmd)

    def getbalance(self, uname: str) -> float:
        if not self.userexists(uname):
            return False
        else:
            userid = self.getuserid(uname)
            cmd = f"""
                        SELECT -Sum(AMOUNT)
                        FROM TRANSACTIONS
                        WHERE CustomerID = {userid}
                    """
            cur = self.__conn.cursor()
            result = cur.execute(cmd).fetchone()
            if result is None:
                # no balance
                return 0.00
            elif result[0] is None:
                return 0.00
            else:
                return float(result[0])

    def getclientlist(self):
        cmd = f"""
                    SELECT Username FROM Users
                    WHERE IsFacilityManager = '0'
                """
        cur = self.__conn.cursor()
        cur.execute(cmd)
        result = cur.fetchall()
        if result is None:
            return []
        else:
            retlist = []
            names = list(map(lambda x: x[0], cur.description))
            for record in result:
                recorddict = {}
                for name, value in zip(names, record):
                    recorddict[name] = value
                retlist.append(recorddict)
            return retlist

    def getmatchingclientlist(self, unamepattern: str, uidpattern: str) -> list:
        patternclause = self.getmatchingclientpatternclause(unamepattern, uidpattern)

        cmd = f"""
                    SELECT Username FROM Users
                    WHERE {patternclause}
                """
        cur = self.__conn.cursor()
        cur.execute(cmd)
        result = cur.fetchall()
        if result is None:
            return []
        else:
            retlist = []
            names = list(map(lambda x: x[0], cur.description))
            for record in result:
                recorddict = {}
                for name, value in zip(names, record):
                    recorddict[name] = value
                retlist.append(recorddict)
            return retlist

    @staticmethod
    def getmatchingclientpatternclause(unamepattern: str, uidpattern: str) -> str:
        patternclause = ''
        if unamepattern != '':
            patternclause = f"Username LIKE '{unamepattern}'"
        if uidpattern != '':
            if patternclause == '':
                patternclause = f"ID LIKE '{uidpattern}'"
            else:
                patternclause += f" AND ID LIKE '{uidpattern}'"
        return patternclause

    def getmachinelist(self):
        cmd = f"""
                    SELECT * FROM ResItemInfo
                """
        cur = self.__conn.cursor()
        cur.execute(cmd)
        result = cur.fetchall()
        if result is None:
            return None
        else:
            retlist = []
            names = list(map(lambda x: x[0], cur.description))
            for record in result:
                recorddict = {}
                for name, value in zip(names, record):
                    recorddict[name] = value
                retlist.append(recorddict)
            return retlist


def gtstmps(stime, etime):
    # get time stamp set
    rets = set()

    i_count = int((etime - stime).seconds / (30 * 60))
    for i in range(i_count + 1):
        ioffm = 30 * i
        ctime = (stime + timedelta(minutes=ioffm)).strftime('%Y%m%D %H:%M:%S')
        if ctime not in rets:
            rets.add(ctime)
    return rets
