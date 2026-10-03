# Authentication Security Note

## Project

Secure Authentication Lab

## 1. Password Storage

Passwords are never stored as plain text.

The application uses Werkzeug's password hashing functionality to generate a password hash before storing the credential.

This means the original password is not stored directly.

## 2. Server-Side Validation

Registration input is validated on the server.

The application checks:

- Username format
- Username length
- Minimum password length
- Required input fields

Client-side validation alone is not relied upon.

## 3. Secure Session Configuration

The application configures session cookies with:

- HttpOnly
- SameSite=Lax
- Session expiration

HttpOnly helps prevent client-side scripts from directly reading the session cookie.

For production HTTPS deployment, the Secure cookie option should also be enabled.

## 4. Session Expiry

Authenticated sessions use a limited lifetime.

The demonstration application uses a 15-minute permanent session lifetime.

## 5. Logout

The logout endpoint clears the server-side session data.

After logout, the user must authenticate again to access the protected dashboard.

## 6. Rate Limiting

The login endpoint is rate-limited to:

5 requests per minute per client address.

This helps reduce repeated automated login attempts.

## 7. Generic Authentication Errors

The login endpoint returns:

"Invalid username or password."

for failed authentication.

The application does not reveal whether a particular username exists.

## 8. Testing

Automated tests verify:

- Password hashing
- Successful login
- Invalid login handling
- Protected page access
- Logout
- Password validation

## 9. Production Considerations

This project is an educational local lab.

For production deployment:

- Use a strong secret stored outside source code.
- Enable Secure cookies when using HTTPS.
- Use a persistent database.
- Use a production WSGI server.
- Store secrets in environment variables or a secret manager.
- Monitor authentication events.
- Review dependencies regularly.