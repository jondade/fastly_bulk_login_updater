# fastly_bulk_login_updater
A tool to mass update user's logins to the Fastly management portal.

## Requirements
Python 3.x
Modules:
* Requests

## Usage
Clone or download this repository. Run `bulk_name_change.py` with arguments to update names.

## Arguments
* -h --help
	Display the help information
* -D --debug
	Output very verbose debugging information.
* -t --token [token]
	An API token from a superuser on the account.
* -f --file [filename]
	The name of the CSV file to read old and new login names from. See `example.csv` for the format.
