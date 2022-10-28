# Final Project for Applied Software Engineering: API epic
# Author: Anqi Ni
# Last Update:  6/4/2020

from flask import Flask, jsonify, request, make_response
from functools import wraps
from BusinessLogic import Reservation
import jwt
import datetime


app = Flask(__name__)
BL = Reservation()

# secrete key to sign the token
app.config['SECRET_KEY'] = 'team8isthebestteamintheworld'


# wrapper functions for token validation
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('Token')
        if not token:
            return jsonify({"Reason": 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'Reason': 'invalid credentials specified'}), 401
        return f(*args, **kwargs)

    return decorated


def active_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('Token')
        data = {}
        if not token:
            return jsonify({"Reason": 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'Reason': 'invalid credentials specified'}), 401
        if not isprofileactive(data):
            return jsonify({'Reason': 'user is not active'}), 403
        return f(*args, **kwargs)

    return decorated


def fm_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('Token')
        data = {}
        if not token:
            return jsonify({"Reason": 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'Reason': 'invalid credentials specified'}), 401
        if data['type'].upper() != 'FM':
            return jsonify({'Reason': 'Not a facility Manager'}), 403
        return f(*args, **kwargs)

    return decorated


# @app.route('/unprotected')
# def unprotected():
# 	return "everyone can see this"


# @app.route('/protected')
# @token_required
# def protected():
# 	return "only available for people with token"

@app.route('/api')
def hello():
    return "Welcome to team 8 API."


@app.route('/api/login', methods=['POST'])
def login():
    req_data = request.get_json()
    if not req_data:
        return jsonify({"Reason": "No parameter provided."}), 400

    username = req_data['Username']
    password = req_data['Password']

    # login verify
    if not BL.login(username, password):
        return make_response('Could not verify!', 401, {"WWW-Authenticate": 'Basic realm="Login Required"'})
    # get profile by username
    profile = BL.user_profile(username)
    # encode the token
    token = jwt.encode({'user': username, \
                        'type': profile['type'], \
                        'isActive': isprofileactive(profile), \
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                        }, app.config['SECRET_KEY'])
    # response
    return jsonify({'Token': token.decode('UTF-8'), \
                    'Type': profile['type'], \
                    'IsActive': isprofileactive(profile)})


def isprofileactive(profiledict: dict) -> bool:
    skey = 'is_active'
    # This codebase is getting really messy,
    # but I don't have the time or patience to clean this up right now
    skey_alt = 'isActive'
    if skey in profiledict:
            # this should always be a boolean,
            # but making this explicit will always cause this function to return a boolean
            # regardless of the dictionary's value
            # if it's 0/1, this will still always return a boolean
        return profiledict[skey] == True
    elif skey_alt in profiledict:
        return profiledict[skey_alt] == True
    else:
        return False


@app.route('/api/register', methods=["POST"])
def register():
    # get request data
    req_data = request.get_json()
    # user input validation
    if not req_data:
        return jsonify({"Reason": "No parameter provided."}), 400
    if not validate_user_register(req_data):
        return jsonify({"Reason": "Data is Malformatted."}), 400

    username = req_data['Username']
    password = req_data['Password']
    usertype = req_data['Type']

    registerresult = BL.add_user(username, password, usertype)
    if registerresult:
        return jsonify({"Username": username}), 200
    else:
        return jsonify({'Reason': 'User already exists'}), 403


@app.route('/api/profile', methods=["GET"])
@token_required
def profile():
    # extract username from token
    token = request.args.get('Token')
    data = jwt.decode(token, app.config['SECRET_KEY'])
    username = gettargetuserforreq(request, data)
    res = BL.user_profile(username)

    return jsonify({"Username": username,
                    "Funds": res['funds'],
                    "IsActive": isprofileactive(res),
                    "Type": res['type']}), 200


def gettargetuserforreq(req: request, data: dict) -> str:
    targetunamekey = 'TargetUsername'
    if targetunamekey in request.json:
        return req.json[targetunamekey]
    else:
        return data['user']


