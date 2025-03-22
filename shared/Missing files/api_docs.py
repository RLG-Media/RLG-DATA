from flask import Flask, jsonify
from flasgger import Swagger, swag_from

app = Flask(__name__)

# Swagger configuration
app.config["SWAGGER"] = {
    "title": "RLG Data API Documentation",
    "uiversion": 3,
    "openapi": "3.0.3",
    "description": """
    Welcome to the RLG Data API Documentation. This interactive guide provides 
    detailed information about all API endpoints, including request/response 
    formats, authentication requirements, and examples.
    """,
}
swagger = Swagger(app)

@app.route('/api/v1/status', methods=['GET'])
@swag_from({
    "tags": ["System"],
    "summary": "Check API status",
    "description": "Endpoint to check the status of the API server.",
    "responses": {
        200: {
            "description": "API is running",
            "content": {
                "application/json": {
                    "example": {"status": "API is running"}
                }
            },
        }
    },
})
def api_status():
    """
    Check the status of the API server.
    """
    return jsonify({"status": "API is running"})


@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
@swag_from({
    "tags": ["Users"],
    "summary": "Fetch user details",
    "description": "Retrieve details for a specific user by their user ID.",
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "required": True,
            "description": "The ID of the user to fetch.",
            "schema": {"type": "integer"},
        }
    ],
    "responses": {
        200: {
            "description": "User details retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "name": "John Doe",
                        "email": "john.doe@example.com"
                    }
                }
            },
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"error": "User not found"}
                }
            },
        },
    },
})
def get_user(user_id):
    """
    Retrieve user details by ID.
    """
    # Mock data for demonstration purposes
    user = {"id": user_id, "name": "John Doe", "email": "john.doe@example.com"}
    return jsonify(user)


@app.route('/api/v1/data/clean', methods=['POST'])
@swag_from({
    "tags": ["Data"],
    "summary": "Clean and prepare data",
    "description": "Submit raw data to be cleaned and processed for analytics.",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "array",
                            "items": {"type": "string"},
                            "example": ["raw1", "raw2", "raw3"],
                        }
                    },
                    "required": ["data"],
                }
            }
        },
    },
    "responses": {
        200: {
            "description": "Data cleaned successfully",
            "content": {
                "application/json": {
                    "example": {
                        "original_data": ["raw1", "raw2", "raw3"],
                        "cleaned_data": ["cleaned1", "cleaned2", "cleaned3"],
                    }
                }
            },
        }
    },
})
def clean_data():
    """
    Clean and process data.
    """
    data = request.json.get("data", [])
    cleaned_data = [item.strip().lower() for item in data]  # Example cleaning
    return jsonify({"original_data": data, "cleaned_data": cleaned_data})


@app.route('/api/v1/docs', methods=['GET'])
@swag_from({
    "tags": ["Documentation"],
    "summary": "Access API documentation",
    "description": "Redirect to the Swagger UI for interactive API documentation.",
    "responses": {
        302: {
            "description": "Redirect to Swagger UI",
        }
    },
})
def api_docs():
    """
    Redirect to Swagger UI for API documentation.
    """
    return jsonify({"message": "Visit /apidocs for API documentation"})


# Automatically scan the app for additional documentation
def auto_generate_docs(app):
    """
    Auto-generate Swagger documentation for all registered routes.
    """
    logging.info("Auto-generating API documentation...")
    Swagger(app)


if __name__ == "__main__":
    # Initialize Swagger
    auto_generate_docs(app)

    # Run Flask app
    app.run(debug=True, port=5000)
