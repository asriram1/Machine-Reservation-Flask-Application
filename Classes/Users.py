from .Reservation import Reservation
from .Transaction import Transaction
# used for time conversions
from datetime import datetime
# Used to simplify underlying HTTP requests
import requests

global timeformat
timeformat = '%Y%m%d %H:%M:%S'

APIBaseURL = 'http://localhost:5000'
endpointdict = {
        'login': f'{APIBaseURL}/api/login',
        'register': f'{APIBaseURL}/api/register',
        'getprofile': f'{APIBaseURL}/api/profile',
        'changeusername': f'{APIBaseURL}/api/profile',
        'setstatus': f'{APIBaseURL}/api/status',
        'setfm': f'{APIBaseURL}/api/setfm',
        'getreslist': f'{APIBaseURL}/api/reservations/list',
        'editres': f'{APIBaseURL}/api/reservations/edit',
        'makeres': f'{APIBaseURL}/api/reservations/create',
        'cancelres': f'{APIBaseURL}/api/reservations/cancel',
        'calculatecost': f'{APIBaseURL}/api/reservations/cost',
        'gettranslist': f'{APIBaseURL}/api/transactions/list',
        'getbalance': f'{APIBaseURL}/api/balance/view',
        'addfunds': f'{APIBaseURL}/api/addfunds',
        'getclientlist': f'{APIBaseURL}/api/clients',
        'searchclients': f'{APIBaseURL}/api/clients/search',
        'searchreservations': f'{APIBaseURL}/api/reservations/list',
        'getmachinelist': f'{APIBaseURL}/api/machines/machinelist'
    }


def getreslistfromjson(jsondict: dict) -> list:
    """
    :param jsondict: a JSON dictionary containing reservation information
    :return: a list of Reservation objects corresponding to the information
        contained in resp
    """
    retlist = []
    for rawres in jsondict:
        res = Reservation()
        res.initfromjson(rawres)
        if res is not None:
            retlist.append(res)
    return retlist


