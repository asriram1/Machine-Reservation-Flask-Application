import datetime

from Database import Database

time_format = '%Y-%m-%d %H:%M'


def check_datetime(datetime_to_check):
    try:
        valid_datetime = datetime.datetime.strptime(datetime_to_check, time_format)
        if valid_datetime.minute == 30 or valid_datetime.minute == 0:
            return valid_datetime
        else:
            return None
    except ValueError:
        return None


def check_start_datetime(start_datetime):
    start = check_datetime(start_datetime)
    if not start or (start - datetime.datetime.now()).days > 30:
        return False
    else:
        return start


def working_days_in_range(start_date, end_date):
    # https://stackoverflow.com/questions/3615375/count-number-of-days-between-dates-ignoring-weekends/32698089#32698089
    from_weekday = start_date.weekday()
    to_weekday = end_date.weekday()
    # If start date is after Friday, modify it to Monday
    if from_weekday > 4:
        from_weekday = 0
    day_diff = to_weekday - from_weekday
    whole_weeks = ((end_date - start_date).days - day_diff) / 7
    workdays_in_whole_weeks = whole_weeks * 5
    beginning_end_correction = min(day_diff, 5) - (max(to_weekday - 4, 0) % 5)
    working_days = workdays_in_whole_weeks + beginning_end_correction
    # Final sanity check (i.e. if the entire range is weekends)
    return int(max(0, working_days))


class Reservation:
    def __init__(self):
        self.__DB = Database()

    def reset_db(self):
        self.__DB.reset_db()

    def get_user_id(self, username):
        return self.__DB.get_user_id(username)

    def add_user(self, username, password, user_type):
        return self.__DB.create_user(username, password, user_type)

    def edit_user(self, username, new_username=None, password=None, add_funds=None, active=None):
        return self.__DB.edit_user(username, new_username, password, add_funds, active)

    def login(self, username, password):
        return self.__DB.grant_access(username, password)

    def user_profile(self, username):
        ret = self.__DB.get_info(username)
        if not ret:
            return None
        else:
            ret.pop('password')
            return ret

    def user_search(self, partial_username):
        return self.__DB.search_client(partial_username)

    def list_clients(self):
        return self.__DB.list_clients()

    def get_price(self, machine, start_datetime, end_datetime, duration=None):
        now = datetime.datetime.now()
        cost = self.__DB.get_cost(machine)

        if duration:
            length = (end_datetime - start_datetime).total_seconds() / 3600 - duration
        else:
            length = (end_datetime - start_datetime).total_seconds() / 3600

        if (start_datetime - now).days > 14:
            return cost * length * .75
        else:
            return cost * length

    def get_refund(self, reservation_id, new_duration=None):
        # Existence of the reservation is always checked before this function is called
        now = datetime.datetime.now()

        reservation_details = self.get_reservations(reservation_id)[0]
        previous_payment = reservation_details['price']

        original_end = datetime.datetime.strptime(reservation_details['end_datetime'], time_format)
        original_start = datetime.datetime.strptime(reservation_details['start_datetime'], time_format)
        original_duration = (original_end - original_start).total_seconds() / 3600

        days_notice = working_days_in_range(now, original_start)

        if new_duration:
            refund_proportion = (original_duration - new_duration) / original_duration
        else:
            refund_proportion = 1

        if days_notice >= 7:
            refund_rate = .75
        elif days_notice >= 2:
            refund_rate = .5
        else:
            refund_rate = 0

        return previous_payment * refund_proportion * refund_rate

    def make_reservation(self, username, machine, start_datetime_str, end_datetime_str):
        start = check_start_datetime(start_datetime_str)
        end = check_datetime(end_datetime_str)
        machine_id = self.__DB.find_available_machine(machine, start_datetime_str, end_datetime_str)

        if start and end and machine_id and self.__DB.get_user_id(username):
            price = self.get_price(machine, start, end)
            reservation_id = self.__DB.add_reservation(start_datetime_str, end_datetime_str, price, True, machine_id,
                                                       username)
            self.__DB.add_transaction(price, 'make', reservation_id, username)
            success = True
        else:
            success = False
            reservation_id = None

        return success, reservation_id

    def edit_reservation(self, reservation_id, start_datetime_str, end_datetime_str):
        success = False
        payment = 0  # Positive means Mad Science should receive payment, negative means they should refund payment
        existing_reservation = self.get_reservations(reservation_id)
        start = check_start_datetime(start_datetime_str)
        end = check_datetime(end_datetime_str)

        if start and end and existing_reservation:
            existing_reservation = existing_reservation[0]
            username = self.__DB.get_username(existing_reservation['user_id'])
            existing_reservation.pop('user_id')
            existing_reservation['username'] = username
            success = True
        else:
            return success, payment

        original_end = datetime.datetime.strptime(existing_reservation['end_datetime'], time_format)
        original_start = datetime.datetime.strptime(existing_reservation['start_datetime'], time_format)
        original_duration = (original_end - original_start).total_seconds() / 3600

        end_datetime = datetime.datetime.strptime(end_datetime_str, time_format)
        start_datetime = datetime.datetime.strptime(start_datetime_str, time_format)
        new_duration = (end_datetime - start_datetime).total_seconds() / 3600

        if new_duration < original_duration:
            payment = - self.get_refund(reservation_id, new_duration)
            price = existing_reservation['price']
            new_price = price + payment
            self.__DB.edit_reservation(reservation_id, start_datetime_str, end_datetime_str, new_price)
            self.__DB.add_transaction(- payment, 'edit', reservation_id, username)
            success = True
        elif new_duration > original_duration:
            payment = self.get_price(existing_reservation['machine_type'], start_datetime, end_datetime,
                                     original_duration)
            price = existing_reservation['price']
            new_price = price + payment
            self.__DB.edit_reservation(reservation_id, start_datetime_str, end_datetime_str, new_price)
            self.__DB.add_transaction(payment, 'edit', reservation_id, username)
        else:
            payment = 0
            self.__DB.edit_reservation(reservation_id, start_datetime_str, end_datetime_str)
            self.__DB.add_transaction(payment, 'edit', reservation_id, username)
            success = True

        return success, payment

    def cancel_reservation(self, reservation_id):
        existing_reservation = self.get_reservations(reservation_id)
        if existing_reservation:
            refund = self.get_refund(reservation_id)
            username = self.__DB.get_username(existing_reservation[0]['user_id'])
            self.__DB.add_transaction(- refund, 'edit', reservation_id, username)
            return True, refund
        else:
            return False, 0

    def get_reservations(self, reservation_id=None, username=None, start_datetime=None, end_datetime=None, status=None,
                         machine=None):
        reservations = self.__DB.reservation_details(reservation_id, start_datetime, end_datetime, status, machine,
                                                     username)
        for reservation in reservations:
            username = self.__DB.get_username(reservation.pop('user_id'))
            reservation['username'] = username
            machine = reservation.pop('machine_type')
            reservation['machine'] = machine
        return reservations

    def get_transactions(self, transaction_id=None, reservation_id=None, username=None, start_datetime=None,
                         end_datetime=None, transaction_type=None):
        transactions = self.__DB.transaction_details(transaction_id, transaction_type, reservation_id, username,
                                                     start_datetime, end_datetime)
        for transaction in transactions:
            username = self.__DB.get_username(transaction.pop('user_id'))
            transaction['username'] = username

        return transactions
