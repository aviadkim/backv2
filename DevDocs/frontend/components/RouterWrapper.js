import React from 'react';
import { BrowserRouter } from 'react-router-dom';

const RouterWrapper = ({ children }) => {
  // Check if we're in the browser environment
  if (typeof window === 'undefined') {
    // Return children without router during server-side rendering
    return <>{children}</>;
  }
  
  return (
    <BrowserRouter>
      {children}
    </BrowserRouter>
  );
};

export default RouterWrapper;