class User:
    def __init__(self):
        self.username = ''
        self.userid = 0
        self.password = ''
        self.balance = 0
        self.isactive = True
        self.token = ''
        self.IsFacilityManager = False
        return

    def __repr__(self):
        return f'username={self.username}, userid={self.userid}'

    @classmethod
    def register(cls, username: str, password: str, isfm: bool, isactive: bool) -> bool:
        """
        :param username: string, a username that the user would like to register
        :param password: string, a password that the user would like to use
        :param isfm: boolean, indicates whether the new user should be a facility manager (True)
                or if they're just a standard client (False)
        :param isactive: boolean, indicates whether the new user should be registered as active (True)
                or inactive (False)
        :return: a boolean indicating whether a user was able to be registered successfully
        """
        try:
            # this is the one that can access the endpoint dictionary directly
            # because this endpoint should never need a token
            if isfm:
                typestr = 'FM'
            else:
                typestr = 'Client'
            resp = requests.post(endpointdict['register'],
                                 json={'Username': username, 'Password': password,
                                       'Type': typestr, 'IsActive': isactive})

        except KeyError:
            # register endpoint isn't defined in the endpoint dictionary
            return False
        except requests.exceptions.ConnectionError:
            # API is down
            return False
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return False
        # 200 is the only valid response here,
        # all others indicate that the user could not be registered
        return resp.status_code == 200

    @classmethod
    def login(cls, username: str, password: str):
        """
        :param username: string, a username associated with a specific user
        :param password: string, a password associated with a specific user
        :return: a User object representing a registered user in the system if the login credentials are valid
            If the credentials are not valid, this should return Nothing
        """
        try:
            resp = requests.post(endpointdict['login'], json={'Username': username, 'Password': password})
        except KeyError:
            # login endpoint isn't defined in the endpoint dictionary
            return None
        except requests.exceptions.ConnectionError:
            # API is down
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None

        # 200 is the only valid response here,
        # all others indicate that the login failed
        if resp.status_code != 200:
            return None
        else:
            token = cls.gettokenfromresponse(resp)
            isfm = cls.getfmpermissionsfromresponse(resp)
            if isfm:
                retuser = FacilityManager()
                retuser.username = username
                retuser.password = password
                retuser.token = token
            else:
                retuser = Client()
                retuser.username = username
                retuser.password = password
                retuser.token = token
            return retuser

    def getendpointurl(self, basename: str) -> str:
        if basename not in endpointdict:
            return ''
        elif self.token == '':
            return endpointdict[basename]
        else:
            return f"{endpointdict[basename]}?Token={self.token}"

    @staticmethod
    def gettokenfromresponse(resp) -> str:
        tokenkey = 'Token'
        if resp.json() is None or tokenkey not in resp.json():
            return ''
        else:
            return resp.json()[tokenkey]

    @staticmethod
    def getfmpermissionsfromresponse(resp) -> bool:
        isfmkey = 'Type'
        if resp.json() is None:
            return False
        elif isfmkey not in resp.json() or resp.json()[isfmkey].upper() not in ('Client', 'FM'):
            # unexpected response format, assume current user is not a facility manager
            # (safer, more access controls)
            return False
        # in Python, direct boolean conversions should never be used
        # because only empty strings evaluate to False and all others evaluate to True
        else:
            return resp.json()[isfmkey].upper() == 'FM'

    def logout(self) -> bool:
        """
        :return: boolean, whether logout was successful or not
            This also modifies the class' internal state
            so it is unauthorized to access the API
        """
        # This doesn't have to hit the API because it's just removing the token
        self.token = ''
        return True

    def getprofile(self, username: str = '') -> dict:
        """
        :return: dictionary indicating user profile information
            Keys are defined in the API spec
        """
        if username != '':
            targetuser = username
        else:
            targetuser = self.username
        try:
            resp = requests.get(self.getendpointurl('getprofile'),
                                json={'Username': self.username, 'TargetUsername': targetuser})
        except KeyError:
            # profile endpoint is not defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None
        # 200 is the only valid response here,
        # all others indicate that the username change failed

        if resp.status_code != 200:
            return None
        else:
            return resp.json()

    def changeusername(self, changeusername: str = '', newusername: str = '') -> bool:
        """
        :newusername: string, the username that the current user would like to use
        :return: boolean indicating whether the username change was successful
        """
        if newusername == '':
            return False
        if changeusername == '':
            changeusername = self.username
        try:
            resp = requests.post(self.getendpointurl('changeusername'),
                                 json={'Username': self.username,
                                       'TargetUsername': changeusername,
                                       'NewUsername': newusername})
        except KeyError:
            # logout endpoint is not defined in the endpoint dictionary
            return False
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return False
        # 200 is the only valid response here,
        # all others indicate that the username change failed

        if resp.status_code != 200:
            return False
        else:
            if changeusername == self.username:
                self.username = newusername
            return True

    def getreslist(self, username: str = '',
                   starttimestr: str = '', endtimestr: str = '', machidlist: list = []):
        try:
            jsondict = {'Username': self.username}
            if username != '':
                jsondict['TargetUsername'] = username
            if starttimestr != '' and endtimestr != '':
                jsondict['Time_Start'] = starttimestr
                jsondict['Time_End'] = endtimestr
            if len(machidlist) > 0:
                jsondict['MachineIDList'] = machidlist
            resp = requests.get(self.getendpointurl('getreslist'),
                                json=jsondict)
        except KeyError:
            # getreslist endpoint is not defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None

        # 200 is the only valid response here,
        # all others indicate that something was wrong with the input or the API
        if resp.status_code != 200:
            return None
        else:
            reslistkey = 'ResList'
            respjson = resp.json()
            if reslistkey not in respjson:
                return []
            else:
                return getreslistfromjson(respjson[reslistkey])

    def getres(self, resid: int) -> Reservation:
        reslist = self.getreslist(self.username)
        if reslist is None:
            return None
        for res in reslist:
            if res.resid == resid:
                return res
        # no matching reservation found,
        # return None
        return None

    def makeres(self, username: str, starttime: str, endtime: str, machinestr: str) -> bool:
        """
        :param username: the name of the user that the reservation should be created for
                This could be either a client or a facility manager
        :param starttime: a string representing the start time for included reservations
                This should be in LOCAL TIME with a format of 'yyyymmdd hh:mm:ss'
        :param endtime: a string representing the end time for included reservations
                This should be in LOCAL TIME  with a format of 'yyyymmdd hh:mm:ss'
        :param machinestr: a string representing the name of the machine that the reservation is for
                This should absolutely be using a numerical ID
        :return: a boolean representing whether the reservation was created successfully or not
        """
        try:
            machdict = {'MachineType': machinestr, 'Time_Start': starttime, 'Time_End': endtime}
            resdict = {'Machine': machdict}
            resp = requests.post(self.getendpointurl('makeres'),
                                 json={'Username': self.username,
                                       'TargetUsername': username,
                                       'Res': resdict})
        except KeyError:
            # endpoint is not defined in the endpoint dictionary
            return 'Endpoint not defined'
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return 'Invalid URL'

        if resp.status_code == 200:
            return True
        else:
            errkey = 'error'
            if errkey in resp.json():
                return resp.json()[errkey]
            else:
                return 'Unspecified error'

    def editres(self, resid: int, newstarttime: datetime = None, newendtime: datetime = None, newmachineid: int = None) -> Reservation:
        """
        :param resid: the ID of a reservation that should be edited
        :param newstarttime: a datetime representing the new start time for a reservation
            This could match the reservation's original start time or could be changed
        :param newendtime: a datetime representing the new end time for a reservation
            This could match the reservation's original end time or could be changed
        :param newmachineid: a datetime representing the new machine id for a reservation
            This could match the original machine id or it could be changed
        :return: a Reservation object representing the reservation after it has been edited
            If the edit couldn't be completed successfully, this will return None
        """
        try:
            jsondict = {'Username': self.username, 'ResID': resid}
            if newstarttime is not None:
                jsondict['Time_Start'] = newstarttime
            if newendtime is not None:
                jsondict['Time_End'] = newendtime
            if newmachineid is not None:
                jsondict['MachineID'] = newmachineid
            resp = requests.post(self.getendpointurl('editres'), json=jsondict)
        except KeyError:
            # endpoint is not defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None

        if resp.status_code != 200:
            return None
        else:
            reskey = 'Res'
            retres = Reservation()
            if reskey in resp.json():
                retres.initfromjson(resp.json()[reskey])
            if retres.resid < 0:
                return None
            else:
                return retres

    def cancelres(self, resid: int) -> float:
        """
        :param resid: the ID of a reservation that should be cancelled
        :return: a float value indicating the refund returned for a successfully cancelled reservation
        """
        try:
            resp = requests.post(self.getendpointurl('cancelres'), json={'ResID': resid})
        except KeyError:
            # endpoint is not defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None

        if resp.status_code != 200:
            return None
        else:
            refundkey = 'Refund'
            if refundkey not in resp.json():
                return None
            try:
                refund = float(resp.json()[refundkey])
                return refund
            except ValueError:
                return None

    def calculatecost(self, starttime: datetime, endtime: datetime, machineid: int) -> float:
        """
        :param starttime: a datetime.datetime object representing the start time for included reservations
                This should be in LOCAL TIME
        :param endtime: a datetime.datetime object representing the end time for included reservations
                This should be in LOCAL TIME
        :param machineid: integer, representing the machine that the reservation is for
        :return: a float representing the cost for the specified reservation
            If something went wrong with the request or API, this will return None
        """
        try:
            resp = requests.post(self.getendpointurl('calculatecost'),
                                 json={'Time_Start': datetime.strftime(starttime, timeformat),
                                       'Time_End': datetime.strftime(endtime, timeformat),
                                       'MachineTypeList': [machineid]})
        except ValueError:
                # date values were in the wrong format
            return None
        except KeyError:
            # endpoint is not defined in the endpoint dictionary
            return None

        if resp.status_code != 200:
            return None
        else:
            pricekey = 'Price'
            if pricekey not in resp.json():
                return None
            try:
                price = float(resp.json()[pricekey])
                return price
            except ValueError:
                return None

    def gettranslist(self, username: str = '', starttime: datetime = None, endtime: datetime = None) -> list:
        """
        :param username: the name of the user that the transactions should be for
                This could be different than the current user
        :param starttime: a datetime.datetime object representing the start time for included reservations
                This should be in LOCAL TIME
        :param endtime: a datetime.datetime object representing the end time for included reservations
                This should be in LOCAL TIME
        :return: a list of Transaction.Transaction objects representing the current user's transactions
            within the times specified (inclusive)
        """
        jsondict = {'Username': self.username}
        if username != '':
            jsondict['TargetUsername'] = username

        if starttime is not None and endtime is not None:
            try:
                    # splitting this out so both are parsed before either is added
                    # this makes sure that an invalid format in one of them will not cause only one to be sent
                stime = datetime.strftime(starttime, timeformat)
                etime = datetime.strftime(endtime, timeformat)
                jsondict['Time_Start'] = stime
                jsondict['Time_End'] = etime
            except TypeError:
                    # don't have to do anything here,
                    # just don't add those keys to the request JSON
                pass
        try:
            resp = requests.get(self.getendpointurl('gettranslist'), json=jsondict)
        except KeyError:
            # endpoint is not defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None

        if resp.status_code != 200:
            return None
        else:
            return self.gettranslistfromresponse(resp)

    @staticmethod
    def gettranslistfromresponse(resp: requests.request) -> list:
        translistkey = 'TransactionList'
        retlist = []
        respjson = resp.json()
        if respjson is not None and translistkey in respjson:
            rawtranslist = respjson[translistkey]
            for rawtrans in rawtranslist:
                trans = Transaction()
                trans.initfromjson(rawtrans)
                if trans is not None:
                    retlist.append(trans)
        return retlist

    def getbalance(self, targetusername: str) -> float:
        """
        :param targetusername - the name of the user whose balance should be checked
        :return: the user's balance
            If something goes wrong with the request or API, this should return None
        """
        try:
            resp = requests.get(self.getendpointurl('getbalance'),
                                json={'Username': self.username, 'TargetUsername': targetusername})
        except KeyError:
            # endpoint is not defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None
        balkey = 'Balance'
        if resp.status_code != 200:
            return None
        elif resp.json() is None or balkey not in resp.json():
            return None
        else:
            try:
                bal = float(resp.json()[balkey])
                return bal
            except ValueError:
                return None

    def addfunds(self, adduser: str, addamount: float) -> float:
        """
        :param adduser - the username of the user that funds are being added for
        :param addamount: the balance to add to the current user's existing balance
        :return: the new balance after adding addamount
        """
        try:
            resp = requests.post(self.getendpointurl('addfunds'),
                                 json={'Username': self.username, 'TargetUsername': adduser, 'Amount': addamount})
        except KeyError:
            # endpoint is not defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None

        if resp.status_code != 200:
            return None
        else:
            balkey = 'Balance'
            if resp.json() is None or balkey not in resp.json():
                return None
            else:
                try:
                    balance = resp.json()[balkey]
                    return balance
                except ValueError:
                    return None

    def getmachinelist(self):
        """
        :return: a list of machine information for machines that users can reserve
        """
        # so this was initially getting machine information from an API endpoint
        # to make machine information guaranteed to be consistent throughout the system
        # That endpoint doesn't exist, so defining this manually
        nk = 'Name'
        ik = 'IType'
        pk = 'Price'
        dk = 'Duration_Hrs'
        return [
                    {nk: 'Workshop', ik: 1, pk: 99, dk: 1},
                    {nk: 'Microvac', ik: 2, pk: 2000, dk: 1},
                    {nk: 'Irradiator', ik: 3, pk: 2200, dk: 1},
                    {nk: 'Extruder', ik: 4, pk: 500, dk: 1},
                    {nk: 'Crusher', ik: 5, pk: 10000, dk: .5},
                    {nk: 'Harvester', ik: 6, pk: 8800, dk: 1}
                ]


