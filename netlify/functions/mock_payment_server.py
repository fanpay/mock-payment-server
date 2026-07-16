from __future__ import annotations

import base64
import json
import os
from typing import Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta

import jwt

_CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Authorization, partnerToken, requestId, Content-Type",
}

# JWT secret (override with env var in production)
_JWT_SECRET = os.getenv("MOCK_AUTH_SECRET", "dev-secret-change-me")
_JWT_ALGORITHM = "HS256"


def _json_response(status_code: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", **_CORS_HEADERS},
        "body": json.dumps(payload),
        "isBase64Encoded": False,
    }


def _error_response(status_code: int, code: str, message: str) -> dict[str, Any]:
    return _json_response(status_code, {"errors": [{"code": code, "message": message}]})


class APIError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def _is_valid_uuid4(value: str) -> bool:
    try:
        parsed = UUID(value)
    except ValueError:
        return False
    return parsed.version == 4


def _validate_headers(partner_token: str | None, request_id: str | None) -> str | None:
    if not partner_token or not _is_valid_uuid4(partner_token):
        raise APIError(
            400,
            "MISSING_REQUIRED_HEADER",
            "partnerToken header is required and must be a valid UUID",
        )
    if request_id is not None and not _is_valid_uuid4(request_id):
        raise APIError(
            400,
            "INVALID_HEADER",
            "requestId header must be a valid UUID",
        )
    return request_id


CUSTOMERS_RESPONSE = [
    {
        "customerId": 27573,
        "phone": "+1-8973452344",
        "city": "New York",
        "address2": "",
        "postalCode": "10022",
        "state": "NY",
        "address": "9011 1234 Block",
        "lastName": "TestOFLHM",
        "firstName": "Automation",
        "country": "US",
        "email": "DPPAutomationTestUser@gmail.com",
        "shippingAddress": {
            "state": "",
            "address": "",
            "lastName": "",
            "firstName": "",
            "email": "test@gmail.com",
            "country": "",
            "phone": "1234567890",
            "city": "",
            "address2": "",
            "postalCode": "",
        },
        "vaults": [
            {
                "vaultCreated": "2024-04-22T00:20:44.757",
                "accNickName": "Visa-Debit",
                "isActive": True,
                "paymentMethodId": "474a4400-9114-4950-957d-4da198c307ed",
                "cardType": "Mastercard",
                "maskedPan": "555555******4444",
                "expiry": "12/35",
                "token": "2632418387214444",
                "accountNumber": "",
                "routingNumber": "",
                "accountType": "Checking",
                "billingAddress": {
                    "firstName": "Jane",
                    "lastName": "Doe",
                    "address": "123 Main St",
                    "address2": "Apt 5",
                    "city": "San Francisco",
                    "state": "CA",
                    "country": "USA",
                    "postalCode": "94111",
                    "phone": "650-555-1234",
                    "email": "jane@email.com",
                },
                "subscription": [
                    {
                        "frequency": None,
                        "amount": "0",
                        "paymentDay": None,
                        "endDate": "0001-01-01T00:00:00",
                        "paymentMonth": None,
                        "startDate": "0001-01-01T00:00:00",
                        "active": False,
                        "subscriptionId": "00000000-0000-0000-0000-000000000000",
                    }
                ],
            }
        ],
    },
    {
        "customerId": 27583,
        "phone": "+1-8973452344",
        "city": "New York",
        "address2": "",
        "postalCode": "10022",
        "state": "NY",
        "address": "1922 1234 Block",
        "lastName": "TestLEEGY",
        "firstName": "Automation",
        "country": "US",
        "email": "DPPAutomationTestUser@gmail.com",
        "shippingAddress": {
            "state": "",
            "address": "",
            "lastName": "",
            "firstName": "",
            "email": "test@gmail.com",
            "country": "",
            "phone": "1234567890",
            "city": "",
            "address2": "",
            "postalCode": "",
        },
        "vaults": [],
    },
]

DEVICES_RESPONSE = {
    "devices": [
        {
            "deviceId": "4",
            "terminalName": "XUAT DESK3500",
            "deviceDisplayName": "QA D3500 GD",
            "deviceSerialNumber": "221197303251060424702233",
            "terminalStatus": "Online",
            "multiMIDSharing": "Enabled",
            "cloudStatus": "Active",
            "sharedMerchantIds": ["6289980008342010"],
            "primaryMerchantId": "6289980008342008",
        },
        {
            "deviceId": "5",
            "terminalName": "XUAT DESK3500",
            "deviceDisplayName": "QA D3500",
            "deviceSerialNumber": "221197303251060424702233",
            "terminalStatus": "Online",
            "multiMIDSharing": "Disabled",
            "cloudStatus": "Active",
            "sharedMerchantIds": [],
            "primaryMerchantId": "6289980008342008",
        },
        {
            "deviceId": "9",
            "terminalName": "QA D3500 WIFI",
            "deviceDisplayName": "QA D3500 WIFI",
            "deviceSerialNumber": "24702233",
            "terminalStatus": "Offline",
            "multiMIDSharing": "Enabled",
            "cloudStatus": "Inactive",
            "sharedMerchantIds": ["6289980008342008"],
            "primaryMerchantId": "6289980008342010",
        },
    ]
}


