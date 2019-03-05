import sys
import argparse
import requests
import csv
import getpass

parser = argparse.ArgumentParser(prog='fastly_bulk_login_update')
parser.add_argument('-D', '--debug', help='Turn on debugging information.', action='store_true')
parser.add_argument('-t', '--token', help='Fastly API token')
parser.add_argument('-p', '--password', help='Your fastly password. If not supplied it will be requested')
parser.add_argument('-c', '--csv', help='CSV file containing old_login,newlogin. One per line. Comma separated')
args = parser.parse_args()

try:
    password = None
    # Check we've got the credentials or there's no point continuing.
    if args.password == None:
        args.password = getpass.getpass(prompt="Please enter your Fastly password: ")
    if args.token == None:
        raise Exception("Authentication credentials missing. Run with '-h' option to see help")
    if args.csv == None:
        raise Exception("No csv file provided. Run with '-h' to see help")
    if args.debug:
        print("\n\nCredentials:")
        print("Token: " + args.token)
        print("Password: " + args.password)
        print("CSV file: " + args.csv)
except GetPassWarning as err:
    print(err)
    sys.exit(1)
except Exception as err:
    print(err)
    sys.exit(1)

try:
    # Create a store of old to new names
    addresses = dict()
    # Read them from the csv file
    with open(args.csv, 'r', newline = '') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            addresses[row[0]] = row[1]
    csvfile.close()
    if args.debug:
        print("\n\nAddresses:")
        for address in addresses:
            print("\t" + address + " => " + addresses[address])
except OSError as err:
    print("Could not open " + args.csv + ": " + err.strerror)
    sys.exit(1)

# get a list of users to map to ids
users_resp = requests.get('https://api.fastly.com/users',
                          headers = {'Fastly-key': args.token,
                                     'Accept': 'application/json'})
users = users_resp.json()
if args.debug:
    print('\n\nUsers:')
    print(users)

# Extract the login to id map
ids = dict()
for user in users:
    ids[user['login']] = user['id']
if args.debug:
    print('\n\nIDs:')
    for login,id in ids.items():
        print(login + " => " + id)

# Create a store for errors
errors = dict()

# Now lets try moving those users...
for old,new in addresses.items():
    print("Moving: %s to %s ... " % (old, new), end="")
    try:
        if old not in ids:
            raise Exception("Login id " + old + " not found.")
        # Set up the parts of the request
        api_data = {'login': new, 'password_confirmation': args.password}
        api_headers = {'Fastly-key': args.token, 'Accept': 'application/json'}
        api_url = "https://api.fastly.com/user/{0}".format(ids[old])
        # Send off that request and see if we're good
        resp = requests.put(api_url, headers=api_headers, data=api_data)
        if args.debug:
            print("\n\n\nRequest (" + old + ")")
            print(resp.request.url)
            print(resp.request.headers)
            print(resp.request.body)
            print("\n\n")
        resp.raise_for_status()
        print("Success.")
    except requests.exceptions.HTTPError as err:
        print("Failed")
        errors[old] = err
    except Exception as err:
        print("Failed")
        errors[old] = err

# Well if we had any problems lets tell folks...
if len(errors) > 0:
    print("\nErrors:")
    for login,error in errors.items():
        print("\tUser %s failed to update with the reason '%s'" % (login, error))
