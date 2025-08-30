import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface User {
  username: string;
  role: 'admin' | 'guest';
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => boolean;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Default users with credentials
const defaultUsers: Record<string, { password: string; role: 'admin' | 'guest' }> = {
  admin: { password: 'RagPortal092025', role: 'admin' },
  guest: { password: 'guestRagPortal092025', role: 'guest' },
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  // Check for stored authentication on component mount
  useEffect(() => {
    const storedUser = localStorage.getItem('authUser');
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.removeItem('authUser');
      }
    }
  }, []);

  const login = (username: string, password: string): boolean => {
    const userInfo = defaultUsers[username.toLowerCase()];
    
    if (userInfo && userInfo.password === password) {
      const authenticatedUser: User = {
        username: username.toLowerCase(),
        role: userInfo.role,
      };
      
      setUser(authenticatedUser);
      localStorage.setItem('authUser', JSON.stringify(authenticatedUser));
      return true;
    }
    
    return false;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('authUser');
  };

  const isAuthenticated = user !== null;
  const isAdmin = user?.role === 'admin';

  const value: AuthContextType = {
    user,
    login,
    logout,
    isAuthenticated,
    isAdmin,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