@app.route('/api/profile', methods=["POST"])
@token_required
def change_username():
    # extract username from token
    token = request.args.get('Token')

    req_data = request.get_json()
    if not validate_change_username(req_data):
        return jsonify({"Reason": "Data is Malformatted."}), 400

    data = jwt.decode(token, app.config['SECRET_KEY'])
    username = gettargetuserforreq(request, data)
    newusername = req_data['NewUsername']

    editresult = BL.edit_user(username, new_username=newusername)
    if editresult:
        return jsonify({"Username": newusername}), 200
    else:
        return jsonify({"Reason": 'Unable to change username'}), 400


@app.route('/api/status', methods=['POST'])
@fm_token_required
def set_status():
    req_data = request.get_json()
    if not req_data:
        return jsonify({"Reason": "No parameter provided."}), 400

    if not validate_set_status(req_data):
        return jsonify({"Reason": "Data is Malformatted."}), 400

    username = req_data['Username']
    is_active = isprofileactive(req_data)
    return jsonify(req_data), 200


@app.route('/api/clients', methods=['GET'])
@fm_token_required
def list_client():
    clients = BL.list_clients()
    return jsonify({"ClientList": clients})


@app.route('/api/clients/search', methods=['GET'])
@fm_token_required
def search_client():
    pkey = 'PartialUsername'
    if pkey not in request.json:
        return jsonify({'Reason': f'Missing {pkey} in request'}), 400
    unamepattern = request.json[pkey]

    matchlist = BL.user_search(unamepattern)
    if matchlist is None:
        return jsonify({'Reason': 'Unable to search clients'}), 400
    else:
        outlist = []
        for user in matchlist:
            unamekey = 'username'
            if unamekey in user:
                outlist.append({unamekey: user[unamekey]})
        return jsonify(outlist), 200


@app.route('/api/reservations/list', methods=['GET'])
@token_required
def list_reservation():
    token = request.args.get('Token')
    data = jwt.decode(token, app.config['SECRET_KEY'])

    usernamekey = 'TargetUsername'
    if usernamekey in data:
        username = data[usernamekey]
    else:
        username = ''

    time_start = request.args.get('Time_Start')
    time_end = request.args.get('Time_End')

    reslist = BL.get_reservations(username=username, start_datetime=time_start, end_datetime=time_end)

    if reslist is None:
        jsonify({'error': 'Unable to get reservation list'}), 400
    else:
        return jsonify({"ResList": reslist}), 200


@app.route('/api/reservations/edit', methods=['POST'])
@active_token_required
def edit_reservation():
    token = request.args.get('Token')
    data = jwt.decode(token, app.config['SECRET_KEY'])
    username = data['user']

    req_data = request.get_json()
    # validate user input
    reskey = 'Res'
    idkey = 'ResID'
    machkey = 'Machine'
    if not req_data or \
            reskey not in req_data or \
            machkey not in req_data[reskey] or \
            idkey not in req_data[reskey] or \
            not validate_machine(req_data[reskey][machkey]):
        return jsonify({"Reason": "Data is Malformatted."}), 400

    reservation_id = req_data[reskey][idkey]
    start_datetime_str = req_data[reskey][machkey]['Time_Start']
    end_datetime_str = req_data[reskey][machkey]['Time_End']

    success, payment = BL.edit_reservation(reservation_id, start_datetime_str, end_datetime_str)
    if success:
        # want to return the original request data representing the new edited reservation
        return jsonify(req_data), 200
    else:
        return jsonify({'error': 'Unable to edit reservation'}), 400


