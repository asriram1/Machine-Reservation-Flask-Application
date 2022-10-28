from Classes.Users import User, Client, FacilityManager
from Classes.Reservation import Reservation
from Classes.Transaction import Transaction
from functools import partial
from datetime import datetime
# seconds are needed for the API because of the specification
timeformatapiformat = '%Y-%m-%d %H:%M:%S'
# don't need seconds for input because including the number of seconds in the start time is a waste of time
timeformatinptformat = '%Y-%m-%d %H:%M'
# keeping this to display the required format to users
timeformatinptstr = 'yyyy-mm-dd hh:mm'

# yeah, this should be defined as part of one long list of tuples or something similar
quitinpt = '-quit'
hlpDict = {
    # 0-9 are reserved for things that can be done while logged out
    0: 'Login to an existing account',
    1: 'Register a new account',
    # 10-99 are reserved for things that can always be done while logged in
    10: 'Logout',
    # 101-199 are reserved for things that can be done by clients
    101: 'Book a reservation',
    102: 'Cancel a reservation',
    103: 'Modify a reservation',
    104: 'List your reservations',
    105: 'Add funds to your account',
    106: 'List your transactions',
    107: 'Edit your profile',
    108: 'Show your account balance',
    # 201-299 are reserved for things that can be done by facility managers
    201: 'Book a reservation for an existing client',
    202: 'Cancel a reservation for an existing client',
    203: 'Modify a reservation for an existing client',
    204: 'List reservations for an existing client',
    205: 'Find a specific reservation',
    206: 'Create a new client',
    207: 'Edit an existing client',
    208: 'Find a specific client',
    209: 'Deactivate a client',
    210: 'Activate a deactivated client',
    211: 'Add funds to an existing client',
    212: 'List all clients',
    213: 'List all transactions',
    214: 'List all transactions for an existing client',
    # 900-999 are reserved for things that can be done at any time
    998: 'Display all available commands',
    999: 'Exit the program'
}
loggedoutacts = {'-login': 0, '-register': 1, '-help': 998, quitinpt: 999}
loggedinclientacts = {'-makeres': 101, '-cancelres': 102, '-modifyres': 103, '-listres': 104, '-addfunds': 105,
                      '-listtrans': 106, '-editprofile': 107, '-balance': 108,
                      '-logout': 10, '-help': 998, quitinpt: 999}
loggedinfmacts = {'-makeres': 201, '-cancelres': 202, '-modifyres': 203, '-listres': 204, '-findres': 205,
                  '-createclient': 206, '-editclient': 207, '-findclient': 208,
                  '-deactivateclient': 209, '-activateclient': 210, '-addfunds': 211,
                  '-listclients': 212, '-listtrans': 213, '-listclienttrans': 214,
                  '-logout': 10, '-help': 998, quitinpt: 999}
global usr
usr = None
global quitbool
quitbool = False


def main():
    global quitbool
    global usr

    while not quitbool:
        if usr is None:
            runloggedoutevents()
        elif not usr.IsFacilityManager:
            runclientevents()
        else:
            runfacilitymanagerevents()

    if usr is not None:
        logoutsuccess = usr.logout()
        if logoutsuccess:
            print(f'Logout successful')
    print('Goodbye!')
    return


def runloggedoutevents():
    u_inpt = input("Please enter an action you would like to perform.\n"
                   "Enter '-help' for a list of valid commands.\n")
    action = getact(u_inpt, 1)

    if action == loggedoutacts[quitinpt]:
        global quitbool
        quitbool = True
        return

    # doing this for some visual separation between commands
    print('-' * 40)
    switcher = {
        0: login,
        1: register,
        998: partial(showhelp, loggedoutacts),
        -1: lambda: print(f"Invalid input '{u_inpt}'\nEnter '-help' to see a list of valid commands.\n"),
    }
    switcher.get(action)()
    print('-' * 40)
    return


def getact(u_inpt, inpttype: int):
    if inpttype == 1:
            # logged out actions
        if u_inpt in loggedoutacts:
            return loggedoutacts[u_inpt]
        else:
            return -1
    elif inpttype == 2:
            # logged in client actions
        if u_inpt in loggedinclientacts:
            return loggedinclientacts[u_inpt]
        else:
            return -1
    elif inpttype == 3:
            # logged in facility manager actions
        if u_inpt in loggedinfmacts:
            return loggedinfmacts[u_inpt]
        else:
            return -1
    else:
        # unexpected inpttype value, return invalid
        return -1


