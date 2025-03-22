API Documentation for RLG Data & RLG Fans
This document provides an overview of the main API endpoints available in RLG Data and RLG Fans, including the required parameters, authentication, and response formats.

Table of Contents
Authentication
User Management
Subscription Management
Data Collection & Analytics
Content Scheduling & Automation
Platform-Specific Services
Notifications & Recommendations
1. Authentication
Login
Endpoint: /api/auth/login
Method: POST
Request:
json
Copy code
{
  "email": "user@example.com",
  "password": "password123"
}
Response:
json
Copy code
{
  "token": "jwt_token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user123"
  }
}
Description: Authenticates a user and returns a JWT token for future requests.
Register
Endpoint: /api/auth/register
Method: POST
Request:
json
Copy code
{
  "email": "user@example.com",
  "username": "user123",
  "password": "password123"
}
Response:
json
Copy code
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user123"
  }
}
2. User Management
Get User Profile
Endpoint: /api/user/profile
Method: GET
Headers: Authorization: Bearer <token>
Response:
json
Copy code
{
  "id": 1,
  "email": "user@example.com",
  "username": "user123",
  "subscription_status": "active"
}
Description: Retrieves the profile of the currently authenticated user.
3. Subscription Management
Create Subscription
Endpoint: /api/subscription/create
Method: POST
Headers: Authorization: Bearer <token>
Request:
json
Copy code
{
  "plan_id": "premium_monthly"
}
Response:
json
Copy code
{
  "status": "Subscription created successfully.",
  "subscription_id": "sub_1Jh5ZDFZhm8c3a"
}
Cancel Subscription
Endpoint: /api/subscription/cancel
Method: DELETE
Headers: Authorization: Bearer <token>
Response:
json
Copy code
{
  "status": "Subscription canceled successfully."
}
4. Data Collection & Analytics
Fetch Data Summary
Endpoint: /api/data/summary
Method: GET
Headers: Authorization: Bearer <token>
Response:
json
Copy code
{
  "mentions": 500,
  "engagement_rate": 12.5,
  "platform_breakdown": {
    "onlyfans": 200,
    "instagram": 100,
    "twitter": 100,
    "tiktok": 100
  }
}
Perform Sentiment Analysis
Endpoint: /api/analytics/sentiment
Method: POST
Headers: Authorization: Bearer <token>
Request:
json
Copy code
{
  "content_id": "12345",
  "text": "Amazing product! Love it!"
}
Response:
json
Copy code
{
  "sentiment": "positive",
  "confidence": 0.98
}
5. Content Scheduling & Automation
Schedule Content
Endpoint: /api/schedule/content
Method: POST
Headers: Authorization: Bearer <token>
Request:
json
Copy code
{
  "platform": "instagram",
  "post_time": "2024-12-01T10:00:00Z",
  "content": "Check out our new product launch!",
  "media_url": "https://example.com/image.jpg"
}
Response:
json
Copy code
{
  "status": "Content scheduled successfully.",
  "post_id": "ig_12345"
}
Cancel Scheduled Content
Endpoint: /api/schedule/cancel
Method: DELETE
Headers: Authorization: Bearer <token>
Request:
json
Copy code
{
  "post_id": "ig_12345"
}
Response:
json
Copy code
{
  "status": "Scheduled content canceled."
}
6. Platform-Specific Services
Fetch OnlyFans Data
Endpoint: /api/platform/onlyfans/data
Method: GET
Headers: Authorization: Bearer <token>
Response:
json
Copy code
{
  "followers": 15000,
  "earnings": 1200.50,
  "top_posts": [
    { "post_id": "123", "likes": 300, "comments": 40 },
    { "post_id": "124", "likes": 250, "comments": 30 }
  ]
}
Fetch Stripchat Analytics
Endpoint: /api/platform/stripchat/analytics
Method: GET
Headers: Authorization: Bearer <token>
Response:
json
Copy code
{
  "total_views": 4500,
  "engagement_rate": 9.7,
  "popular_content": [
    { "title": "Live Show", "viewers": 800 },
    { "title": "Exclusive Content", "viewers": 600 }
  ]
}
(Repeat similar structure for each platform integration: Sheer, Pornhub, Simpcity, etc.)

7. Notifications & Recommendations
Fetch Notifications
Endpoint: /api/notifications
Method: GET
Headers: Authorization: Bearer <token>
Response:
json
Copy code
{
  "notifications": [
    { "id": 1, "message": "New follower on OnlyFans!", "timestamp": "2024-12-01T10:00:00Z" },
    { "id": 2, "message": "Content schedule confirmed for Instagram.", "timestamp": "2024-12-01T12:00:00Z" }
  ]
}
Get Content Recommendations
Endpoint: /api/recommendations/content
Method: GET
Headers: Authorization: Bearer <token>
Response:
json
Copy code
{
  "recommendations": [
    {
      "content": "Post about your holiday sale with hashtags #holidaysale #exclusive",
      "platform": "Instagram"
    },
    {
      "content": "Offer a limited-time discount for subscribers",
      "platform": "OnlyFans"
    }
  ]
}
Status Codes
200 OK: Successful request.
400 Bad Request: Invalid request parameters.
401 Unauthorized: Invalid or missing authentication token.
404 Not Found: Requested resource not found.
500 Internal Server Error: General server error.

Additional Notes
Rate Limiting: Endpoints are rate-limited to prevent abuse. Contact support for higher usage needs.
Error Responses: For failed requests, the response will contain an error key describing the issue.


This document provides a comprehensive overview of the APIs for RLG Data and RLG Fans tools. For further details or questions, refer to the Developer Guide or contact our support team.

