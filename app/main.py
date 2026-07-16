from typing import Any
from uuid import UUID, uuid4
import os
from datetime import datetime, timedelta

import jwt
import uvicorn
from fastapi import Body, FastAPI, Header, Request, Form
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


app = FastAPI()

# JWT secret for demo tokens (override with env var in production)
_JWT_SECRET = os.getenv("MOCK_AUTH_SECRET", "dev-secret-change-me")
_JWT_ALGORITHM = "HS256"

# Allow Authorization header for browser-based Try-it flows
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "partnerToken", "requestId", "Content-Type"],
)


class APIError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"errors": [{"code": code, "message": message}]},
    )


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


def _create_jwt(sub: str, expires_in: int = 3600) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)


def _verify_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise APIError(401, "TOKEN_EXPIRED", "Access token has expired")
    except jwt.InvalidTokenError:
        raise APIError(401, "INVALID_TOKEN", "Access token is invalid")


def _validate_auth(partner_token: str | None, authorization: str | None, request_id: str | None) -> str | None:
    # If Authorization header provided, accept Bearer JWT tokens instead of partnerToken
    if authorization:
        if not authorization.lower().startswith("bearer "):
            raise APIError(401, "INVALID_TOKEN", "Authorization header must be a Bearer token")
        token = authorization.split(None, 1)[1]
        _verify_jwt_token(token)
        if request_id is not None and not _is_valid_uuid4(request_id):
            raise APIError(400, "INVALID_HEADER", "requestId header must be a valid UUID")
        return request_id
    # fallback to original header validation
    return _validate_headers(partner_token, request_id)


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


@app.middleware("http")
async def log_and_set_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    print(
        f"{request.method} {request.url.path} headers={dict(request.headers)} status={response.status_code}"
    )
    return response


@app.exception_handler(APIError)
async def api_error_handler(_: Request, exc: APIError):
    return _error_response(exc.status_code, exc.code, exc.message)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(_: Request, __: RequestValidationError):
    return _error_response(400, "INVALID_REQUEST", "Request body is invalid")


@app.exception_handler(StarletteHTTPException)
async def not_found_handler(_: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return _error_response(404, "ROUTE_NOT_FOUND", "Route not found")
    return _error_response(exc.status_code, "HTTP_ERROR", str(exc.detail))


@app.get("/dpp/v1/customers")
async def get_customers(
    partner_token: str | None = Header(None, alias="partnerToken"),
    request_id: str | None = Header(None, alias="requestId"),
    authorization: str | None = Header(None, alias="Authorization"),
):
    _validate_auth(partner_token, authorization, request_id)
    return JSONResponse(content=CUSTOMERS_RESPONSE)


@app.get("/dpp/v1/emv/devices")
async def get_devices(
    partner_token: str | None = Header(None, alias="partnerToken"),
    request_id: str | None = Header(None, alias="requestId"),
    authorization: str | None = Header(None, alias="Authorization"),
):
    _validate_auth(partner_token, authorization, request_id)
    return JSONResponse(content=DEVICES_RESPONSE)


@app.post("/dpp/v1/payments")
async def post_payments(
    payload: dict[str, Any] = Body(...),
    partner_token: str | None = Header(None, alias="partnerToken"),
    request_id: str | None = Header(None, alias="requestId"),
    authorization: str | None = Header(None, alias="Authorization"),
):
    request_id = _validate_auth(partner_token, authorization, request_id)

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
    response_body = {
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
    return JSONResponse(content=response_body)


@app.post("/dpp/v1/auth/token")
async def auth_token(request: Request, client_id: str | None = Form(None), client_secret: str | None = Form(None), body: dict | None = Body(None)):
    # Accept both form-encoded (OAuth2) and JSON bodies for demo client-credentials
    data = {}
    if client_id or client_secret:
        data["clientId"] = client_id
        data["clientSecret"] = client_secret
    if body:
        data.update(body)
    client_id = data.get("clientId") or data.get("client_id")
    client_secret = data.get("clientSecret") or data.get("client_secret")
    if client_id != "demo-client" or client_secret != "demo-secret":
        raise APIError(401, "INVALID_CLIENT", "Invalid client credentials")
    token = _create_jwt(client_id)
    return JSONResponse(content={"access_token": token, "token_type": "bearer", "expires_in": 3600})


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=4010, reload=False)