def showhelp(actsdict):
    # show help information

    for txt, ID in actsdict.items():
        if ID in hlpDict:
            print(f'{txt:<20}:\t{hlpDict[ID]:<30}')
    return


def login():
    username = input('Please enter your username: ')
    pw = input('Please enter your password: ')
    global usr
    usr = User.login(username, pw)
    if usr is None:
        print('Invalid username or password')
    else:
        print('Login successful')
    return


def logout():
    global usr
    if usr is not None:
        logoutsuccess = usr.logout()
    else:
        logoutsuccess = False
    if logoutsuccess:
        print('Logout successful')
        # it would be nice if logout modified usr directly,
        # but not going to push that right now
        usr = None
    else:
        print('Unable to logout')
    return


def register():
    username = input('Please enter a new username: ')
    pw = input('Please enter a password: ')
    rawisfm = input('Enter 1 if the user should be a facility manager or 0 if they should be a client: ')
    isfm = (rawisfm == '1')

    registersuccess = User.register(username, pw, isfm, True)
    if not registersuccess:
        print('Unable to register the specified user')
    else:
        print('User registered successfully, attempting to login...')
        global usr
        usr = User.login(username, pw)
        if usr is None:
            print('Automatic login failed')
        else:
            print('Login successful')
    return


def runclientevents():
    u_inpt = input("Please enter an action you would like to perform.\n"
                   "Enter '-help' for a list of valid commands.\n")
    action = getact(u_inpt, 2)

    if action == loggedoutacts[quitinpt]:
        global quitbool
        quitbool = True
        return

    # doing this for some visual separation between commands
    print('-' * 40)
    switcher = {
        101: makeres,
        102: cancelres,
        103: modifyres,
        104: listres,
        105: addfunds,
        106: listtrans,
        107: editprofile,
        108: balance,
        10: logout,
        998: partial(showhelp, loggedinclientacts),
        -1: lambda: print(f"Invalid input '{u_inpt}.'\nEnter '-help' to see a list of valid commands.\n"),
    }
    switcher.get(action)()
    print('-' * 40)
    return


def makeres():
    quitmsg = 'No reservation was created'
    global usr
    print(f'Please enter information about the new reservation below\n'
          f"If you would like to stop creating a reservation, enter '{quitinpt}'")
    machineinpt = getmachineinpt(allowmultiple=False)
    if machineinpt == quitinpt:
        print(quitmsg)
        return

    starttimeinpt = gettimeinput(starttime=True)
    if starttimeinpt == quitinpt:
        print(quitmsg)
        return
    else:
        try:
            stimestr = datetime.strptime(starttimeinpt, timeformatinptformat).strftime(timeformatapiformat)
        except ValueError:
            print(f'The time entered was not in the correct format.\n{quitmsg}')
            return

    endtimeinpt = gettimeinput(starttime=False)
    if endtimeinpt == quitinpt:
        print(quitmsg)
        return
    else:
        try:
            etimestr = datetime.strptime(endtimeinpt, timeformatinptformat).strftime(timeformatapiformat)
        except ValueError:
            print(f'The time entered was not in the correct format.\n{quitmsg}')
            return
    mkresresult = usr.makeres(stimestr, etimestr, machineinpt)
    if type(mkresresult) is bool:
        if mkresresult:
            print('Reservation created successfully')
        else:
            print('Reservation could not be created')
    else:
        print(f'Reservation could not be created: {mkresresult}')
    return


def gettimeinput(starttime: bool) -> str:
    if starttime:
        timetypestr = 'a start'
    else:
        timetypestr = 'an end'
    return input(f"Please enter {timetypestr} time for this reservation in the format '{timeformatinptstr}': ")


def getmachineinpt(allowmultiple: bool) -> str:
    machinelist = usr.getmachinelist()
    if machinelist is not None:
        idtonamedict = {}
        if len(machinelist) > 0:
            print(f'{"ID":<3}\t{"Name":<15}\t{"Price":<8}\t{"Duration (Hrs)":<5}')
            for mchdict in machinelist:
                idval, name, price, duration = getmchinfofromdict(mchdict)

                if idval is not None and name is not None:
                    idtonamedict[idval] = name
                    print(f'{idval:<3}\t{name:<15}\t{price:<8}\t{duration:<5}')
        print('-' * 40)
        if allowmultiple:
            prompt = 'Please enter a comma-delimited list of IDs that you would like to search for: '
        else:
            prompt = 'Please enter the ID of the machine that you would like to reserve: '
        rawinpt = input(prompt)
        if allowmultiple:
            if rawinpt == '':
                idlist = []
            else:
                idlist = rawinpt.replace(', ', ',').split(',')
            outlist = []
            for mid in idlist:
                machname = getmachinenamefromid(mid, machinelist)
                if machname != '':
                    outlist.append(machname)
            return outlist
        else:
            return getmachinenamefromid(rawinpt, machinelist)
    else:
        if allowmultiple:
            prompt = 'Please enter a comma-delimited list of machine names that you would like to search for: '
        else:
            prompt = 'Please enter the name of the machine that you would like to reserve: '
        return input(prompt)


