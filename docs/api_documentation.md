# Enterprise AI Platform API Documentation

## GET /

Description:
Returns application status.

Response

{
    "status":"running"
}

------------------------------------------------

## GET /health

Description

Returns system health.

Response

{
    "database":"connected",
    "vector_db":"connected",
    "llm":"connected"
}

------------------------------------------------

## POST /login

Description

Authenticate user.

Request

{
    "email":"admin@company.com",
    "password":"password"
}

Response

{
    "access_token":"JWT",
    "token_type":"bearer"
}

Error Codes

400
401
403
500