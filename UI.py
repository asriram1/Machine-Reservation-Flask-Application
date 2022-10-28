from flask import Flask, jsonify, request, make_response, render_template, session, redirect, url_for
from forms import * #SignUpForm, LoginForm, ReservationCreate, ShowReservations, EditReservations, CancelReservations, AddFunds, ListTransactions, EditProfile, FMLogin, ReservationSearch
from db import DBCls
from Database import Database
from BusinessLogic import Reservation
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'team8'
timestr = '%Y-%m-%d %H:%M:%S'
BL = Reservation()
DBObj = DBCls()
DBObj2 = Database()

@app.route("/", methods = ['GET'])
def homepage():
    #return render_template('UserLogin.html')
    return redirect(url_for('userlogin'))

@app.route("/login", methods = ['GET', 'POST'])
def userlogin():
    form = LoginForm()
    if form.is_submitted():
        result = request.form
        username = result['username']
        password = result['password']
        isfm = DBObj.isuserfacilitymanager(username)

        if isfm:
            return redirect(url_for('fmlogin'))

        if DBObj.login(username, password):
            newtoken = DBObj.generatetoken(username)
            isfm = DBObj.isuserfacilitymanager(username)
            session['username'] = username
            #return make_response(jsonify({'Token': newtoken, 'IsFacilityManager': isfm}), 200)
            return render_template("ClientOptions.html", username = username)
        else:
            return render_template('LoginFail.html')
    
    return render_template('login.html', form = form)


@app.route("/fmlogin", methods = ['GET', 'POST'])
def fmlogin():
    form = FMLogin()
    if form.is_submitted():
        result = request.form
        username = result['username']
        password = result['password']
        if DBObj.login(username, password):
            newtoken = DBObj.generatetoken(username)
            isfm = DBObj.isuserfacilitymanager(username)
            session['username'] = username

            x = DBObj.isuserfacilitymanager(username)
            if x == False:
                return render_template('LoginFail.html')
            #return make_response(jsonify({'Token': newtoken, 'IsFacilityManager': isfm}), 200)
            return render_template("FMOptions.html", username = username)
        else:
            return render_template('LoginFail.html')
    
    return render_template('fmlogin.html', form = form)

@app.route("/fmhome", methods = ['GET', 'POST'])
def fmhome():
    username = session['username']
    return render_template("FMOptions.html", username = username)

@app.route("/fm/clients", methods = ['GET', 'POST'])
def getclientlist():

    clientlist = DBObj.getclientlist()
    username = session['username']

    if clientlist is None:
        return render_template("ClientListSuccess.html", username = username, clientlist = "Error!")
    else:
        return render_template("ClientListSuccess.html", username = username, clientlist = clientlist)

@app.route('/fm/reservations/search', methods=['GET', 'POST'])
def searchreservations():

    form = ReservationSearch()
    if form.is_submitted():
        result = request.form
        username = result['username']
        stimekey = result['stimekey']
        etimekey = result['etimekey']
        machid = result['machineid']

        stime = datetime.strptime(stimekey, timestr)
        etime = datetime.strptime(etimekey, timestr)

        machidlist = [machid]

        reslist = DBObj.getreservationlist(username, stime, etime, machidlist)
        if reslist is None:
            return render_template('SearchReservationSuccess.html', username = username, reslist = "Error")
        else:
            #return make_response(jsonify({'ReservationList': reslist}), 200)
            return render_template('SearchReservationSuccess.html', username = username, reslist = reslist)


        #return render_template('user.html', result = result)
    return render_template('SearchReservations.html', form = form)



@app.route('/fm/clientlist/search', methods=['GET', 'POST'])
def searchclients():

    form = ClientListSearch()
    if form.is_submitted():
        result = request.form
        username = session['username']
        unamepattern = result['unamepatternkey']
        uidpattern = result['uidpatternkey']


        matchingclientlist = DBObj.getmatchingclientlist(unamepattern, uidpattern)
        if matchingclientlist is None:
            return render_template('ClientSearchSuccess.html', username = username, matchingclientlist = "Error")
        else:
            return render_template('ClientSearchSuccess.html', username = username, matchingclientlist = matchingclientlist)


        #return render_template('user.html', result = result)
    return render_template('ClientListSearch.html', form = form)



