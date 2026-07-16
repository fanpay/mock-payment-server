const { randomUUID } = require("crypto");

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "partnerToken, requestId, Content-Type",
};

function jsonResponse(statusCode, payload) {
  return {
    statusCode,
    headers: { "Content-Type": "application/json", ...CORS_HEADERS },
    body: JSON.stringify(payload),
  };
}

function errorResponse(statusCode, code, message) {
  return jsonResponse(statusCode, { errors: [{ code, message }] });
}

function isValidUUID4(value) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value);
}

function getHeader(headers, name) {
  if (!headers) return null;
  const lower = name.toLowerCase();
  const key = Object.keys(headers).find((k) => k.toLowerCase() === lower);
  return key ? headers[key] : null;
}

function validateHeaders(partnerToken, requestId) {
  if (!partnerToken || !isValidUUID4(partnerToken)) {
    return errorResponse(400, "MISSING_REQUIRED_HEADER", "partnerToken header is required and must be a valid UUID");
  }
  if (requestId !== null && requestId !== undefined && !isValidUUID4(requestId)) {
    return errorResponse(400, "INVALID_HEADER", "requestId header must be a valid UUID");
  }
  return null;
}

const CUSTOMERS_RESPONSE = [
  {
    customerId: 27573,
    phone: "+1-8973452344",
    city: "New York",
    address2: "",
    postalCode: "10022",
    state: "NY",
    address: "9011 1234 Block",
    lastName: "TestOFLHM",
    firstName: "Automation",
    country: "US",
    email: "DPPAutomationTestUser@gmail.com",
    shippingAddress: {
      state: "", address: "", lastName: "", firstName: "",
      email: "test@gmail.com", country: "", phone: "1234567890",
      city: "", address2: "", postalCode: "",
    },
    vaults: [
      {
        vaultCreated: "2024-04-22T00:20:44.757",
        accNickName: "Visa-Debit",
        isActive: true,
        paymentMethodId: "474a4400-9114-4950-957d-4da198c307ed",
        cardType: "Mastercard",
        maskedPan: "555555******4444",
        expiry: "12/35",
        token: "2632418387214444",
        accountNumber: "",
        routingNumber: "",
        accountType: "Checking",
        billingAddress: {
          firstName: "Jane", lastName: "Doe", address: "123 Main St",
          address2: "Apt 5", city: "San Francisco", state: "CA",
          country: "USA", postalCode: "94111", phone: "650-555-1234",
          email: "jane@email.com",
        },
        subscription: [
          {
            frequency: null, amount: "0", paymentDay: null,
            endDate: "0001-01-01T00:00:00", paymentMonth: null,
            startDate: "0001-01-01T00:00:00", active: false,
            subscriptionId: "00000000-0000-0000-0000-000000000000",
          },
        ],
      },
    ],
  },
  {
    customerId: 27583,
    phone: "+1-8973452344",
    city: "New York",
    address2: "",
    postalCode: "10022",
    state: "NY",
    address: "1922 1234 Block",
    lastName: "TestLEEGY",
    firstName: "Automation",
    country: "US",
    email: "DPPAutomationTestUser@gmail.com",
    shippingAddress: {
      state: "", address: "", lastName: "", firstName: "",
      email: "test@gmail.com", country: "", phone: "1234567890",
      city: "", address2: "", postalCode: "",
    },
    vaults: [],
  },
];

const DEVICES_RESPONSE = {
  devices: [
    {
      deviceId: "4",
      terminalName: "XUAT DESK3500",
      deviceDisplayName: "QA D3500 GD",
      deviceSerialNumber: "221197303251060424702233",
      terminalStatus: "Online",
      multiMIDSharing: "Enabled",
      cloudStatus: "Active",
      sharedMerchantIds: ["6289980008342010"],
      primaryMerchantId: "6289980008342008",
    },
    {
      deviceId: "5",
      terminalName: "XUAT DESK3500",
      deviceDisplayName: "QA D3500",
      deviceSerialNumber: "221197303251060424702233",
      terminalStatus: "Online",
      multiMIDSharing: "Disabled",
      cloudStatus: "Active",
      sharedMerchantIds: [],
      primaryMerchantId: "6289980008342008",
    },
    {
      deviceId: "9",
      terminalName: "QA D3500 WIFI",
      deviceDisplayName: "QA D3500 WIFI",
      deviceSerialNumber: "24702233",
      terminalStatus: "Offline",
      multiMIDSharing: "Enabled",
      cloudStatus: "Inactive",
      sharedMerchantIds: ["6289980008342008"],
      primaryMerchantId: "6289980008342010",
    },
  ],
};

function handlePayments(body, requestId) {
  const { paymentType, amount } = body;

  if (!paymentType) {
    return errorResponse(400, "MISSING_REQUIRED_FIELD", "paymentType is required");
  }
  if (!["Sale", "Authorization", "Recurring"].includes(paymentType)) {
    return errorResponse(400, "INVALID_PAYMENT_TYPE", "paymentType must be one of: Sale, Authorization, Recurring");
  }
  if (!amount || typeof amount !== "object" || !("amount" in amount)) {
    return errorResponse(400, "MISSING_REQUIRED_FIELD", "amount is required");
  }

  const amountValue = parseFloat(amount.amount);
  if (isNaN(amountValue)) {
    return errorResponse(400, "INVALID_AMOUNT", "amount.amount must be a number");
  }
  if (amountValue <= 0) {
    return errorResponse(400, "INVALID_AMOUNT", "amount.amount must be greater than 0");
  }

  const approved = amountValue <= 9999;
  return jsonResponse(200, {
    isPartial: false,
    orderId: "Order123",
    customerId: 4321,
    batchNumber: 131001,
    subscriptionId: "9a2cb7fe-119c-48ef-973e-8299246df7c2",
    fee: { feeAuthResponse: "APPROVED", feeAmount: 1.99 },
    token: "1556778677451110",
    accountResponseData: { avs: "Y", cvv: "Y" },
    amountApproved: amountValue,
    authResponse: approved ? "APPROVED" : "DECLINED",
    responseCode: approved ? 0 : 51,
    responseMessage: null,
    paymentId: "d290f1ee-6c54-4b01-90e6-d701748f0851",
    requestId: requestId || randomUUID(),
    customData: [],
  });
}

exports.handler = async (event) => {
  const method = (event.httpMethod || "GET").toUpperCase();

  if (method === "OPTIONS") {
    return { statusCode: 200, headers: CORS_HEADERS, body: "" };
  }

  const path = event.path || "/";
  const headers = event.headers || {};
  const partnerToken = getHeader(headers, "partnerToken");
  const requestId = getHeader(headers, "requestId");

  const headerError = validateHeaders(partnerToken, requestId);
  if (headerError) return headerError;

  if (method === "GET" && path === "/dpp/v1/customers") {
    return jsonResponse(200, CUSTOMERS_RESPONSE);
  }

  if (method === "GET" && path === "/dpp/v1/emv/devices") {
    return jsonResponse(200, DEVICES_RESPONSE);
  }

  if (method === "POST" && path === "/dpp/v1/payments") {
    let body = {};
    try {
      body = event.body ? JSON.parse(event.body) : {};
    } catch {
      return errorResponse(400, "INVALID_REQUEST", "Request body is invalid");
    }
    return handlePayments(body, requestId);
  }

  return errorResponse(404, "ROUTE_NOT_FOUND", "Route not found");
};
