"""
    Represents individual reservations for machines at a facility
    This is a very simple class that's just used to provide
    object-oriented behavior to things like the User's reservation list
"""

from datetime import datetime
global timeformat
timeformat = '%Y-%m-%d %H:%M'


class Reservation:
    def __init__(self):
        self.resid = -1
        self.machres = None
        return

    def __repr__(self):
        return f'Reservation object, ResID={self.resid}, MachineRes={self.machres}'

    def initfromvals(self, resid: int,
                     starttime: datetime, endtime: datetime, machineid: int) -> None:
        """
        :param resid: int, the id of this specific reservation
        :param resid: int, the unique ID number for this specific reservation
            Any negative ID here will be assumed to be invalid
            or a reservation that has been set up but not submitted to the system
        :param starttime: datetime, the time that the reservation starts
            It is assumed that this is in LOCAL TIME
        :param endtime: the time that the reservation ends
            It is assumed that this is in LOCAL TIME
        :param machineid: the ID of the machine
        :return:
        """
        self.resid = resid
        resmachine = MachineRes()
        resmachine.initfromvalues(starttime, endtime, machineid)
        self.machres = resmachine
        return

    def initfromjson(self, jsonstr: str) -> None:
        residkey = 'id'

        if residkey in jsonstr:
            self.resid = jsonstr[residkey]
        resmachine = MachineRes()
        resmachine.initfromjson(jsonstr)
        self.machres = resmachine
        return


class MachineRes:
    def __init__(self):
        self.starttime = None
        self.endtime = None
        self.machinetype = ''
        return

    def __repr__(self):
        return f'MachineRes object, starttime={self.starttime}, endtime={self.endtime}, machinetype={self.machinetype}'

    def initfromvalues(self, starttime: datetime, endtime: datetime, machinetype: str) -> None:
        self.starttime = starttime
        self.endtime = endtime
        self.machinetype = machinetype
        return

    def initfromjson(self, jsonstr: str) -> None:
        machinetypekey = 'machine_type'
        timestartkey = 'start_datetime'
        timeendkey = 'end_datetime'
        starttime = self.starttime
        endtime = self.endtime
        machinetype = self.machinetype

        if machinetypekey in jsonstr:
            machinetype = jsonstr[machinetypekey]
        if timestartkey in jsonstr:
            try:
                starttime = datetime.strptime(jsonstr[timestartkey], timeformat)
            except ValueError:
                pass
        if timeendkey in jsonstr:
            try:
                endtime = datetime.strptime(jsonstr[timeendkey], timeformat)
            except ValueError:
                pass

        self.initfromvalues(starttime, endtime, machinetype)
        pass