class Client(User):
    def __init__(self):
        super().__init__()
        self.IsFacilityManager = False
        return

    def __repr__(self):
        return f'Client: {super().__repr__()}'

    def getprofile(self) -> dict:
        return super().getprofile(self.username)

    def changeusername(self, newusername: str) -> bool:
        return super().changeusername(self.username, newusername)

    def getreslist(self) -> list:
        return super().getreslist(self.username, '', '', [])

    def makeres(self, starttime: str, endtime: str, machinestr: str) -> bool:
        """
        :param starttime: a string representing the start time for included reservations
                This should be in LOCAL TIME with a format of 'yyyymmdd hh:mm:ss'
        :param endtime: a string representing the end time for included reservations
                This should be in LOCAL TIME  with a format of 'yyyymmdd hh:mm:ss'
        :param machinestr: a string representing the name of the machine that the reservation is for
                This should absolutely be using a numerical ID
        :return: a boolean indicating if the reservation was created successfully
        """
        return super().makeres(self.username, starttime, endtime, machinestr)

    def gettranslist(self, starttime: datetime = None, endtime: datetime = None) -> list:
        """
        :param starttime: a datetime.datetime object representing the start time for included reservations
                This should be in LOCAL TIME
        :param endtime: a datetime.datetime object representing the end time for included reservations
                This should be in LOCAL TIME
        :return: a list of Transaction.Transaction objects representing the current user's transactions
            within the times specified (inclusive)
        """
        return super().gettranslist(self.username, starttime, endtime)

    def addfunds(self, addamount: float) -> float:
        """
        :param addamount: the balance to add to the current user's existing balance
        :return: the new balance after adding addamount
        """
        return super().addfunds(self.username, addamount)

    def getbalance(self):
        """
        :return: the current user's balance
        """
        return super().getbalance(self.username)


