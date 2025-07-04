// components/ui/card.jsx
import React from 'react';
import PropTypes from 'prop-types';

export function Card({ className = '', ...props }) {
  return (
    <div className={`rounded-xl border bg-card text-card-foreground shadow w-full ${className}`} {...props} />
  );
}

Card.propTypes = {
  className: PropTypes.string,
};

export function CardContent({ className = '', ...props }) {
  // Apenas defina o padding aqui. Se você quer 16px (p-4), use p-4.
  // Se quiser 24px, use p-6. Remova qualquer pt-0 ou px/py conflitante.
  return (
    <div className={`p-4 ${className}`} {...props} />
  );
}

CardContent.propTypes = {
  className: PropTypes.string,
};