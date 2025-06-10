"use client";

import { ChangeEvent, InputHTMLAttributes, ReactNode, useState } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: ReactNode;
  error?: string;
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
}

export default function Input({
  label,
  error,
  id,
  className = '',
  onChange,
  ...props
}: InputProps) {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="mb-5">
      <label
        htmlFor={id}
        className="block text-sm font-medium text-gray-800 mb-1.5 drop-shadow-sm"
      >
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          className={`w-full px-4 py-2.5 border ${error ? 'border-red-500' : isFocused ? 'border-primary-500' : 'border-gray-300'}
          rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
          transition-all duration-200 ${className}`}
          onChange={onChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? `${id}-error` : undefined}
          {...props}
        />
      </div>
      {error && (
        <p id={`${id}-error`} className="mt-1.5 text-sm text-red-600 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}
