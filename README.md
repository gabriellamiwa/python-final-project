# French Verb API

A Flask HTTP API for retrieving French verb information from an external service and saving each user's favorite verbs in MongoDB. The project also includes account registration, password-based login, and JWT-protected endpoints.

## Features

- Register accounts and authenticate with email and password. Passwords are hashed with bcrypt.
- Issue JWTs for authenticated requests. Clients send the token in the `x-access-token` header.
- Look up a French verb and request a random set of verbs through the external French Verb API.
- Add, retrieve, list, and delete a user's favorite verbs.
- Retrieve account names and email addresses through an authenticated user-list endpoint.

## Technology

- Python and Flask
- MongoDB with PyMongo
- bcrypt password hashing and PyJWT token handling
- Requests for calls to the external French Verb API

## Architecture

Flask blueprints in `views/` define HTTP routes and validate request fields. Functions in `controllers/` handle account and favorite-verb operations, using the shared MongoDB client from `database/`. `models/` contains the user and verb data objects. `helpers/` contains token validation, error messages, and the external API client.

The API uses two MongoDB collections: `users` stores account name, email, and password hash; `verbs` stores a favorite verb and its owner ID.

## Project structure

```
.
├── app.py                      # Flask application entry point
├── app_config.py               # MongoDB, JWT, and collection settings
├── controllers/                # Account and verb operations
├── database/                   # MongoDB client setup
├── helpers/                    # Token validation and external API calls
├── models/                     # User and favorite-verb models
└── views/                      # Flask API blueprints and routes
```

## Setup and run

### Requirements

- Python 3
- A MongoDB database
- Network access to the configured French Verb API

### Install

Clone the repository and create a virtual environment:

```sh
git clone https://github.com/gabriellamiwa/python-final-project.git
cd python-final-project
python -m venv .venv
```

Activate the environment and install the project dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

&nbsp;

On macOS or Linux:

```sh
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Configure services

The application reads the MongoDB connection URI, database name, collection names, JWT signing secret, and token lifetime from `app_config.py`. The external API URL and access token are defined in `helpers/external_api.py`. Use development credentials for services you control. These settings are currently stored in tracked source files, so rotate any active credentials that have already been published to GitHub. Secret values are not repeated in this README.

Start the Flask development server from the repository root:

```sh
python app.py
```

By default, Flask serves locally at `http://127.0.0.1:5000`. The root route returns `HOME`.

## API reference

Protected endpoints require the JWT returned by `POST /v0/users/login` in the `x-access-token` header. The default token lifetime is 30 days, as configured by `JWT_EXPIRATION`.

| Method and path                              | Authentication | Request body                | Purpose                                                                |
| :------------------------------------------- | :------------- | :-------------------------- | :--------------------------------------------------------------------- |
| `POST /v0/users/`                            | No             | `name`, `email`, `password` | Create an account and return its ID.                                   |
| `POST /v0/users/login`                       | No             | `email`, `password`         | Authenticate and return a JWT, expiration, and logged-in user details. |
| `GET /v0/users/`                             | Yes            | None                        | Return the user list with IDs, names, and email addresses.             |
| `GET /v0/verbs/`                             | Yes            | `verb`                      | Look up a verb through the external API.                               |
| `GET /v0/verbs/random/`                      | Yes            | `quantity`                  | Request random verbs from the external API.                            |
| `POST /v0/verbs/favorites`                   | Yes            | `verb`                      | Save a favorite verb for the authenticated user.                       |
| `GET /v0/verbs/favorites/`                   | Yes            | None                        | List the authenticated user's favorites.                               |
| `GET /v0/verbs/favorites/{favorite_uid}/`    | Yes            | None                        | Retrieve one saved favorite.                                           |
| `DELETE /v0/verbs/favorites/{favorite_uid}/` | Yes            | None                        | Delete one saved favorite.                                             |

The verb lookup and random-verb endpoints read JSON request bodies on `GET` requests in the current implementation.

### Example: look up a verb

Register an account, then log in to obtain a token. The following Python example uses the `requests` package installed above:

```py
import requests

base_url = "http://127.0.0.1:5000"
login = requests.post(
    f"{base_url}/v0/users/login",
    json={"email": "learner@example.com", "password": "your-password"},
)
token = login.json()["token"]

response = requests.get(
    f"{base_url}/v0/verbs/",
    headers={"x-access-token": token},
    json={"verb": "parler"},
)
print(response.json())
```

## Tests

Run the unit tests with Python's standard-library test runner:

```sh
python -m unittest discover -s tests -v
```

The token-validation tests cover missing, malformed, valid, and expired JWTs. They exercise the helper without connecting to MongoDB or the external verb service.
