import React from 'react';
import PropTypes from 'prop-types';

export function Badge({ className = '', variant = 'default', children, ...props }) {
  const baseStyles = 'inline-flex items-center rounded-md border border-gray-200 px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-950 focus:ring-offset-2';

  const variantStyles = {
    default: 'border-transparent bg-black text-white hover:bg-gray-800/80',
    secondary: 'border-transparent bg-gray-100 text-gray-900 hover:bg-gray-200/80',
    destructive: 'border-transparent bg-red-600 text-white hover:bg-red-700/80',
    outline: 'text-gray-950',
  };

  return (
    <div className={`${baseStyles} ${variantStyles[variant]} ${className}`} {...props}>
      {children}
    </div>
  );
}

Badge.propTypes = {
  className: PropTypes.string,
  variant: PropTypes.oneOf(['default', 'secondary', 'destructive', 'outline']),
  children: PropTypes.node.isRequired,
};