def getmachinenamefromid(machid: str, machinelist: list) -> str:
    namekey = 'Name'
    idkey = 'IType'
    if machinelist is not None:
        for mdict in machinelist:
            if namekey in mdict and idkey in mdict and str(mdict[idkey]) == machid:
                return mdict[namekey]
        return ''
    else:
        return machid


def getmchinfofromdict(mchdict) -> (int, str, float, float):
    namekey = 'Name'
    idkey = 'IType'
    pricekey = 'Price'
    durationkey = 'Duration_Hrs'
    if idkey in mchdict:
        idval = mchdict[idkey]
    else:
        idval = None
    if namekey in mchdict:
        name = mchdict[namekey]
    else:
        name = None
    if pricekey in mchdict:
        price = mchdict[pricekey]
    else:
        price = None
    if durationkey in mchdict:
        duration = mchdict[durationkey]
    else:
        duration = None
    return idval, name, price, duration


def cancelres():
    global usr
    print(f'Please enter information about the reservation you would like to cancel\n'
          f"If you would like to stop creating a reservation, enter '{quitinpt}'")
    resid = input('Enter the reservation id that you would like to cancel: ')

    if resid == quitinpt:
        print('No reservation will be cancelled')
        return
    cancelresult = usr.cancelres(resid)
    if type(cancelresult) is float:
        print(f'Reservation cancelled successfully.\nYour account was refunded {float}')
    return


def modifyres():
    global usr
    quitmsg = 'No reservation will be edited'

    print(f'Please enter information about the reservation you would like to edit\n'
          f"If you would like to stop editing a reservation, enter '{quitinpt}'")
    resid = input('Enter the reservation id that you would like to edit: ')
    if resid == quitinpt:
        print(quitmsg)
        return

    res = usr.getres(resid)
    if res is None:
        print(f'Unable to find an active reservation with an ID of {resid}\n{quitmsg}')
        return

    print("If you would not like to edit a specific field, do not enter anything and press the return key")
    existingstarttime = res.machres.starttime
    print(f'The current start time for this reservation is {existingstarttime}')
    newstarttime = gettimeinput(starttime=True)
    if newstarttime == quitinpt:
        print(quitmsg)
        return
    elif newstarttime == '':
        newstarttime = existingstarttime
    else:
        try:
            newstarttime = datetime.strptime(newstarttime, timeformatinptformat).strftime(timeformatapiformat)
        except ValueError:
            print(f'The time entered was not in the correct format.\n{quitmsg}')
            return

    existingendtime = res.machres.endtime
    print(f'The current end time for this reservation is {existingendtime}')
    newendtime = gettimeinput(starttime=False)
    if newendtime == quitinpt:
        print(quitmsg)
        return
    elif newendtime == '':
        newendtime = existingendtime
    else:
        try:
            newendtime = datetime.strptime(newendtime, timeformatinptformat).strftime(timeformatapiformat)
        except ValueError:
            print(f'The time entered was not in the correct format.\n{quitmsg}')
            return

    existingmachinetype = res.machres.machinetype
    print(f'The current machine type for this reservation is {existingmachinetype}')
    newmachinetype = input("Please enter a new machine type for this reservation: ")
    if newmachinetype == quitinpt:
        print(quitmsg)
        return
    elif newmachinetype == '':
        newmachinetype = existingmachinetype

    if existingstarttime == newstarttime and existingendtime == newendtime and existingmachinetype == newmachinetype:
        print('No information was changed, so an edit request will not be submitted')
        return
    else:
        editresult = usr.editres(resid, newstarttime, newendtime, newmachinetype)
        if editresult:
            print(f'Reservation {resid} was changed successfully')
        else:
            print(f'Unable to edit reservation {resid}')
    return


