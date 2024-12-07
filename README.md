# Temporary SSH Session Manager
A temporary SSH session manager.

## Why would you need this?
Sometimes you have apps or services you need to test. Or just commands that you want to play with and maybe have to possibility to ruin your system. Using a temporary SSH session manager you can do that without having to worry about the consequences. Powered by Docker.

## Installation

Prerequisites:
- Docker (rootless doesn't work)
- Python 3.6+
- pip

Just clone this repository
```bash
git clone https://github.com/kokofixcomputers/TemporarySSHSessionManager
```
and then install dependencies with:
```bash
pip install -r requirements.txt
``` 
In some cases you might have to install with `pip3` instead of `pip`.

then, just run with
```bash
python main.py
```
In some cases you might have to run with `python3` instead of `python`.

## Configuration
The configuration file is located at `config.json`.

Here is all the configuration keys and their description:
| Key | Description | Default Value |
| --- | ----------- | ------------- |
| `REQUIRE_AUTH` | If set to `true`, the user will be redirected to kokoauth for login. **DO NOT TURN OFF IN PRODUCTION** | `true` |
| `ALLOW_ALL_VALID_KOKOAUTH_ACCOUNTS_TO_CREATE_SESSIONS` | If set to `true`, all valid kokoauth accounts will be able to create sessions. **NOT RECOMMENDED as it allows anyone to create sessions** | `true` |
| `ALLOWED_KOKOAUTH_ACCOUNTS_EMAIL` | A list of kokoauth accounts email address that are allowed to create sessions. (ONLY IF `ALLOW_ALL_VALID_KOKOAUTH_ACCOUNTS_TO_CREATE_SESSIONS` is set to `false`) **RECOMMENDED** | `` |