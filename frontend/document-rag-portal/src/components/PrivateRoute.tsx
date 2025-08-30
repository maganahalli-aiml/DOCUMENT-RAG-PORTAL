import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import Login from './Login';

interface PrivateRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, isAdmin } = useAuth();

  // If not authenticated, show login
  if (!isAuthenticated) {
    return <Login />;
  }

  // If admin is required but user is not admin, show access denied
  if (requireAdmin && !isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50">
        <div className="max-w-md w-full text-center p-8">
          <div className="mx-auto h-20 w-20 flex items-center justify-center bg-gradient-to-r from-red-500 to-orange-600 rounded-full mb-6">
            <svg className="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h2>
          <p className="text-gray-600 mb-6">
            You need administrator privileges to access this page. Please contact your administrator for access.
          </p>
          <div className="text-sm text-gray-500">
            Current role: Guest
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default PrivateRoute;