@app.route('/fm/machinelist', methods=['GET', 'POST'])
def machinelist():
    machinelist = DBObj.getmachinelist()
    username = session['username']
    if machinelist is None:
        return render_template('MachineList.html', username = username, machinelist = "Error!")
    else:
        return render_template('MachineList.html', username = username, machinelist = machinelist)


@app.route("/home", methods = ['GET', 'POST'])
def home():
    username = session['username']
    return render_template("ClientOptions.html", username = username)

@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = SignUpForm()
    if form.is_submitted():
        result = request.form
        username = result['username']
        password = result['password']
        typekey = result['typekey']
        isactivekey = result['isactive']
        if DBObj.register(username, password, typekey, isactivekey):
            #return make_response(jsonify({'success': 'Register successful'}), 200)
            return render_template('RegisterSuccess.html', username = username)
        else:
            return render_template('RegisterFail.html')

        #return render_template('user.html', result = result)
    return render_template('signup.html', form = form)


@app.route('/reservations/create', methods=['GET','POST'])
def makeres():

    form = ReservationCreate()

    if form.is_submitted():
        result = request.form
        username = session['username']
        etimekey = result['etimekey']
        stimekey = result['stimekey']
        machineidkey = result['machineidkey']
        try:
            machineid = int(machineidkey)
        except ValueError:
            return render_template('ReservationCreateFail.html', username = username)
            #return make_response(jsonify({'error': f'Invalid {machineidkey} value'}), 400)

        stime = datetime.strptime(stimekey, timestr)
        etime = datetime.strptime(etimekey, timestr)
        
        #createresult = BL.make_reservation(username, machineid, stimekey,etimekey)
    
        createresult = DBObj.makeres(username, stime, etime, machineid)
        #createresult = DBObj2.add_reservation
        if type(createresult) is bool:
            if createresult:
                #return make_response(jsonify({'success': 'Reservation created successfully'}), 200)
                return render_template('ReservationCreateSuccess.html', username = username)
            else:
                return render_template('ReservationCreateFail.html', username = username)
        else:
            #return make_response(jsonify({'error': createresult}), 400)
            return render_template('ReservationCreateFail.html', username = username)

        #return render_template('user.html', result = result)
    return render_template('CreateReservation.html', form = form)
    


@app.route('/reservations/list', methods=['GET', 'POST'])
def getreslist():

    form = ShowReservations()
    username = session['username']
    if form.is_submitted():
        result = request.form
        username = session['username']
        etimekey = result['etimekey']
        stimekey = result['stimekey']
        machineidkey = result['machineidkey']
        try:
            machineid = int(machineidkey)
        except ValueError:
            return render_template('ReservationListSuccess.html', username = username, reslist = "Invalid Machine ID!")
            #return make_response(jsonify({'error': f'Invalid {machineidkey} value'}), 400)
    
        stime = datetime.strptime(stimekey, timestr)
        etime = datetime.strptime(etimekey, timestr)
        machidlist = [machineidkey]

        #reslist = DBObj.getreservationlist(username, stime, etime, machidlist)
        reslist = DBObj2.reservation_details(None, stime, etime, None, None,
                                                     username)

        if reslist is None:
            return render_template('ReservationListSuccess.html', username = username, reslist = "Error")
        else:
            return render_template('ReservationListSuccess.html', username = username, reslist = reslist)
            #return make_response(jsonify({'ResList': reslist}), 200)

    return render_template('ShowReservations.html', form = form, username = username)


@app.route('/reservations/edit', methods=['GET','POST'])
def editres():


    form = EditReservations()
    username = session['username']
    if form.is_submitted():
        result = request.form
        username = session['username']
        reservationid = result['reservationid']
        etimekey = result['etimekey']
        stimekey = result['stimekey']
        #machineidkey = result['machineidkey']


        kwargsdict = {}
        kwargsdict['ResID'] = reservationid
        kwargsdict['Time_Start'] = datetime.strptime(stimekey, timestr)
        kwargsdict['Time_End'] = datetime.strptime(etimekey, timestr)
        #kwargsdict['MachineID'] = machineidkey


        #editresult = DBObj.editres(**kwargsdict)
        editresult = BL.edit_reservation(reservationid,stimekey, etimekey)
        if not editresult:
            return render_template('ReservationEditFail.html', username = username)
        else:
            return render_template('ReservationEditSuccess.html', username = username)
            #return make_response(jsonify({'success': 'reservation edited successfully'}), 200)


    return render_template('EditReservations.html', form = form, username = username)




