'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Product } from '@/types';

interface InventoryFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export default function InventoryForm({ onSuccess, onCancel }: InventoryFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(true);
  const [formData, setFormData] = useState({
    productId: '',
    batchCode: '',
    quantity: '',
    expiryDate: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const response = await api.getProducts();
      setProducts(response.data);
    } catch (err) {
      console.error('Failed to load products:', err);
    } finally {
      setLoadingProducts(false);
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Product ID validation
    if (!formData.productId) {
      newErrors.productId = 'Please select a product';
    }

    // Batch code validation (optional, but if provided, max 100 chars)
    if (formData.batchCode && formData.batchCode.length > 100) {
      newErrors.batchCode = 'Batch code must be 100 characters or less';
    }

    // Quantity validation
    if (!formData.quantity) {
      newErrors.quantity = 'Quantity is required';
    } else {
      const qty = parseInt(formData.quantity);
      if (isNaN(qty) || qty <= 0) {
        newErrors.quantity = 'Quantity must be greater than 0';
      }
    }

    // Expiry date validation
    if (!formData.expiryDate) {
      newErrors.expiryDate = 'Expiry date is required';
    } else {
      const expiryDate = new Date(formData.expiryDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      if (expiryDate < today) {
        newErrors.expiryDate = 'Expiry date cannot be in the past';
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
      await api.createInventoryBatch({
        productId: parseInt(formData.productId),
        batchCode: formData.batchCode.trim() || undefined,
        quantity: parseInt(formData.quantity),
        expiryDate: formData.expiryDate,
      });

      onSuccess();
    } catch (err: unknown) {
      let message = 'Failed to create inventory batch';
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  // Get minimum date (today)
  const getMinDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 text-sm">
      {error && (
        <div className="border border-[var(--danger)] text-[var(--danger)] px-4 py-3 rounded-md bg-black/40 text-xs">
          {error}
        </div>
      )}

      {/* Product Selection */}
      <div>
        <label htmlFor="productId" className="block text-xs font-medium mb-1 tracking-[0.16em] uppercase text-[var(--foreground-muted)]">
          Product <span className="text-red-500">*</span>
        </label>
        {loadingProducts ? (
          <div className="w-full px-3 py-2 bg-black/40 border border-[var(--border-subtle)] rounded-md fp-card-price text-[var(--foreground-muted)]">
            Loading products...
          </div>
        ) : (
          <select
            id="productId"
            name="productId"
            value={formData.productId}
            onChange={handleChange}
            className={`w-full px-3 py-2 bg-black/40 border rounded-md outline-none focus:ring-0 focus:border-[var(--accent)] fp-card-price ${
              errors.productId ? 'border-[var(--danger)]' : 'border-[var(--border-subtle)]'
            }`}
          >
            <option value="">Select a product</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.sku} - {product.name}
              </option>
            ))}
          </select>
        )}
        {errors.productId && <p className="text-[var(--danger)] text-xs mt-1">{errors.productId}</p>}
      </div>

      {/* Batch Code */}
      <div>
        <label htmlFor="batchCode" className="block text-xs font-medium mb-1 tracking-[0.16em] uppercase text-[var(--foreground-muted)]">
          Batch Code
        </label>
        <input
          type="text"
          id="batchCode"
          name="batchCode"
          value={formData.batchCode}
          onChange={handleChange}
          className={`w-full px-3 py-2 bg-black/40 border rounded-md outline-none focus:ring-0 focus:border-[var(--accent)] fp-card-price ${
            errors.batchCode ? 'border-[var(--danger)]' : 'border-[var(--border-subtle)]'
          }`}
          placeholder="e.g., BATCH-2024-001"
        />
        {errors.batchCode && <p className="text-[var(--danger)] text-xs mt-1">{errors.batchCode}</p>}
        <p className="text-[var(--foreground-muted)] text-[10px] mt-1 tracking-[0.12em] uppercase">
          Optional batch identification code
        </p>
      </div>

      {/* Quantity */}
      <div>
        <label htmlFor="quantity" className="block text-xs font-medium mb-1 tracking-[0.16em] uppercase text-[var(--foreground-muted)]">
          Quantity <span className="text-red-500">*</span>
        </label>
        <input
          type="number"
          id="quantity"
          name="quantity"
          value={formData.quantity}
          onChange={handleChange}
          min="1"
          step="1"
          className={`w-full px-3 py-2 bg-black/40 border rounded-md outline-none focus:ring-0 focus:border-[var(--accent)] fp-card-price ${
            errors.quantity ? 'border-[var(--danger)]' : 'border-[var(--border-subtle)]'
          }`}
          placeholder="e.g., 100"
        />
        {errors.quantity && <p className="text-[var(--danger)] text-xs mt-1">{errors.quantity}</p>}
      </div>

      {/* Expiry Date */}
      <div>
        <label htmlFor="expiryDate" className="block text-xs font-medium mb-1 tracking-[0.16em] uppercase text-[var(--foreground-muted)]">
          Expiry Date <span className="text-red-500">*</span>
        </label>
        <input
          type="date"
          id="expiryDate"
          name="expiryDate"
          value={formData.expiryDate}
          onChange={handleChange}
          min={getMinDate()}
          className={`w-full px-3 py-2 bg-black/40 border rounded-md outline-none focus:ring-0 focus:border-[var(--accent)] fp-card-price ${
            errors.expiryDate ? 'border-[var(--danger)]' : 'border-[var(--border-subtle)]'
          }`}
        />
        {errors.expiryDate && <p className="text-[var(--danger)] text-xs mt-1">{errors.expiryDate}</p>}
        <p className="text-[var(--foreground-muted)] text-[10px] mt-1 tracking-[0.12em] uppercase">
          Date when this batch expires
        </p>
      </div>

      {/* Form Actions */}
      <div className="flex gap-3 pt-4 text-xs">
        <button
          type="submit"
          disabled={isSubmitting || loadingProducts}
          className="flex-1 fp-pill-button justify-center disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Creating...' : 'Add Inventory Batch'}
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
