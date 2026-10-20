import unittest

from app.auth_logic import authorize_service_user, authorize_user
from app.models import WhoAmIResponse
from app.settings import (
    API_SERVICE_PASSWORD,
    API_SERVICE_SUBSCRIBE_SUBJECTS,
    API_SERVICE_USERNAME,
    FLAIR_SERVICE_PUBLISH_SUBJECTS,
    FLAIR_SERVICE_USERNAME,
    FLAIR_SERVICE_SUBSCRIBE_SUBJECTS,
    NATS_FLAIR_JOB_SUBJECT,
    NATS_FLAIR_REGEX_SUBJECT,
    NATS_IRELEMENT_SUBJECT,
    NATS_NOTIFICATION_BROADCAST_SUBJECT,
    NATS_NOTIFICATION_SUBJECT,
    NATS_SUBJECT_ROOT,
)


class AuthLogicTests(unittest.TestCase):
    def test_active_end_user_is_granted_read_access(self):
        decision = authorize_user(
            WhoAmIResponse(username="alice", is_active=True, id=123)
        )
        self.assertTrue(decision.allow)
        self.assertEqual([], decision.publish)
        self.assertEqual(
            [
                NATS_IRELEMENT_SUBJECT,
                f"{NATS_SUBJECT_ROOT}.notification.user.123.>",
                NATS_NOTIFICATION_BROADCAST_SUBJECT,
            ],
            decision.subscribe,
        )
        self.assertIn("scot.irelement.>", decision.subscribe)
        self.assertIn("scot.notification.user.123.>", decision.subscribe)
        self.assertIn("scot.notification.broadcast.>", decision.subscribe)
        self.assertNotIn("scot.notification.user.456.>", decision.subscribe)
        self.assertNotIn(NATS_FLAIR_JOB_SUBJECT, decision.publish)
        self.assertNotIn(NATS_FLAIR_JOB_SUBJECT, decision.subscribe)
        self.assertNotIn("scot.>", decision.subscribe)

    def test_inactive_end_user_is_denied(self):
        decision = authorize_user(
            WhoAmIResponse(username="alice", is_active=False, id=1)
        )
        self.assertFalse(decision.allow)
        self.assertEqual("inactive_user", decision.reason)

    def test_unknown_service_user_is_not_recognized(self):
        self.assertIsNone(authorize_service_user("unknown", "secret"))

    def test_known_service_user_with_wrong_password_is_denied(self):
        decision = authorize_service_user(API_SERVICE_USERNAME, "wrong")
        self.assertIsNotNone(decision)
        self.assertFalse(decision.allow)
        self.assertEqual("invalid_service_password", decision.reason)

    def test_known_service_user_with_expected_password_is_allowed(self):
        if not API_SERVICE_PASSWORD:
            self.skipTest("API_SERVICE_PASSWORD not set in test environment")
        decision = authorize_service_user(API_SERVICE_USERNAME, API_SERVICE_PASSWORD)
        self.assertIsNotNone(decision)
        self.assertTrue(decision.allow)
        self.assertEqual(API_SERVICE_USERNAME, decision.username)

    def test_api_service_default_subscribe_subjects_include_notifications(self):
        self.assertIn(NATS_IRELEMENT_SUBJECT, API_SERVICE_SUBSCRIBE_SUBJECTS)
        self.assertIn(NATS_NOTIFICATION_SUBJECT, API_SERVICE_SUBSCRIBE_SUBJECTS)

    def test_api_service_default_publish_subjects_include_flair_regex(self):
        from app.settings import API_SERVICE_PUBLISH_SUBJECTS

        self.assertIn(NATS_FLAIR_REGEX_SUBJECT, API_SERVICE_PUBLISH_SUBJECTS)

    def test_flair_jobs_subject_defaults(self):
        from app.settings import API_SERVICE_PUBLISH_SUBJECTS

        self.assertEqual("scot.flair.job.>", NATS_FLAIR_JOB_SUBJECT)
        self.assertIn(NATS_FLAIR_JOB_SUBJECT, API_SERVICE_PUBLISH_SUBJECTS)
        self.assertIn(NATS_FLAIR_JOB_SUBJECT, FLAIR_SERVICE_SUBSCRIBE_SUBJECTS)
        self.assertNotIn(NATS_FLAIR_JOB_SUBJECT, FLAIR_SERVICE_PUBLISH_SUBJECTS)
        self.assertEqual([], FLAIR_SERVICE_PUBLISH_SUBJECTS)

    def test_flair_service_default_subscribe_subjects_include_flair_regex(self):
        self.assertIn(NATS_FLAIR_REGEX_SUBJECT, FLAIR_SERVICE_SUBSCRIBE_SUBJECTS)

    def test_flair_service_identity_is_supported(self):
        decision = authorize_service_user(FLAIR_SERVICE_USERNAME, "wrong")
        self.assertIsNotNone(decision)
        self.assertFalse(decision.allow)
        self.assertEqual("invalid_service_password", decision.reason)


if __name__ == "__main__":
    unittest.main()
