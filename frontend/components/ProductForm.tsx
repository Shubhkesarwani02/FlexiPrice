'use client';

import { useState } from 'react';
import { api } from '@/lib/api';

interface ProductFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export default function ProductForm({ onSuccess, onCancel }: ProductFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    sku: '',
    name: '',
    description: '',
    category: '',
    basePrice: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // SKU validation
    if (!formData.sku.trim()) {
      newErrors.sku = 'SKU is required';
    } else if (formData.sku.length > 100) {
      newErrors.sku = 'SKU must be 100 characters or less';
    }

    // Name validation
    if (!formData.name.trim()) {
      newErrors.name = 'Product name is required';
    } else if (formData.name.length > 255) {
      newErrors.name = 'Name must be 255 characters or less';
    }

    // Category validation
    if (formData.category && formData.category.length > 100) {
      newErrors.category = 'Category must be 100 characters or less';
    }

    // Base price validation
    if (!formData.basePrice) {
      newErrors.basePrice = 'Base price is required';
    } else {
      const price = parseFloat(formData.basePrice);
      if (isNaN(price) || price <= 0) {
        newErrors.basePrice = 'Base price must be greater than 0';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      await api.createProduct({
        sku: formData.sku.trim(),
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
        category: formData.category.trim() || undefined,
        basePrice: parseFloat(formData.basePrice),
      });

      onSuccess();
    } catch (err: unknown) {
      let message = 'Failed to create product';
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        message = axiosError.response?.data?.detail || message;
      } else if (err instanceof Error) {
        message = err.message;
      }
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 text-sm">
      {error && (
        <div className="border border-[var(--danger)] text-[var(--danger)] px-4 py-3 rounded-md bg-black/40 text-xs">
          {error}
        </div>
      )}

      {/* SKU */}
      <div>
        <label htmlFor="sku" className="block text-xs font-medium mb-1 tracking-[0.16em] uppercase text-[var(--foreground-muted)]">
          SKU <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="sku"
          name="sku"
          value={formData.sku}
          onChange={handleChange}
          className={`w-full px-3 py-2 bg-black/40 border rounded-md outline-none focus:ring-0 focus:border-[var(--accent)] fp-card-price ${
            errors.sku ? 'border-[var(--danger)]' : 'border-[var(--border-subtle)]'
          }`}
          placeholder="e.g., LAPTOP-001"
        />
        {errors.sku && <p className="text-[var(--danger)] text-xs mt-1">{errors.sku}</p>}
      </div>

      {/* Name */}
      <div>
        <label htmlFor="name" className="block text-xs font-medium mb-1 tracking-[0.16em] uppercase text-[var(--foreground-muted)]">
          Product Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className={`w-full px-3 py-2 bg-black/40 border rounded-md outline-none focus:ring-0 focus:border-[var(--accent)] fp-card-price ${
            errors.name ? 'border-[var(--danger)]' : 'border-[var(--border-subtle)]'
          }`}
          placeholder="e.g., Premium Laptop Pro"
        />
        {errors.name && <p className="text-[var(--danger)] text-xs mt-1">{errors.name}</p>}
      </div>

      {/* Category */}
      <div>
        <label htmlFor="category" className="block text-xs font-medium mb-1 tracking-[0.16em] uppercase text-[var(--foreground-muted)]">
          Category
        </label>
        <input
          type="text"
          id="category"
          name="category"
          value={formData.category}
          onChange={handleChange}
          className={`w-full px-3 py-2 bg-black/40 border rounded-md outline-none focus:ring-0 focus:border-[var(--accent)] fp-card-price ${
            errors.category ? 'border-[var(--danger)]' : 'border-[var(--border-subtle)]'
          }`}
          placeholder="e.g., Electronics"
        />
        {errors.category && <p className="text-[var(--danger)] text-xs mt-1">{errors.category}</p>}
      </div>

      {/* Base Price */}
      <div>
        <label htmlFor="basePrice" className="block text-xs font-medium mb-1 tracking-[0.16em] uppercase text-[var(--foreground-muted)]">
          Base Price ($) <span className="text-red-500">*</span>
        </label>
        <input
          type="number"
          id="basePrice"
          name="basePrice"
          value={formData.basePrice}
          onChange={handleChange}
          step="0.01"
          min="0"
          className={`w-full px-3 py-2 bg-black/40 border rounded-md outline-none focus:ring-0 focus:border-[var(--accent)] fp-card-price ${
            errors.basePrice ? 'border-[var(--danger)]' : 'border-[var(--border-subtle)]'
          }`}
          placeholder="e.g., 999.99"
        />
        {errors.basePrice && <p className="text-[var(--danger)] text-xs mt-1">{errors.basePrice}</p>}
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-xs font-medium mb-1 tracking-[0.16em] uppercase text-[var(--foreground-muted)]">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          className="w-full px-3 py-2 bg-black/40 border border-[var(--border-subtle)] rounded-md outline-none focus:ring-0 focus:border-[var(--accent)] fp-card-price"
          placeholder="Product description..."
        />
      </div>

      {/* Form Actions */}
      <div className="flex gap-3 pt-4 text-xs">
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 fp-pill-button justify-center disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Creating...' : 'Create Product'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="flex-1 border border-[var(--border-subtle)] rounded-full py-2 px-4 text-[var(--foreground-muted)] hover:border-[var(--accent-subtle)] hover:text-[var(--accent)] transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
