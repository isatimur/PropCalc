# PropCalc Authentication System

This document describes the authentication system implementation for the PropCalc backend.

## Overview

The authentication system provides user registration, login, and profile management functionality. It's designed to be secure and scalable, with support for different user roles and statuses.

## Features

- **User Registration**: Create new user accounts with validation
- **User Authentication**: Secure login with username/email and password
- **Profile Management**: View and update user profiles
- **Password Management**: Change passwords and request password resets
- **Session Management**: Track user sessions and provide logout functionality
- **Role-Based Access Control**: Different user roles (admin, analyst, viewer, developer)
- **User Status Management**: Active, inactive, suspended, and pending verification statuses

## Architecture

### Components

1. **User Repository** (`infrastructure/repositories/user_repository.py`)
   - Handles all database operations for users
   - Provides authentication and user management methods

2. **Authentication API** (`api/auth.py`)
   - RESTful endpoints for authentication operations
   - Integrates with the user repository
   - Handles request validation and error responses

3. **Database Models** (`infrastructure/database/models.py`)
   - User, UserSession, and UserActivity models
   - SQLAlchemy ORM models with proper relationships

4. **Security Module** (`domain/security/oauth2.py`)
   - OAuth2 implementation for token-based authentication
   - Password hashing and verification utilities

### Database Schema

#### Users Table
- `id`: Primary key
- `uuid`: Unique identifier
- `username`: Unique username
- `email`: Unique email address
- `full_name`: User's full name
- `hashed_password`: Encrypted password
- `role`: User role (admin, analyst, viewer, developer)
- `status`: Account status (active, inactive, suspended, pending_verification)
- `is_active`: Whether the account is active
- `email_verified`: Email verification status
- `last_login`: Last login timestamp
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

#### User Sessions Table
- `id`: Primary key
- `user_id`: Reference to user
- `session_token`: Active session token
- `refresh_token`: Refresh token for session renewal
- `expires_at`: Session expiration timestamp
- `ip_address`: IP address of the session
- `user_agent`: User agent string
- `is_active`: Whether the session is active

#### User Activities Table
- `id`: Primary key
- `user_id`: Reference to user
- `activity_type`: Type of activity
- `description`: Activity description
- `ip_address`: IP address of the activity
- `user_agent`: User agent string
- `metadata`: Additional activity data
- `created_at`: Activity timestamp

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Refresh access token

### User Management

- `GET /api/v1/auth/profile` - Get user profile
- `PUT /api/v1/auth/profile` - Update user profile
- `POST /api/v1/auth/change-password` - Change password
- `POST /api/v1/auth/forgot-password` - Request password reset

## Usage Examples

### User Registration

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "full_name": "New User",
    "password": "securepassword123",
    "role": "viewer"
  }'
```

### User Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword123"
  }'
```

### Get User Profile

```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Development Notes

### Mock User

For development purposes, there's a mock admin user:
- Username: `admin`
- Password: `admin123`
- Role: `admin`

### Testing

Run the test script to verify the authentication system:

```bash
cd backend
python test_auth.py
```

### Security Considerations

1. **Password Hashing**: Currently using simple hashing for development. In production, use bcrypt or similar.
2. **Token Management**: Implement proper JWT token generation and validation.
3. **Rate Limiting**: Add rate limiting for login attempts.
4. **Input Validation**: Ensure all inputs are properly validated and sanitized.
5. **HTTPS**: Use HTTPS in production for all authentication endpoints.

## Future Enhancements

1. **Email Verification**: Implement email verification for new accounts
2. **Two-Factor Authentication**: Add 2FA support
3. **Social Login**: Integrate with OAuth providers (Google, GitHub, etc.)
4. **Audit Logging**: Enhanced activity logging and monitoring
5. **Password Policies**: Enforce strong password requirements
6. **Account Lockout**: Implement account lockout after failed attempts

## Dependencies

- FastAPI
- SQLAlchemy
- Pydantic
- Python 3.8+

## Configuration

The system uses environment variables for configuration. See `config/settings.py` for available options.

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure the database is running and accessible
2. **Model Mismatches**: Check that database models match the current schema
3. **Import Errors**: Verify all required packages are installed
4. **Permission Issues**: Check database user permissions

### Logs

Check the application logs for detailed error information:

```bash
tail -f logs/app.log
```

## Support

For issues or questions about the authentication system, please refer to the project documentation or create an issue in the project repository.
