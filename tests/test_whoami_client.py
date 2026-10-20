import unittest

from app.whoami_client import build_whoami_authorization_header


class WhoAmIClientTests(unittest.TestCase):
    def test_raw_token_defaults_to_bearer(self):
        self.assertEqual(
            "Bearer abc123",
            build_whoami_authorization_header("abc123"),
        )

    def test_existing_bearer_prefix_is_preserved(self):
        self.assertEqual(
            "Bearer abc123",
            build_whoami_authorization_header("Bearer abc123"),
        )

    def test_apikey_prefix_is_preserved(self):
        self.assertEqual(
            "apikey key123",
            build_whoami_authorization_header("apikey key123"),
        )

    def test_scheme_matching_is_case_insensitive(self):
        self.assertEqual(
            "Bearer abc123",
            build_whoami_authorization_header("bearer abc123"),
        )
        self.assertEqual(
            "apikey key123",
            build_whoami_authorization_header("APIKEY key123"),
        )

    def test_empty_values_are_rejected(self):
        with self.assertRaises(ValueError):
            build_whoami_authorization_header("")
        with self.assertRaises(ValueError):
            build_whoami_authorization_header("Bearer   ")
        with self.assertRaises(ValueError):
            build_whoami_authorization_header("apikey   ")


if __name__ == "__main__":
    unittest.main()
