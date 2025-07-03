import React from 'react';
import PropTypes from 'prop-types';

export function Progress({ value = 0, className = '', ...props }) {
  const clampedValue = Math.min(100, Math.max(0, value)); // Ensure value is between 0 and 100

  return (
    <div
      className={`relative h-2 w-full overflow-hidden rounded-full bg-gray-200 ${className}`}
      {...props}
    >
      <div
        className="h-full w-full flex-1 bg-blue-600 transition-all duration-300 ease-in-out"
        style={{ transform: `translateX(-${100 - clampedValue}%)` }}
      />
    </div>
  );
}

Progress.propTypes = {
  value: PropTypes.number,
  className: PropTypes.string,
};