@app.route('/reservations/cancel', methods=['GET','POST'])
def cancelres():


    form = CancelReservations()
    username = session['username']
    if form.is_submitted():
        result = request.form
        resid= result['reservationid']
        cancelresult, refund = BL.cancel_reservation(resid)
    
        #cancelresult = DBObj.cancelres(resid)
        if not cancelresult:
            return render_template('ReservationCancelFail.html', username = username)
        else:
            return render_template('ReservationCancelSuccess.html', username = username, refund = refund)
            #return make_response(jsonify({'success': 'Reservation cancelled successfully'}), 200)


    return render_template('CancelReservation.html', form = form, username = username)



@app.route('/balance/addfunds', methods=['GET','POST'])
def addfunds():

    form = AddFunds()
    username = session['username']
    if form.is_submitted():
        result = request.form
        funds= result['funds']
        addfundsresult = DBObj.addfunds(username, int(funds))
        if not addfundsresult:
            return render_template('AddFundsSuccess.html', username = username, newbal = "Error!")
        else:
            newbal = DBObj.getbalance(username)
            return render_template('AddFundsSuccess.html', username = username, newbal = newbal)
            #return make_response(jsonify({'Username': username, 'Balance': newbal}), 200)
    

    return render_template('AddFunds.html', form = form, username = username)




@app.route('/transactions/list', methods=['GET','POST'])
def listtrans():

    form = ListTransactions()
    username = session['username']
    if form.is_submitted():
        result = request.form
        stime = result['stimekey']
        etime = result['etimekey']

        stime = datetime.strptime(stime, timestr)
        etime = datetime.strptime(etime, timestr)

        translist = DBObj.gettranslist(username, stime, etime)
        if translist is None:
            #return make_response(jsonify({'error': 'Unable to get transactions list'}), 403)
            return render_template('TransactionSuccess.html', username = username, translist = "Error!")
        else:
            return render_template('TransactionSuccess.html', username = username, translist = translist)
            #return make_response(jsonify({'TransactionList': translist}), 200)


    return render_template('PastTransactions.html', form = form, username = username)



@app.route('/balance/view', methods=['GET'])
def getbalance():

    username = session['username']
    balance = DBObj.getbalance(username)
    if balance is None:
        return render_template('BalanceSuccess.html', username = username, balance = "Error!")
        # return make_response(jsonify({'error': 'Getting balance failed'}), 403)
    else:
        return render_template('BalanceSuccess.html', username = username, balance = balance)
        #return make_response(jsonify({'Balance': balance}), 200)


@app.route('/reservations/cost', methods=['GET','POST'])
def calccost():

    form = CalculateCost()
    username = session['username']
    if form.is_submitted():
        result = request.form
        machineid = result['machineidkey']
        stimekey = result['stimekey']
        etimekey = result['etimekey']

        stime = datetime.strptime(stimekey, timestr)
        etime = datetime.strptime(etimekey, timestr)

        resprice = DBObj.getresprice(machineid, stime, etime)
        if resprice is None:
            return render_template('ReservationCostSuccess.html', username = username, resprice = "Error!")
        else:
            return render_template('ReservationCostSuccess.html', username = username, resprice = resprice)
    
    return render_template('ReservationCost.html', form = form, username = username)

@app.route('/editprofile', methods=['GET','POST'])
def changeusername():

    form = EditProfile()
    username = session['username']
    if form.is_submitted():
        result = request.form
        newusername = result['newusername']


        changeresult = DBObj.changeusername(username, newusername)

        if not changeresult:
            #return make_response(jsonify({'error': 'Username change failed'}), 403)
            return render_template('EditProfileSuccess.html', newusername = "Error!")
        else:
            return render_template('EditProfileSuccess.html', newusername = newusername)
            #return make_response(jsonify({'success': 'Username change successful'}), 200)


    return render_template('EditProfile.html', form = form, username = username)


@app.route('/logout', methods=['GET','POST'])
def logout():
    return render_template('Logout.html')





if __name__ == '__main__':
    app.run(debug=True, port = 4996)