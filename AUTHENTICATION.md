# Authentication System Documentation

## 🔐 Overview
The Document RAG Portal includes a comprehensive authentication system with role-based access control and configurable credentials via environment variables.

## 🔑 User Accounts Configuration

### Environment Variable Configuration
User credentials are now configured via environment variables for enhanced security:

```bash
# Frontend authentication environment variables
REACT_APP_ADMIN_PASSWORD=your_secure_admin_password
REACT_APP_GUEST_PASSWORD=your_secure_guest_password
```

### Default Users
The system comes with two pre-configured user accounts:

#### 1. Admin User
- **Username:** `admin`
- **Password:** Configured via `REACT_APP_ADMIN_PASSWORD` environment variable
- **Default Password:** `RagPortal092025` (⚠️ CHANGE FOR PRODUCTION)
- **Role:** Administrator
- **Access:** Full access to all features including the Evaluation page

#### 2. Guest User
- **Username:** `guest`
- **Password:** Configured via `REACT_APP_GUEST_PASSWORD` environment variable
- **Default Password:** `guestRagPortal092025` (⚠️ CHANGE FOR PRODUCTION)
- **Role:** Guest
- **Access:** Limited access - cannot view the Evaluation page

## 🚨 Security Configuration

### Production Deployment
**CRITICAL**: Change default passwords before production deployment!

1. **Set Environment Variables:**
   ```bash
   export REACT_APP_ADMIN_PASSWORD="your_very_secure_admin_password_here"
   export REACT_APP_GUEST_PASSWORD="your_very_secure_guest_password_here"
   ```

2. **Update .env file:**
   ```bash
   REACT_APP_ADMIN_PASSWORD=your_very_secure_admin_password_here
   REACT_APP_GUEST_PASSWORD=your_very_secure_guest_password_here
   ```

3. **Docker Deployment:**
   The docker-compose files automatically use environment variables:
   ```yaml
   environment:
     - REACT_APP_ADMIN_PASSWORD=${REACT_APP_ADMIN_PASSWORD:-RagPortal092025}
     - REACT_APP_GUEST_PASSWORD=${REACT_APP_GUEST_PASSWORD:-guestRagPortal092025}
   ```

### Password Requirements
- Minimum 12 characters recommended
- Include uppercase, lowercase, numbers, and symbols
- Avoid dictionary words or common patterns
- Use unique passwords for each environment

## Features

### 🔐 Login Screen
- Clean, modern login interface
- Username and password authentication
- Password visibility toggle
- Form validation and error handling

### 👤 User Profile Display
- User information shown in sidebar
- Current role displayed
- Logout functionality

### 🛡️ Role-Based Access Control
- **Admin Role:** Can access all pages including Evaluation
- **Guest Role:** Restricted access - Evaluation page is hidden and protected

### 🔒 Route Protection
- Automatic redirect to login for unauthenticated users
- Admin-only routes are protected with proper error messages
- Session persistence using localStorage

## Usage

### Logging In
1. Open the application at http://localhost:3002
2. You'll be automatically redirected to the login screen
3. Enter credentials based on your environment configuration:
   - **Admin access:** username: `admin`, password: Value of `REACT_APP_ADMIN_PASSWORD`
   - **Guest access:** username: `guest`, password: Value of `REACT_APP_GUEST_PASSWORD`
   - **Default development:** Use the fallback passwords if environment variables not set

### Navigation
- Once logged in, navigation is filtered based on user role
- Admin users see all menu items including "Evaluation"
- Guest users see all menu items except "Evaluation"

### Logging Out
- Click the logout button in the sidebar
- Or click the logout icon in the mobile header
- You'll be redirected back to the login screen

## Technical Implementation

### Components
- `AuthContext.tsx` - React context for authentication state management
- `Login.tsx` - Login form component
- `PrivateRoute.tsx` - Route protection wrapper
- `Layout.tsx` - Updated with user profile and role-based navigation

### Security Features
- Client-side authentication with localStorage persistence
- Role-based route protection
- Graceful access denied handling for unauthorized users
- Automatic login state restoration on page refresh

### Development Notes
- Authentication state is managed using React Context
- User credentials are stored in localStorage for session persistence
- The system is designed for easy extension with additional roles and users
- All routes are protected by default - unauthenticated users see only the login screen

## Testing the System

### Admin Access Test
1. Login with admin/admin credentials
2. Verify access to all pages including Evaluation
3. Check that user profile shows "Admin" role

### Guest Access Test
1. Login with guest/guest credentials
2. Verify that Evaluation page is not visible in navigation
3. Confirm access denied if trying to access /evaluation directly
4. Check that user profile shows "Guest" role

### Session Persistence Test
1. Login and navigate around the app
2. Refresh the browser
3. Verify that authentication state is maintained
4. Logout and confirm redirect to login screen

## Future Enhancements
- Add user registration functionality
- Implement password change feature
- Add more granular permissions
- Integrate with backend authentication API
- Add password strength requirements
- Implement session timeout
