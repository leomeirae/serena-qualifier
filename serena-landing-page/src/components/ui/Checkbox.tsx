"use client";

import { ChangeEvent, InputHTMLAttributes, ReactNode } from 'react';

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label: ReactNode;
  error?: string;
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
}

export default function Checkbox({
  label,
  error,
  id,
  className = '',
  onChange,
  ...props
}: CheckboxProps) {
  return (
    <div className="mb-5">
      <div className="flex items-start">
        <div className="flex items-center h-5">
          <input
            id={id}
            type="checkbox"
            className={`h-4 w-4 text-primary-500 border-gray-300 rounded
            focus:ring-2 focus:ring-primary-500 focus:ring-offset-1
            transition-colors duration-200 cursor-pointer ${className}`}
            onChange={onChange}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={error ? `${id}-error` : undefined}
            {...props}
          />
        </div>
        <div className="ml-3">
          <label htmlFor={id} className="text-gray-800 cursor-pointer drop-shadow-sm">
            {label}
          </label>
        </div>
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
