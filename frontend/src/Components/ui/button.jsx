"use client";

import React from "react";
import PropTypes from "prop-types"; // Se você estiver usando PropTypes, mantenha a importação

export function Button({ children, variant = "default", size = "default", onClick, type = "button", className = "", disabled = false }) {
  // Estilos base comuns a todos os botões
  const baseClasses = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-950 disabled:pointer-events-none disabled:opacity-50";

  // Estilos de variante, adaptados para suas cores principais e as do Shadcn UI
  const variantClasses = {
    // Sua variante 'primary' original, agora 'default' para seguir a convenção do Shadcn
    default: "bg-black text-white shadow hover:bg-gray-800",
    // Sua variante 'secondary' original, pode ser a mesma ou diferente
    secondary: "bg-gray-100 text-gray-900 shadow-sm hover:bg-gray-200", // Alterado para ser diferente da default
    destructive: "bg-red-600 text-white shadow-sm hover:bg-red-700",
    outline: "border border-gray-200 bg-white shadow-sm hover:bg-gray-100 hover:text-gray-900",
    ghost: "hover:bg-gray-100 hover:text-gray-900",
    link: "text-blue-600 underline-offset-4 hover:underline",
  };

  // Estilos de tamanho
  const sizeClasses = {
    default: "h-9 px-4 py-2", // Tamanho padrão do Shadcn
    sm: "h-8 px-3 text-xs",
    lg: "h-10 px-8",
    icon: "h-9 w-9", // Para botões com apenas ícones
    // Você pode adicionar seu tamanho original 'w-full py-3 px-4' aqui se ainda precisar dele como uma opção específica
    full: "w-full py-3 px-4", // Exemplo de como adicionar seu tamanho original
  };

  // Lógica para aplicar classes de desabilitado
  const disabledClasses = "bg-gray-400 text-gray-700 cursor-not-allowed opacity-50"; // Mantive sua ideia e adicionei opacity

  return (
    <button
      type={type}
      onClick={onClick}
      // Combina as classes base, de variante, de tamanho e as classes adicionais (className)
      // A classe de desabilitado sobrescreve as de variante quando `disabled` é true
      className={`${baseClasses} ${
        disabled ? disabledClasses : variantClasses[variant]
      } ${sizeClasses[size]} ${className}`}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

// Opcional: Adicione PropTypes para melhor validação e documentação
Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(["default", "secondary", "destructive", "outline", "ghost", "link"]),
  size: PropTypes.oneOf(["default", "sm", "lg", "icon", "full"]), // Inclua 'full' se você adicionar essa variante de tamanho
  onClick: PropTypes.func,
  type: PropTypes.string,
  className: PropTypes.string,
  disabled: PropTypes.bool,
};