def listres():
    global usr
    reslist = usr.getreslist()
    if reslist is None or len(reslist) == 0:
        print('NO RESERVATIONS FOUND')
    else:
        print(f'{"ID":<3}\t{"StartTime":<20}\t{"EndTime":<20}\t{"MachineType":<30}')
        for res in reslist:
            print(f'{res.resid:<3}\t{res.machres.starttime.strftime(timeformatinptformat):<20}'
                  f'\t{res.machres.endtime.strftime(timeformatinptformat):<20}\t{res.machres.machinetype:<30}')
    return


def addfunds():
    quitmsg = 'No funds will be added'
    print(f"If you would not like to add funds, enter '{quitinpt}'")
    rawaddamount = input('Enter the amount of funds you would like to add: ')
    try:
        addamount = float(rawaddamount)
    except ValueError:
        print(f'The value entered was not a valid amount.\n{quitmsg}')
        return

    if rawaddamount == 0.00:
        print(f'A zero amount was entered.\n{quitmsg}')
        return
    else:
        global usr
        newbalance = usr.addfunds(addamount)
        if newbalance is None:
            print(f'Unable to add funds.')
        else:
            print(f'Funds added successfully.\nYour new balance is {newbalance:.2f}')
    return


def listtrans():
    global usr
    translist = usr.gettranslist()

    if translist is None:
        print('Unable to get a list of transactions')
    else:
        printtranslist(translist)
    return


def editprofile():
    global usr
    quitmsg = 'Your username will not be changed'
    print(f"If you would not like to edit your username, enter '{quitinpt}'")
    newusername = input(f'Enter your new username: ')
    if newusername == quitinpt:
        print(quitmsg)
        return
    elif newusername == '':
        print(f'Cannot change a username to an empty string.\n{quitinpt}')
        return
    elif newusername == usr.username:
        print(f'The username you specified matches your current username.\n{quitinpt}')
    else:
        changeresult = usr.changeusername(newusername)
        if changeresult:
            print('Username was changed successfully')
        else:
            print('Unable to perform username change')
    return


def balance():
    global usr
    bal = usr.getbalance()
    if bal is None:
        print('Unable to get your current balance.')
    else:
        print(f'Your current balance is {bal:.2f}')
    return


def runfacilitymanagerevents():
    u_inpt = input("Please enter an action you would like to perform.\n"
                   "Enter '-help' for a list of valid commands.\n")
    action = getact(u_inpt, 3)

    if action == loggedoutacts[quitinpt]:
        global quitbool
        quitbool = True
        return

    # doing this for some visual separation between commands
    print('-' * 40)
    switcher = {
        201: makeres_fm,
        202: cancelres,
        203: modifyres,
        204: listres_fm,
        205: findres,
        206: createclient,
        207: editclient,
        208: findclient,
        209: partial(setclientstatus, False),
        210: partial(setclientstatus, True),
        211: addfunds_fm,
        212: listclients,
        213: listtrans_fm,
        214: listclienttrans,
        998: partial(showhelp, loggedinfmacts),
        10: logout,
        -1: lambda: print(f"Invalid input '{u_inpt}'\nEnter '-help' to see a list of valid commands.\n"),
    }
    switcher.get(action)()
    print('-' * 40)
    return


def makeres_fm():
    quitmsg = 'No reservation was created'
    global usr
    print(f'Please enter information about the new reservation below\n'
          f"If you would like to stop creating a reservation, enter '{quitinpt}'")

    clientusername = input('Enter a client username for this reservation: ')
    if clientusername == quitinpt:
        print(quitmsg)
        return

    machineinpt = getmachineinpt(allowmultiple=False)
    if machineinpt == quitinpt:
        print(quitmsg)
        return

    starttimeinpt = gettimeinput(starttime=True)
    if starttimeinpt == quitinpt:
        print(quitmsg)
        return

    endtimeinpt = gettimeinput(starttime=False)
    if endtimeinpt == quitinpt:
        print(quitmsg)
        return

    mkresresult = usr.makeres(clientusername, starttimeinpt, endtimeinpt, machineinpt)
    if type(mkresresult) is bool:
        if mkresresult:
            print('Reservation created successfully')
        else:
            print('Reservation could not be created')
    else:
        print(f'Reservation could not be created: {mkresresult}')
    return


