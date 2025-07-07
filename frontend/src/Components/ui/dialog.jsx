import React from 'react';
import PropTypes from 'prop-types';

export function Dialog({ open, onOpenChange, children }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div
        className="relative z-50 rounded-lg bg-white shadow-xl  "
        onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside modal content
      >
        {children}
      </div>
    </div>
  );
}

Dialog.propTypes = {
  open: PropTypes.bool.isRequired,
  onOpenChange: PropTypes.func.isRequired,
  children: PropTypes.node.isRequired,
};

export function DialogContent({ className = '', children, ...props }) {
  return (
    <div className={`relative flex flex-col rounded-lg ${className}`} {...props}>
      {children}
    </div>
  );
}

DialogContent.propTypes = {
  className: PropTypes.string,
  children: PropTypes.node.isRequired,
};

export function DialogHeader({ className = '', children, ...props }) {
  return (
    <div className={`flex flex-col space-y-1.5 text-center sm:text-left ${className}`} {...props}>
      {children}
    </div>
  );
}

DialogHeader.propTypes = {
  className: PropTypes.string,
  children: PropTypes.node.isRequired,
};

export function DialogTitle({ className = '', children, ...props }) {
  return (
    <h2 className={`text-lg font-semibold leading-none tracking-tight ${className}`} {...props}>
      {children}
    </h2>
  );
}

DialogTitle.propTypes = {
  className: PropTypes.string,
  children: PropTypes.node.isRequired,
};