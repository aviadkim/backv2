import React from 'react';

/**
 * AccessibilityWrapper component
 * This component adds accessibility features to its children
 */
const AccessibilityWrapper = ({ children, id, label, role, description, ...props }) => {
  // Generate a unique ID if not provided
  const uniqueId = id || `accessibility-${Math.random().toString(36).substring(2, 9)}`;
  
  return (
    <div
      id={uniqueId}
      role={role || 'region'}
      aria-label={label || 'Content section'}
      aria-describedby={description ? `${uniqueId}-desc` : undefined}
      {...props}
    >
      {description && (
        <div id={`${uniqueId}-desc`} className="sr-only">
          {description}
        </div>
      )}
      {children}
    </div>
  );
};

export default AccessibilityWrapper;
