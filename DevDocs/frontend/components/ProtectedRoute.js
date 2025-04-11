import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../providers/AuthProvider';
import LoadingScreen from './LoadingScreen';

/**
 * Higher-order component for protected routes
 * @param {React.ComponentType} Component - The component to wrap
 * @param {Object} options - Options for the protected route
 * @param {string[]} options.allowedRoles - Roles allowed to access the route (optional)
 * @returns {React.ComponentType} - The wrapped component
 */
const withProtectedRoute = (Component, options = {}) => {
  const ProtectedRoute = (props) => {
    const { user, loading } = useAuth();
    const router = useRouter();
    const [isAuthorized, setIsAuthorized] = useState(false);
    
    useEffect(() => {
      // If still loading auth state, wait
      if (loading) return;
      
      // If no user, redirect to login
      if (!user) {
        router.push({
          pathname: '/login',
          query: { returnUrl: router.asPath }
        });
        return;
      }
      
      // Check role-based access if roles are specified
      if (options.allowedRoles && options.allowedRoles.length > 0) {
        if (!options.allowedRoles.includes(user.role)) {
          router.push('/unauthorized');
          return;
        }
      }
      
      // User is authorized
      setIsAuthorized(true);
    }, [user, loading, router]);
    
    // Show loading screen while checking authorization
    if (loading || !isAuthorized) {
      return <LoadingScreen />;
    }
    
    // Render the protected component
    return <Component {...props} />;
  };
  
  // Copy getInitialProps if it exists
  if (Component.getInitialProps) {
    ProtectedRoute.getInitialProps = Component.getInitialProps;
  }
  
  return ProtectedRoute;
};

export default withProtectedRoute;
