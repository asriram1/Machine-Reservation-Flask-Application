from Classes.Users import User, Client, FacilityManager
from Classes.Reservation import Reservation
from Classes.Transaction import Transaction


def main():
    uname = 'FMTEST'
    pw = 'ABC123'

    uname2 = 'mm594'
    newuname2 = 'mm594_1'
    pw2 = 'TESTPW'

    localuser = User.login(uname, pw)

    if localuser is None:
        registersuccess = User.register(uname, pw, True, True)
        if registersuccess:
            localuser = User.login(uname, pw)

    if localuser is not None:
        print(f'Login successful.\nProfile: {localuser.getprofile()}')
        if localuser.IsFacilityManager:
            testuser = User.login(uname2, pw2)
            if testuser is None:
                newuserregistersuccess = User.register(uname2, pw2, False, True)
                if newuserregistersuccess:
                    print(f'New user registration success.\nNew user profile: {localuser.getprofile(uname2)}')
                else:
                    print(f'New user registration fail')
            else:
                # user already exists and login was successful
                print(f'New user profile: {localuser.getprofile(uname2)}')

            print(f'Client list: {localuser.getclientlist()}')
            print(f"Reservation creation result: {localuser.makeres('mm594', '2020-06-15 12:00', '2020-06-15 13:00', 'Workshop')}")
            print(f'Username change request result: {localuser.changeusername(uname2, newuname2)}')
            print(f"Client list: {localuser.searchclients(usernamepattern='mm5*', useridpattern='')}")
            print(f'Username change request result: {localuser.changeusername(newuname2, uname2)}')
            print(f"Client list: {localuser.searchclients(usernamepattern='mm5*', useridpattern='')}")
            print(f'Facility reservation list: {localuser.searchreservations()}')
            print(f'Facility transaction list: {localuser.gettranslist()}')
        else:
            print(f'Client user profile: {localuser.getprofile()}')
            print(f"Reservation creation result: {localuser.makeres('2020-06-15 14:00', '2020-06-01 15:00', 'Workshop')}")
            print(f'Client reservation list: {localuser.getreslist()}')
            print(f'Client transaction list: {localuser.gettranslist()}')

        print(f'Logout result: {localuser.logout()}, token={localuser.token}')
    else:
        print('Unable to login')
    return


if __name__ == '__main__':
    main()
