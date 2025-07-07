import React from 'react';
import PropTypes from 'prop-types';

export function Textarea({ className = '', ...props }) {
  const baseStyles = 'flex min-h-[60px] w-full rounded-md border border-gray-200 bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-950 disabled:cursor-not-allowed disabled:opacity-50';

  return (
    <textarea
      className={`${baseStyles} ${className}`}
      {...props}
    />
  );
}

Textarea.propTypes = {
  className: PropTypes.string,
};