def listres_fm():
    quitmsg = 'Operation cancelled'
    allflag = '-all'
    clientflag = '-client'
    dateflag = '-date'

    global usr
    print(f'Enter {quitinpt} at any time to abandon the current operation')
    print('Would you like to list all reservations, reservations for a specific client, or reservatioon for a date range?')
    inpt = input(f'Enter {allflag} for all, {clientflag} for client, or {dateflag} for a date range: ')

    if inpt == quitinpt:
        print(quitmsg)
        return
    elif inpt == allflag:
        reslist = usr.getreslist(username='')
    elif inpt == clientflag:
        client = input('Enter the username of the client you would like to search for: ')
        if client == quitinpt:
            print(quitmsg)
            return
        reslist = usr.getreslist(client)
    elif inpt == dateflag:
        rawstime = gettimeinput(starttime=True)
        if rawstime == quitmsg:
            print(quitmsg)
            return
        rawetime = gettimeinput(starttime=False)
        if rawetime == quitmsg:
            print(quitmsg)
            return
        try:
            stime = datetime.strptime(rawstime, timeformatinptformat).strftime(timeformatapiformat)
            etime = datetime.strptime(rawetime, timeformatinptformat).strftime(timeformatapiformat)
        except ValueError:
            print(f'Either the start or end times entered were invalid.\n{quitmsg}')
            return
        reslist = usr.getreslist(username='', starttimestr=stime, endtimestr=etime)
    else:
        print(f'Invalid input detected.\n{quitmsg}')
        return
    printreslist(reslist)
    return


def printtranslist(translist: list):
    if translist is None or len(translist) == 0:
        print('NO TRANSACTIONS FOUND')
    else:
        print(f'{"ID":<5}\t{"UserID":<10}\t{"Price":<8}\t{"Type":<10}\t{"Time":<20}')
        for t in translist:
            if t.id is None:
                idval = 'NONE'
            else:
                idval = t.id
            if t.userid is None:
                userid = 'NONE'
            else:
                userid = t.userid
            if t.price is None:
                priceval = 'NONE'
            else:
                priceval = t.price
            if t.type is None:
                typeval = 'NONE'
            else:
                typeval = t.type
            if t.time is None:
                timeval = 'NONE'
            else:
                timeval = t.time

            pstr = f'{priceval:.2f}'
            # can't format lists using :< formatting
            print(f'{idval:<5}\t{userid:<10}\t{pstr:<8}\t{typeval:<10}\t{timeval:<20}')
    return


def printreslist(reslist: list):
    if reslist is None or len(reslist) == 0:
        print('NO RESERVATIONS FOUND')
    else:
        print(f'{"ID":<5}\t{"StartTime":<20}\t{"EndTime":<20}\t{"MachineType":<30}')
        for res in reslist:
            print(f'{res.resid:<5}\t{res.machres.starttime.strftime(timeformatinptformat):<20}'
                  f'\t{res.machres.endtime.strftime(timeformatinptformat):<20}\t{res.machres.machinetype:<30}')
    return


def findres():
    quitmsg = 'Reservation search abandoned'
    print('Please enter criteria for the reservation search below\n'
          f"If you would like to stop creating a reservation, enter '{quitinpt}'\n"
          'If you would not like to include a specific value from your search, do not enter anything for that value')

    searchpattern = input('Enter a client username pattern to search for (* is a wildcard): ')
    if searchpattern == quitinpt:
        print(quitmsg)
        return

    machineidsearchlist = getmachineinpt(allowmultiple=True)
    if machineidsearchlist == quitinpt or \
            (type(machineidsearchlist) is list and len(machineidsearchlist) > 0 and machineidsearchlist[0] == quitinpt):
        print(quitmsg)
        return

    starttimeinpt = gettimeinput(starttime=True)
    if starttimeinpt == quitinpt:
        print(quitmsg)
        return
    elif starttimeinpt == '':
        starttime = None
    else:
        try:
            starttime = datetime.strptime(starttimeinpt, timeformatinptformat)
        except ValueError:
            print('Start time was not in the correct format, so it will not be included in the search')
            starttime = None

    endtimeinpt = gettimeinput(starttime=False)
    if endtimeinpt == quitinpt:
        print(quitmsg)
        return
    elif endtimeinpt == '':
        endtime = None
    else:
        try:
            endtime = datetime.strptime(endtimeinpt, timeformatinptformat)
        except ValueError:
            print('End time was not in the correct format, so it will not be included in the search')
            starttime = None

    global usr
    matchingreslist = usr.searchreservations(searchpattern, starttime, endtime, machineidsearchlist)
    if matchingreslist is None:
        print('Unable to get a list of matching reservations')
    else:
        printreslist(matchingreslist)
    return


