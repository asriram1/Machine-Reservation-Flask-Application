from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

class SignUpForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    typekey = StringField('Type (input 1 for facility manager 0 for client)')
    isactive = StringField('IsActive (1 for yes, 0 for no)?')
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Log In')

class ReservationCreate(FlaskForm):
    stimekey = StringField('Time Start')
    etimekey = StringField('Time End')
    machineidkey = StringField('MachineID')
    submit = SubmitField('Create Reservation')

class ShowReservations(FlaskForm):
    stimekey = StringField('Time Start')
    etimekey = StringField('Time End')
    machineidkey = StringField('MachineID')
    submit = SubmitField('Show Reservations')


class EditReservations(FlaskForm):
    reservationid = StringField('Reservation ID (Try 1)')
    stimekey = StringField('New Start Time')
    etimekey = StringField('New End Time')
    #machineidkey = StringField('New MachineID')
    submit = SubmitField('Edit Reservation')

class CancelReservations(FlaskForm):
    reservationid = StringField('Reservation ID (Try 1)')
    submit = SubmitField('Cancel Reservation')

class AddFunds(FlaskForm):
    funds = StringField('How much do you want to add? ')
    submit = SubmitField('Add Funds')

class ListTransactions(FlaskForm):
    stimekey = StringField('Time Start')
    etimekey = StringField('Time End')
    submit = SubmitField('List Transactions')

class EditProfile(FlaskForm):
    newusername = StringField('Enter new username')
    submit = SubmitField('Edit Profile')

class FMLogin(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Log In')

class ReservationSearch(FlaskForm):
    username = StringField('Client Username')
    stimekey = StringField('Start Time')
    etimekey = StringField('End Time')
    machineid = StringField('MachineID')
    submit = SubmitField('Search Reservations')

class ClientListSearch(FlaskForm):
    unamepatternkey = StringField('Enter Username Pattern')
    uidpatternkey = StringField('Enter User ID Pattern')
    submit = SubmitField('Search Clients')

class CalculateCost(FlaskForm):
    machineidkey = StringField('Enter MachineID')
    stimekey = StringField('Enter StartTime')
    etimekey = StringField('Enter EndTime')
    submit = SubmitField('Get Cost')



