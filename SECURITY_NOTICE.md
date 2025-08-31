# 🔐 SECURITY NOTICE FOR DOCUMENT RAG PORTAL

⚠️  **CRITICAL SECURITY UPDATE**: Frontend authentication passwords have been refactored to use environment variables.

## 🚨 IMMEDIATE ACTION REQUIRED

### Default Passwords Removed
- **BEFORE**: Hardcoded passwords in `AuthContext.tsx`
- **NOW**: Environment variables with secure fallbacks
- **ACTION**: Change default passwords immediately for production

### Changed Files
- `frontend/document-rag-portal/src/contexts/AuthContext.tsx` - Now reads from environment variables
- `frontend/document-rag-portal/.env` - Added password environment variables
- `docker-compose.yml` & `docker-compose.hub.yml` - Added password environment variables
- `.env.template` & `.env.production` - Added password configuration templates

## 🔒 ENVIRONMENT VARIABLES

### Frontend Authentication
```bash
# Admin user password (CHANGE FOR PRODUCTION!)
REACT_APP_ADMIN_PASSWORD=your_secure_admin_password_here

# Guest user password (CHANGE FOR PRODUCTION!)
REACT_APP_GUEST_PASSWORD=your_secure_guest_password_here
```

## Before deployment:
1. Copy `.env.template` to `.env`
2. Replace ALL placeholder values with real credentials
3. **CRITICAL**: Change default authentication passwords
4. Never commit your `.env` file to git
5. Ensure your `.gitignore` excludes `.env` files

## Placeholder patterns replaced:
- SECRET_KEY=your_secret_key_here_minimum_64_characters_long_for_security
- GROQ_API_KEY=your_groq_api_key_here  
- GOOGLE_API_KEY=your_google_api_key_here
- DATABASE_URL with your_database_password
- **NEW**: REACT_APP_ADMIN_PASSWORD=your_secure_admin_password_here
- **NEW**: REACT_APP_GUEST_PASSWORD=your_secure_guest_password_here

## 🛡️ SECURITY BEST PRACTICES

### Password Requirements
- Minimum 12 characters
- Include uppercase, lowercase, numbers, and symbols
- Avoid dictionary words or common patterns
- Use unique passwords for each service
- Consider using a password manager

### Production Deployment Checklist
- [ ] Change REACT_APP_ADMIN_PASSWORD from default
- [ ] Change REACT_APP_GUEST_PASSWORD from default
- [ ] Set strong POSTGRES_PASSWORD
- [ ] Add your actual API keys
- [ ] Verify CORS_ORIGINS is restrictive
- [ ] Enable HTTPS in production
- [ ] Regularly rotate passwords and API keys