def createclient():
    quitmsg = 'No client was created'
    print(f'Please enter information about the client that you would like to create.\n'
          f'If you would not like to create a client, enter {quitinpt} at any time')

    username = input('Please enter a username for the new client: ')
    if username == quitinpt:
        print(quitmsg)
        return
    elif username == '':
        print(f'A username was not specified for the new client.\n{quitmsg}')
        return

    pw = input('Please enter a password for the new client: ')
    if username == quitinpt:
        print(quitmsg)
        return
    elif username == '':
        print(f'A password was not specified for the new client.\n{quitmsg}')
        return

    # Assuming this only needs to create clients and not facility managers
    # creating facility managers is handled by the Register endpoint
    registersuccess = User.register(username, pw, False, True)
    if registersuccess:
        print('Client created successfully')
    else:
        print('Unable to create a new client')
    return


def editclient():
    global usr
    quitmsg = 'A profile will not be edited'
    print(f"If you would not like to edit a profile, enter '{quitinpt}'")
    existingusername = input('Enter the username that you would like to change\n'
                             'If nothing is entered, your username will be used')
    if existingusername == quitinpt:
        print(quitmsg)
        return
    elif existingusername == '':
        existingusername = usr.username
    newusername = input(f'Enter the username that you would like to change {existingusername} to: ')
    if newusername == quitinpt:
        print(quitmsg)
        return
    elif newusername == '':
        print(f'Cannot change a username to an empty string.\n{quitinpt}')
        return
    else:
        changeresult = usr.changeusername(existingusername, newusername)
        if changeresult:
            print('Username was changed successfully')
        else:
            print('Unable to perform username change')
    return


def printclientlist(clientlist: list):
    if len(clientlist) == 0:
        print('No clients were found')
    else:
        print('Username')
        for client in clientlist:
            print(client)
    return


def listclients():
    global usr
    clientlist = usr.getclientlist()
    if clientlist is None:
        print('Unable to get a list of clients')
    else:
        printclientlist(clientlist)
    return


def findclient():
    quitmsg = 'Client search abandoned'
    print(f"If you would not like to search clients, enter '{quitinpt}'")
    inptpattern = input('Enter a username pattern to search for: ')
    if inptpattern == quitinpt:
        print(quitmsg)
        return

    global usr
    searchclientlist = usr.searchclients(inptpattern)
    if searchclientlist is None:
        print('Unable to get a list of matching clients')
    else:
        printclientlist(searchclientlist)
    return


def setclientstatus(newstatus: bool):
    if newstatus:
        statusstr = 'activate'
    else:
        statusstr = 'deactivate'
    client = input(f"Enter a username to {statusstr}: ")
    if client == quitinpt:
        print('Client status will not be changed')
        return

    global usr
    if newstatus:
        result = usr.activateclient(client)
    else:
        result = usr.deactivateclient(client)
    if result:
        print(f'{client} {statusstr}d successfully')
    else:
        print(f'Unable to {statusstr} {client}')
    return


def addfunds_fm():
    quitmsg = 'No funds will be added'
    print(f"If you would not like to add funds, enter '{quitinpt}'")
    addusername = input('Enter the username that you would like to add funds for: ')
    if addusername == quitinpt or addusername == '':
        print(quitmsg)
        return
    rawaddamount = input('Enter the amount of funds you would like to add: ')
    try:
        addamount = float(rawaddamount)
    except ValueError:
        print(f'The value entered was not a valid amount.\n{quitmsg}')
        return

    if rawaddamount == 0.00:
        print(f'A zero amount was entered.\n{quitmsg}')
        return
    else:
        global usr
        newbalance = usr.addfunds(addusername, addamount)
        if newbalance is None:
            print(f'Unable to add funds.')
        else:
            print(f'Funds added successfully.\nThe new balance for {addusername} is {newbalance:.2f}')
    return


def listtrans_fm():
    global usr
    translist = usr.gettranslist()
    if translist is None:
        print('Unable to get a list of transactions')
    else:
        printtranslist(translist)
    return


def listclienttrans():
    quitmsg = 'No transactions will be listed'
    print(f"If you would not like to get a list of transactions, enter '{quitinpt}'")
    username = input('Enter the name of the client that you would like to use: ')
    if username == quitinpt:
        print(quitmsg)
        return
    elif username == '':
        print(f'No username value was provided.\n{quitinpt}')
    translist = usr.gettranslist(username)
    if translist is None:
        print('Unable to get a list of transactions')
    else:
        printtranslist(translist)
    return


if __name__ == '__main__':
    main()
