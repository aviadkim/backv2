import React from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';

const LoadingScreen = () => {
  return (
    <AccessibilityWrapper>
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
        <h2 className="text-xl font-semibold text-gray-700 mt-4">Loading...</h2>
        <p className="text-gray-500 mt-2">Please wait while we prepare your experience</p>
      </div>
    </div>
    </AccessibilityWrapper>
  );
};

export default LoadingScreen;