class FacilityManager(User):
    def __init__(self):
        super().__init__()
        self.IsFacilityManager = True
        return

    def __repr__(self):
        return f'FacilityManager: {super().__repr__()}'

    def setfm(self, clientid: int, newval: bool) -> bool:
        try:
            resp = requests.post(self.getendpointurl('setfm'),
                                 json={'Username': self.username,
                                       'TargetUserID': clientid,
                                       'IsFacilityManager': newval})
        except KeyError:
            # login endpoint isn't defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None

        # 200 is the only valid response here,
        # all others indicate that the login failed
        return resp.status_code == 200

    def getprofile(self, username: str = '') -> dict:
        return super().getprofile(username)

    def changeusername(self, changeusername: str = '', newusername: str = '') -> bool:
        return super().changeusername(changeusername, newusername)

    def makeres(self, username: str, starttime: str, endtime: str, machinestr: str) -> bool:
        """
        :param username: the name of the user that the reservation should be created for
                This could be either a client or a facility manager
        :param starttime: a string representing the start time for included reservations
                This should be in LOCAL TIME with a format of 'yyyymmdd hh:mm:ss'
        :param endtime: a string representing the end time for included reservations
                This should be in LOCAL TIME  with a format of 'yyyymmdd hh:mm:ss'
        :param machinestr: a string representing the name of the machine that the reservation is for
                This should absolutely be using a numerical ID
        :return: a boolean indicating whether the reservation was created successfully or not
        """
        return super().makeres(username, starttime, endtime, machinestr)

    def getclientlist(self):
        try:
            resp = requests.get(self.getendpointurl('getclientlist'), json={'Username': self.username})
        except KeyError:
            # login endpoint isn't defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None

        # 200 is the only valid response here,
        # all others indicate that the client list could not be obtained
        clistkey = 'ClientList'
        if resp.status_code != 200 or resp.json() is None or clistkey not in resp.json():
            return None
        else:
            retlist = []
            clist = resp.json()[clistkey]
            for uname in clist:
                retlist.append(uname)
            return retlist

    def getreslist(self, username: str = '', starttimestr: str = '', endtimestr: str = '',
                   machidlist: list = []) -> list:
        return super().getreslist(username, starttimestr, endtimestr, machidlist)

    def searchreservations(self, targetusernamepattern: str = '',
                           starttime: datetime = None, endtime: datetime = None, machineidlist: list = []) -> list:

        try:
            jsondict = {'Username': self.username}
            if targetusernamepattern != '':
                jsondict['TargetUsername'] = targetusernamepattern
            if starttime is not None and endtime is not None:
                jsondict['Time_Start'] = starttime.strftime(timeformat)
                jsondict['Time_End'] = endtime.strftime(timeformat)
            if len(machineidlist) > 0:
                jsondict['MachineIDList'] = f"({', '.join(machineidlist)})"
            resp = requests.get(self.getendpointurl('searchreservations'),
                                json=jsondict)
        except KeyError:
            # login endpoint isn't defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None

        # 200 is the only valid response here,
        # all others indicate that the client list could not be obtained
        rlistkey = 'ResList'
        if resp.status_code != 200 or resp.json() is None or rlistkey not in resp.json():
            return None
        else:
            return getreslistfromjson(resp.json()[rlistkey])

    def createclient(self, username: str, password: str, isfm: bool, isactive: bool):
        return super().register(username, password, isfm, isactive)

    def activateclient(self, username: str) -> bool:
        try:
            resp = requests.post(self.getendpointurl('setstatus'),
                                 json={'Username': self.username, 'TargetUsername': username, 'IsActive': True})
        except KeyError:
            # login endpoint isn't defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None
        # 200 is the only valid response here,
        # all others indicate that the login failed
        return resp.status_code == 200

    def deactivateclient(self, username: str) -> bool:
        try:
            resp = requests.post(self.getendpointurl('setstatus'),
                                 json={'Username': self.username, 'TargetUsername': username, 'IsActive': False})
        except KeyError:
            # login endpoint isn't defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None
        # 200 is the only valid response here,
        # all others indicate that the login failed
        return resp.status_code == 200

    def searchclients(self, usernamepattern: str = '', useridpattern: str = '') -> list:
        try:
            resp = requests.get(self.getendpointurl('searchclients'),
                                json={'Username': self.username,
                                      'PartialUsername': usernamepattern, 'UserIDPattern': useridpattern})
        except KeyError:
            # login endpoint isn't defined in the endpoint dictionary
            return None
        except requests.exceptions.InvalidURL:
            # URL is invalid in the endpoint dictionary
            return None

        # 200 is the only valid response here,
        # all others indicate that the client list could not be obtained
        if resp.status_code != 200 or resp.json() is None:
            return None
        else:
            retlist = []
            unamekey = 'username'
            for elem in resp.json():
                if unamekey in elem:
                    retlist.append(elem[unamekey])
            return retlist

    def getbalance(self, targetusername: str):
        return super().getbalance(targetusername)

    def addfunds(self, addusername: str, addamount: float) -> float:
        return super().addfunds(addusername, addamount)

    def gettranslist(self, username: str = '', starttime: datetime = None, endtime: datetime = None) -> list:
        """
        :param username: the username that the transactions should be for
        :param starttime: a datetime.datetime object representing the start time for included reservations
                This should be in LOCAL TIME
        :param endtime: a datetime.datetime object representing the end time for included reservations
                This should be in LOCAL TIME
        :return: a list of Transaction.Transaction objects representing the current user's transactions
            within the times specified (inclusive)
        """
        return super().gettranslist(username, starttime, endtime)
