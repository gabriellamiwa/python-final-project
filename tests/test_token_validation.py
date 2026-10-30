import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from flask import Flask
import jwt

import app_config
from helpers.token_validation import validate_token


class TokenValidationTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.secret_patch = patch.object(
            app_config,
            "TOKEN_SECRET",
            "unit-test-only-secret-with-more-than-32-bytes",
        )
        self.secret_patch.start()
        self.addCleanup(self.secret_patch.stop)

    def create_token(self, expiration):
        return jwt.encode(
            {"uid": "test-user", "email": "test@example.com", "exp": expiration},
            app_config.TOKEN_SECRET,
            algorithm="HS256",
        )

    def test_missing_token_returns_400(self):
        with self.app.test_request_context("/protected"):
            self.assertEqual(validate_token(), 400)

    def test_malformed_token_returns_401(self):
        with self.app.test_request_context(
            "/protected", headers={"x-access-token": "not-a-jwt"}
        ):
            self.assertEqual(validate_token(), 401)

    def test_valid_token_returns_decoded_claims(self):
        token = self.create_token(datetime.now(timezone.utc) + timedelta(minutes=5))

        with self.app.test_request_context(
            "/protected", headers={"x-access-token": token}
        ):
            claims = validate_token()

        self.assertEqual(claims["uid"], "test-user")
        self.assertEqual(claims["email"], "test@example.com")

    def test_expired_token_returns_401(self):
        token = self.create_token(datetime.now(timezone.utc) - timedelta(minutes=5))

        with self.app.test_request_context(
            "/protected", headers={"x-access-token": token}
        ):
            self.assertEqual(validate_token(), 401)


if __name__ == "__main__":
    unittest.main()
