"""
Swagger/OpenAPI docs definitions for Flask routes.
Keeping specs here keeps app.py focused on request handling.
"""

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "UNSDG Classifier API",
        "description": "API docs for SDG classification routes.",
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["http", "https"],
}

HELLO_DOC = {
    "tags": ["Health"],
    "responses": {
        200: {
            "description": "API is alive",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Hello, World!"}
                },
            },
        }
    },
}

CLASSIFY_AURORA_DOC = {
    "tags": ["Classification"],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["projectDescription"],
                "properties": {
                    "projectName": {"type": "string", "example": "My Project"},
                    "projectUrl": {
                        "type": "string",
                        "example": "https://github.com/org/repo",
                    },
                    "projectDescription": {
                        "type": "string",
                        "example": "AI tool for clean energy monitoring.",
                    },
                },
            },
        }
    ],
    "responses": {
        200: {"description": "SDG predictions"},
        400: {"description": "Missing projectDescription"},
        500: {"description": "Classification failed"},
    },
}

CLASSIFY_ST_DESCRIPTION_DOC = {
    "tags": ["Classification"],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["projectDescription"],
                "properties": {
                    "projectName": {"type": "string", "example": "My Project"},
                    "projectUrl": {
                        "type": "string",
                        "example": "https://github.com/org/repo",
                    },
                    "projectDescription": {
                        "type": "string",
                        "example": "Open source project for digital education.",
                    },
                },
            },
        }
    ],
    "responses": {
        200: {"description": "SDG predictions"},
        400: {"description": "Missing projectDescription"},
        500: {"description": "Classification failed"},
    },
}

CLASSIFY_ST_URL_DOC = {
    "tags": ["Classification"],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["projectDescription", "projectUrl"],
                "properties": {
                    "projectName": {"type": "string", "example": "My Project"},
                    "projectUrl": {
                        "type": "string",
                        "example": "https://github.com/org/repo",
                    },
                    "projectDescription": {
                        "type": "string",
                        "example": "Required by current route validation.",
                    },
                },
            },
        }
    ],
    "responses": {
        200: {"description": "SDG predictions"},
        400: {"description": "Invalid request or repository URL"},
        500: {"description": "Classification failed"},
    },
}

OSDG_API_DOC = {
    "tags": ["External"],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["projectDescription"],
                "properties": {
                    "projectName": {"type": "string", "example": "My Project"},
                    "projectUrl": {
                        "type": "string",
                        "example": "https://github.com/org/repo",
                    },
                    "projectDescription": {
                        "type": "string",
                        "example": "Project summary text.",
                    },
                },
            },
        }
    ],
    "responses": {
        200: {"description": "External API predictions"},
        400: {"description": "Missing projectDescription"},
        500: {"description": "External API request failed"},
    },
}