def _header_value(headers: dict[str, Any] | None, name: str) -> str | None:
    if not headers:
        return None
    lower_name = name.lower()
    for key, value in headers.items():
        if str(key).lower() == lower_name:
            return value
    return None


def _parse_body(event: dict[str, Any]) -> dict[str, Any]:
    body = event.get("body")
    if body is None or body == "":
        return {}
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    # If content-type is form encoded, parse into dict
    headers = event.get("headers") or {}
    content_type = _header_value(headers, "content-type") or ""
    if isinstance(body, dict):
        return body
    if "application/x-www-form-urlencoded" in content_type:
        try:
            from urllib.parse import parse_qs

            parsed = parse_qs(body)
            # parse_qs returns lists for each value
            return {k: v[0] if isinstance(v, list) and v else v for k, v in parsed.items()}
        except Exception:
            return {}
    try:
        return json.loads(body)
    except Exception:
        return {}


def _create_payment_response(payload: dict[str, Any], request_id: str | None) -> dict[str, Any]:
    payment_type = payload.get("paymentType")
    if payment_type is None:
        raise APIError(400, "MISSING_REQUIRED_FIELD", "paymentType is required")
    if payment_type not in {"Sale", "Authorization", "Recurring"}:
        raise APIError(
            400,
            "INVALID_PAYMENT_TYPE",
            "paymentType must be one of: Sale, Authorization, Recurring",
        )

    amount_obj = payload.get("amount")
    if not isinstance(amount_obj, dict) or "amount" not in amount_obj:
        raise APIError(400, "MISSING_REQUIRED_FIELD", "amount is required")

    try:
        amount_value = float(amount_obj["amount"])
    except (TypeError, ValueError):
        raise APIError(400, "INVALID_AMOUNT", "amount.amount must be a number")

    if amount_value <= 0:
        raise APIError(400, "INVALID_AMOUNT", "amount.amount must be greater than 0")

    approved = amount_value <= 9999
    return {
        "isPartial": False,
        "orderId": "Order123",
        "customerId": 4321,
        "batchNumber": 131001,
        "subscriptionId": "9a2cb7fe-119c-48ef-973e-8299246df7c2",
        "fee": {"feeAuthResponse": "APPROVED", "feeAmount": 1.99},
        "token": "1556778677451110",
        "accountResponseData": {"avs": "Y", "cvv": "Y"},
        "amountApproved": amount_value,
        "authResponse": "APPROVED" if approved else "DECLINED",
        "responseCode": 0 if approved else 51,
        "responseMessage": None,
        "paymentId": "d290f1ee-6c54-4b01-90e6-d701748f0851",
        "requestId": request_id or str(uuid4()),
        "customData": [],
    }

def _create_jwt(sub: str, expires_in: int = 3600) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)

def _verify_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return {"error": _error_response(401, "TOKEN_EXPIRED", "Access token has expired")}
    except jwt.InvalidTokenError:
        return {"error": _error_response(401, "INVALID_TOKEN", "Access token is invalid")}


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    del context

    path = event.get("path") or event.get("rawPath") or "/"
    method = str(
        event.get("httpMethod")
        or event.get("requestContext", {}).get("http", {}).get("method", "GET")
    ).upper()
    headers = event.get("headers")
    partner_token = _header_value(headers, "partnerToken")
    request_id = _header_value(headers, "requestId")
    authorization = _header_value(headers, "Authorization")

    if method == "OPTIONS":
        return {"statusCode": 200, "headers": _CORS_HEADERS, "body": ""}

    try:
        # If Authorization Bearer token is present, validate it. Otherwise require partnerToken header.
        if authorization:
            if not str(authorization).lower().startswith("bearer "):
                return _error_response(401, "INVALID_TOKEN", "Authorization header must be a Bearer token")
            token = str(authorization).split(None, 1)[1]
            verify_result = _verify_jwt(token)
            if isinstance(verify_result, dict) and verify_result.get("error"):
                return verify_result["error"]
        else:
            _validate_headers(partner_token, request_id)

        # Token issuance endpoint (client credentials demo)
        if method == "POST" and path == "/dpp/v1/auth/token":
            try:
                body = _parse_body(event)
            except json.JSONDecodeError:
                return _error_response(400, "INVALID_REQUEST", "Request body is invalid")
            client_id = body.get("clientId") or body.get("client_id")
            client_secret = body.get("clientSecret") or body.get("client_secret")
            if client_id != "demo-client" or client_secret != "demo-secret":
                return _error_response(401, "INVALID_CLIENT", "Invalid client credentials")
            token = _create_jwt(client_id)
            return _json_response(200, {"access_token": token, "token_type": "bearer", "expires_in": 3600})

        if method == "GET" and path == "/dpp/v1/customers":
            return _json_response(200, CUSTOMERS_RESPONSE)
        if method == "GET" and path == "/dpp/v1/emv/devices":
            return _json_response(200, DEVICES_RESPONSE)
        if method == "POST" and path == "/dpp/v1/payments":
            payload = _parse_body(event)
            return _json_response(200, _create_payment_response(payload, request_id))
    except APIError as exc:
        return _error_response(exc.status_code, exc.code, exc.message)
    except json.JSONDecodeError:
        return _error_response(400, "INVALID_REQUEST", "Request body is invalid")

    return _error_response(404, "ROUTE_NOT_FOUND", "Route not found")