import unittest

from app.callout_service import _user_data
from app.models import AuthDecision
from nats_callout.encoder import AdaptixEncoder


class UserDataTests(unittest.TestCase):
    def test_empty_publish_allow_list_is_explicitly_denied(self):
        user_data = _user_data(
            AuthDecision(
                allow=True,
                publish=[],
                subscribe=["scot.irelement.>"],
            )
        )

        self.assertEqual([], user_data.pub.allow)
        self.assertEqual([">"], user_data.pub.deny)
        self.assertEqual(["scot.irelement.>"], user_data.sub.allow)
        self.assertEqual([], user_data.sub.deny)

        serialized = AdaptixEncoder()._dump_data(user_data)
        self.assertEqual({"allow": [], "deny": [">"]}, serialized["pub"])

    def test_empty_subscribe_allow_list_is_explicitly_denied(self):
        user_data = _user_data(
            AuthDecision(
                allow=True,
                publish=["scot.notification.>"],
                subscribe=[],
            )
        )

        self.assertEqual(["scot.notification.>"], user_data.pub.allow)
        self.assertEqual([], user_data.pub.deny)
        self.assertEqual([], user_data.sub.allow)
        self.assertEqual([">"], user_data.sub.deny)


if __name__ == "__main__":
    unittest.main()
