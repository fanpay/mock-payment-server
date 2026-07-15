import unittest

from fastapi.testclient import TestClient

from app.main import app


class MockPaymentServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.headers = {"partnerToken": "550e8400-e29b-41d4-a716-446655440000"}

    def test_missing_partner_token_returns_400(self) -> None:
        response = self.client.get("/dpp/v1/customers")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["errors"][0]["code"], "MISSING_REQUIRED_HEADER")

    def test_get_devices_success(self) -> None:
        response = self.client.get("/dpp/v1/emv/devices", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("devices", response.json())
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")

    def test_payments_declined_over_limit(self) -> None:
        body = {
            "paymentType": "Sale",
            "amount": {"amount": 10000, "currency": "USD"},
            "paymentMethod": {
                "card": {"card": "4111111111111110", "expiry": "11/26", "cvv": "245"}
            },
        }
        response = self.client.post("/dpp/v1/payments", headers=self.headers, json=body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["authResponse"], "DECLINED")
        self.assertEqual(response.json()["responseCode"], 51)

    def test_undefined_route_returns_standard_error(self) -> None:
        response = self.client.get("/not-found", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["errors"][0]["code"], "ROUTE_NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
