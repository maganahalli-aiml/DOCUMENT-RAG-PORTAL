# Frontend Authentication Refactoring - Test Guide

## Testing Environment Variable Configuration

### 1. Local Development Testing

```bash
# Set custom passwords for testing
export REACT_APP_ADMIN_PASSWORD="TestAdmin123!"
export REACT_APP_GUEST_PASSWORD="TestGuest456!"

# Start the frontend
cd frontend/document-rag-portal
npm start
```

### 2. Docker Testing

```bash
# Test with custom environment variables
docker run -e REACT_APP_ADMIN_PASSWORD="DockerAdmin789!" \
           -e REACT_APP_GUEST_PASSWORD="DockerGuest012!" \
           -p 3002:3000 \
           document-portal-frontend:v1.0
```

### 3. Docker Compose Testing

```bash
# Set environment variables in shell
export REACT_APP_ADMIN_PASSWORD="ComposeAdmin345!"
export REACT_APP_GUEST_PASSWORD="ComposeGuest678!"

# Deploy with docker-compose
docker-compose up document-portal-frontend
```

### 4. Production Testing

```bash
# Create production environment file
cp .env.production .env

# Edit .env with your secure passwords
nano .env

# Build and test
npm run build
serve -s build
```

## Verification Steps

1. **Environment Variable Loading**
   - Check that `process.env.REACT_APP_ADMIN_PASSWORD` is available in browser console
   - Verify fallback to default values when env vars not set

2. **Authentication Testing**
   - Try logging in with environment variable passwords
   - Verify fallback to default passwords works
   - Test both admin and guest user accounts

3. **Docker Integration**
   - Verify environment variables pass through Docker containers
   - Test that docker-compose environment variables work
   - Confirm production builds include environment variables

## Security Verification

1. **Default Password Check**
   ```bash
   # Ensure defaults are not used in production
   grep -r "RagPortal092025\|guestRagPortal092025" frontend/document-rag-portal/build/
   ```

2. **Environment Variable Check**
   ```bash
   # Verify environment variables are set
   echo $REACT_APP_ADMIN_PASSWORD
   echo $REACT_APP_GUEST_PASSWORD
   ```

3. **Build Verification**
   ```bash
   # Check that environment variables are embedded in build
   grep -r "REACT_APP_" frontend/document-rag-portal/build/static/js/
   ```

## Expected Results

- ✅ Environment variables override hardcoded values
- ✅ Fallback to secure defaults when env vars not set
- ✅ Docker containers respect environment variables
- ✅ Production builds include environment variables
- ✅ Authentication works with custom passwords
- ✅ No hardcoded passwords in production builds

## Troubleshooting

### Environment Variables Not Working
```bash
# Check if variables are set
env | grep REACT_APP_

# Restart development server after setting env vars
npm start
```

### Docker Issues
```bash
# Check environment variables in container
docker exec container_name env | grep REACT_APP_

# Rebuild with no cache
docker build --no-cache -t document-portal-frontend:v1.0 .
```

### Production Build Issues
```bash
# Clear cache and rebuild
rm -rf build node_modules
npm install
npm run build
```