@app.route('/api/reservations/create', methods=['POST'])
@active_token_required
def create_reservation():
    token = request.args.get('Token')
    data = jwt.decode(token, app.config['SECRET_KEY'])
    targetusername = gettargetuserforreq(request, data)

    req_data = request.get_json()
    # validate user input
    if not req_data or \
            "Res" not in req_data or \
            "Machine" not in req_data['Res'] or \
            not validate_machine(req_data['Res']["Machine"]):
        print(f'{"Res" not in req_data}, {"Machine" not in req_data["Res"]}\n{validate_machine(req_data["Res"]["Machine"])}')
        return jsonify({"Reason": "Data is Malformatted."}), 400

    machdict = req_data['Res']['Machine']
    machine = machdict['MachineType']
    start_datetime = machdict['Time_Start']
    end_datetime = machdict['Time_End']
    makeresresult, resid = BL.make_reservation(targetusername, machine, start_datetime, end_datetime)

    if makeresresult:
        return jsonify({'Result': 'Success'}), 200
    else:
        return jsonify({'error': 'Unable to create request'}), 400


@app.route('/api/reservations/cancel', methods=['POST'])
@active_token_required
def cancel_reservation():
    token = request.args.get('Token')
    data = jwt.decode(token, app.config['SECRET_KEY'])
    username = data['user']

    req_data = request.get_json()
    # validate user input
    if not req_data or "Res" not in req_data or "ResID" not in req_data['Res']:
        return jsonify({"Reason": "Data is Malformatted."}), 400

    success, refund = BL.cancel_reservation(req_data['Res']['ResID'])

    if success:
        return jsonify({"Refund": refund}), 200
    else:
        return jsonify({'error': 'Unable to cancel reservation'}), 400


@app.route('/api/transactions/list', methods=['GET'])
@active_token_required
def list_transactions():
    token = request.args.get('Token')
    data = jwt.decode(token, app.config['SECRET_KEY'])
    username = data['user']

    req_data = request.get_json()
    tukey = 'TargetUsername'
    skey = 'Time_Start'
    ekey = 'Time_End'
    if tukey in req_data:
        username = req_data[tukey]
    else:
        username = None
    if skey in req_data:
        starttime = req_data[skey]
    else:
        starttime = None
    if ekey in req_data:
        endtime = req_data[ekey]
    else:
        endtime = None

    tset = BL.get_transactions(transaction_id=None, reservation_id=None, username=username, start_datetime=starttime,
                               end_datetime=endtime, transaction_type=None)
    return jsonify({"TransactionList": tset}), 200


@app.route('/api/addfunds', methods=['POST'])
@active_token_required
def addfunds():
    token = request.args.get('Token')
    data = jwt.decode(token, app.config['SECRET_KEY'])
    username = gettargetuserforreq(request, data)

    req_data = request.get_json()
    addamountkey = 'Amount'
    if addamountkey not in req_data:
        return jsonify({"Reason": f'Missing {addamountkey} value'}), 400

    addamount = req_data[addamountkey]
    addresult = BL.edit_user(username,add_funds=addamount)
    if addresult:
        profdict = BL.user_profile(username)
        balkey = 'funds'
        if balkey in profdict:
            userbal = profdict[balkey]
        else:
            userbal = ''
        return jsonify({"Balance": userbal}), 200
    else:
        return jsonify({"error": 'Unable to add balance'}), 400
    return


# validate input from API
def validate_machine(data):
    if "MachineType" not in data or \
            "Time_Start" not in data or \
            "Time_End" not in data:
        return False
    if type(data['MachineType']) is not str or \
            type(data['Time_Start']) is not str or \
            type(data['Time_End']) is not str:
        return False
    return True


def validate_user_register(data):
    if "Username" not in data or \
            "Password" not in data or \
            "Type" not in data or \
            "IsActive" not in data:
        return False
    if type(data["Username"]) is not str or \
            type(data["Password"]) is not str or \
            type(data["Type"]) is not str or \
            type(data["IsActive"]) is not bool:
        return False
    return True


def validate_change_username(data):
    if "Username" not in data or \
            "NewUsername" not in data:
        return False
    if type(data["Username"]) is not str or \
            type(data["NewUsername"]) is not str:
        return False
    return True


def validate_set_status(data):
    if "Username" not in data or \
            "IsActive" not in data:
        return False
    if type(data["Username"]) is not str or \
            type(data["IsActive"]) is not bool:
        return False
    return True


if __name__ == "__main__":
    app.run(debug=True)
