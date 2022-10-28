# -*- coding: utf-8 -*-

from BusinessLogic import Reservation

reservation = Reservation()


def test_add_user():
    print('Testing add_user: ', end='')
    flag = reservation.add_user('john', 'johnjohn', 'client')
    assert (flag is True)
    flag = reservation.add_user('john', 'johnjohnjohn', 'client')
    assert (flag is False)
    flag = reservation.add_user('steve', 'stevesteve', 'client')
    assert (flag is True)
    print('SUCCESS')


def test_edit_user():
    print('Testing edit_user: ', end='')
    flag = reservation.edit_user('john', new_username='newjohn')
    assert (flag is True)
    flag = reservation.edit_user('john', new_username='newjohn')
    assert (flag is False)
    flag = reservation.edit_user('newjohn', password='newjohnnewjohn')
    assert (flag is True)
    flag = reservation.edit_user('newjohn', add_funds=10, active=False)
    assert (flag is True)
    print('SUCCESS')


def test_user_search():
    print('Testing user_search: ', end='')
    ret = reservation.user_search('john')
    assert ({"username": 'newjohn',
             "funds": 10,
             "is_active": False,
             "type": 'client'} in ret)
    print('SUCCESS')


def test_user_profile():
    print('Testing user_profile: ', end='')
    ret = reservation.user_profile('john')
    assert (ret is None)
    ret = reservation.user_profile('newjohn')
    assert (ret == {'funds': 10, 'is_active': False, 'type': 'client'})
    print('SUCCESS')


def test_list_clients():
    print('Testing list_client: ', end='')
    ret = reservation.list_clients()
    print('SUCCESS')


def test_login():
    print('Testing login: ', end='')
    ret = reservation.login("steve", "stevesteve")
    assert (ret is True)
    ret = reservation.login("steve", "buscemi")
    assert (ret is False)
    print('SUCCESS')


def test_get_reservations():
    print('Testing get_reservations: ', end='')
    ret = reservation.get_reservations()
    print(ret)


def test_make_reservation():
    print('Testing make_reservation: ', end='')
    ret = reservation.make_reservation("steve", "Irradiator", "2020-6-16 12:30", "2020-6-16 15:30")
    assert (ret == (True, 1))
    ret = reservation.make_reservation("newjohn", "Irradiator", "2020-6-16 10:30", "2020-6-16 11:30")
    assert (ret == (True, 2))
    ret = reservation.make_reservation("newjohn", "Irradiator", "2020-6-16 10:30", "2020-6-16 11:30")
    assert (ret == (True, 3))
    ret = reservation.make_reservation("steve", "Irradiator", "2020-7-12 10:30", "2020-7-12 11:30")
    assert (ret == (True, 4))
    ret = reservation.make_reservation("steve", "Irradiator", "2020-6-16 10:30", "2020-6-16 11:30")
    assert (ret == (False, None))
    ret = reservation.make_reservation("newjohn", "Irradiator", "2020-6-16 10:30", "2020-6-16 11:30")
    assert (ret == (False, None))
    ret = reservation.make_reservation("NotUser", "Irradiator", "2020-6-16 10:30", "2020-6-16 11:30")
    assert (ret == (False, None))
    ret = reservation.make_reservation("newjohn", "NotMachine", "2020-6-16 10:30", "2020-6-16 11:30")
    assert (ret == (False, None))
    ret = reservation.make_reservation("newjohn", "Irradiator", "2020-6-16 13:30", "2020-6-16 15:30")
    assert (ret == (True, 5))
    print('SUCCESS')


def test_edit_reservation():
    print('Testing edit_reservation: ', end='')
    # Non-existent reservation
    ret = reservation.edit_reservation(7, "2020-6-12 10:30", "2020-6-12 12:30")
    assert (ret == (False, 0))

    # Less than 2 days notice, decrease of 50%, no refund
    ret = reservation.edit_reservation(3, "2020-6-12 10:30", "2020-6-12 11:00")
    assert (ret == (True, -0.0))

    # Less than 2 weeks in advance, add 1 hour, full price
    ret = reservation.edit_reservation(3, "2020-6-12 10:30", "2020-6-12 12:00")
    assert (ret == (True, 2200.0))

    # Greater than 2 weeks, add 30 min, 25% discount
    ret = reservation.edit_reservation(3, "2020-7-12 10:30", "2020-7-12 12:30")
    assert (ret == (True, 825.0))

    # Greater than 7 days notice, decrease of 50%, 75% refund (on 50% of balance)
    ret = reservation.edit_reservation(3, "2020-7-12 10:30", "2020-7-12 11:30")
    assert (ret == (True, -1959.375))

    # No change in duration, no cost
    ret = reservation.edit_reservation(3, "2020-6-17 10:30", "2020-6-17 11:30")
    assert (ret == (True, 0))

    # Greater than 2 days notice, decrease of 50%, 50% refund (on 50% of balance)
    ret = reservation.edit_reservation(3, "2020-6-17 10:30", "2020-6-17 11:00")
    assert (ret == (True, -0.0))
    print('SUCCESS')


def test_get_transactions(full=False):
    ret = reservation.get_transactions()
    print(ret)
    if full:
        ret = reservation.get_transactions(reservation_id=1)
        print(ret)
        ret = reservation.get_transactions(username="newjohn")
        print(ret)
        ret = reservation.get_transactions(start_datetime="2020-06-10 10:30")
        print(ret)
        ret = reservation.get_transactions(end_datetime="2020-12-10 10:30")
        print(ret)
        ret = reservation.get_transactions(transaction_type='make')
        print(ret)
        ret = reservation.get_transactions(transaction_type='edit')
        print(ret)
        ret = reservation.get_transactions(transaction_type='cancel')
        print(ret)


def test_cancel_reservation():
    print('Testing cancel_reservation: ', end='')
    ret = reservation.cancel_reservation(1)
    assert (ret == (True, 0))
    ret = reservation.cancel_reservation(8)
    assert (ret == (False, 0))
    ret = reservation.cancel_reservation(4)
    assert (ret == (True, 1237.5))
    ret = reservation.cancel_reservation(5)
    assert (ret == (True, 0))
    print("SUCCESS")


def test_reset_db():
    print('Testing reset_db: ', end='')
    flag = reservation.add_user('john', 'johnjohn', 'client')
    assert (flag is True)
    flag = reservation.add_user('john', 'johnjohnjohn', 'client')
    assert (flag is False)
    reservation.reset_db()
    flag = reservation.add_user('john', 'johnjohnjohn', 'client')
    assert (flag is True)
    print('SUCCESS')


reservation.reset_db()
test_add_user()
test_edit_user()
test_user_profile()
test_user_search()
test_list_clients()
test_login()
test_get_reservations()
test_get_transactions()
test_make_reservation()
test_get_reservations()
test_get_transactions()
test_edit_reservation()
test_get_reservations()
test_get_transactions(True)
test_cancel_reservation()
test_get_transactions(True)
test_reset_db()
