'use client';

import { useState, useEffect } from 'react';
import useSWR from 'swr';
import { api } from '@/lib/api';
import { Product, Discount } from '@/types';
import Link from 'next/link';
import Modal from '@/components/Modal';
import ProductForm from '@/components/ProductForm';
import InventoryForm from '@/components/InventoryForm';

const productsFetcher = () => api.getProducts().then(res => res.data);
const discountsFetcher = () => api.getAllDiscounts().then(res => res.data);

type ModalType = 'product' | 'inventory' | null;

export default function AdminPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState('');
  const [authError, setAuthError] = useState('');
  const [activeTab, setActiveTab] = useState<'products' | 'discounts' | 'inventory'>('products');
  const [activeModal, setActiveModal] = useState<ModalType>(null);
  const [successMessage, setSuccessMessage] = useState('');

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = () => {
      const storedToken = localStorage.getItem('adminToken');
      if (storedToken) {
        setIsAuthenticated(true);
      }
    };
    checkAuth();
  }, []);

  // Auto-hide success message after 3 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(''), 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    const expectedToken = 'your-secret-admin-token-here'; // In production, use env variable
    
    if (token === expectedToken) {
      localStorage.setItem('adminToken', token);
      setIsAuthenticated(true);
      setAuthError('');
    } else {
      setAuthError('Invalid token. Please try again.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    setIsAuthenticated(false);
    setToken('');
  };

  const { data: products, isLoading: productsLoading, mutate: mutateProducts } = useSWR<Product[]>(
    isAuthenticated ? '/admin/products' : null,
    productsFetcher,
    { refreshInterval: 30000 }
  );

  const { data: discounts, isLoading: discountsLoading } = useSWR<Discount[]>(
    isAuthenticated ? '/admin/discounts' : null,
    discountsFetcher,
    { refreshInterval: 30000 }
  );

  const handleProductSuccess = () => {
    setActiveModal(null);
    setSuccessMessage('Product created successfully!');
    mutateProducts();
  };

  const handleInventorySuccess = () => {
    setActiveModal(null);
    setSuccessMessage('Inventory batch added successfully!');
    mutateProducts();
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen fp-shell flex items-center justify-center">
        <div className="fp-panel w-full max-w-md p-8">
          <h1 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-6 text-center">
            Admin Login
          </h1>
          <form onSubmit={handleLogin} className="space-y-4 text-sm">
            <div>
              <label
                htmlFor="token"
                className="block text-xs font-medium mb-2 tracking-[0.16em] uppercase text-[var(--foreground-muted)]"
              >
                Admin Token
              </label>
              <input
                type="password"
                id="token"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                className="w-full px-3 py-2 bg-black/40 border border-[var(--border-subtle)] rounded-md outline-none focus:ring-0 focus:border-[var(--accent)] fp-card-price"
                placeholder="Enter admin token"
                required
              />
            </div>
            {authError && (
              <p className="text-[var(--danger)] text-xs mt-1">{authError}</p>
            )}
            <button
              type="submit"
              className="w-full fp-pill-button justify-center mt-4"
            >
              Login
            </button>
          </form>
          <div className="mt-6 text-center">
            <Link
              href="/"
              className="text-[11px] tracking-[0.16em] uppercase text-[var(--foreground-muted)] hover:text-[var(--accent)]"
            >
              ← Back to store
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fp-shell">
      <header className="fp-shell-header">
        <div className="fp-shell-header-inner">
          <div className="fp-brand">
            <h1 className="fp-brand-title">
              <span>FlexiPrice</span> Admin
            </h1>
            <p className="fp-brand-subtitle">Products · Discounts · Inventory</p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="text-[11px] tracking-[0.16em] uppercase text-[var(--foreground-muted)] hover:text-[var(--accent)]"
            >
              Storefront
            </Link>
            <button onClick={handleLogout} className="fp-pill-button text-[10px]">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="fp-main">
        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 fp-panel px-4 py-3 flex items-center justify-between border border-[var(--accent-subtle)] text-xs">
            <span className="text-[var(--accent-subtle)]">{successMessage}</span>
            <button
              onClick={() => setSuccessMessage('')}
              className="text-[var(--foreground-muted)] hover:text-[var(--accent-subtle)]"
            >
              ×
            </button>
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-[var(--border-subtle)] mb-6">
          <nav className="-mb-px flex space-x-6 text-xs">
            <button
              onClick={() => setActiveTab('products')}
              className={`${
                activeTab === 'products'
                  ? 'border-[var(--accent-subtle)] text-[var(--accent-subtle)]'
                  : 'border-transparent text-[var(--foreground-muted)] hover:text-[var(--accent-subtle)] hover:border-[var(--border-subtle)]'
              } whitespace-nowrap py-3 px-1 border-b font-medium tracking-[0.18em] uppercase transition-colors`}
            >
              Products ({products?.length || 0})
            </button>
            <button
              onClick={() => setActiveTab('inventory')}
              className={`${
                activeTab === 'inventory'
                  ? 'border-[var(--accent-subtle)] text-[var(--accent-subtle)]'
                  : 'border-transparent text-[var(--foreground-muted)] hover:text-[var(--accent-subtle)] hover:border-[var(--border-subtle)]'
              } whitespace-nowrap py-3 px-1 border-b font-medium tracking-[0.18em] uppercase transition-colors`}
            >
              Inventory
            </button>
            <button
              onClick={() => setActiveTab('discounts')}
              className={`${
                activeTab === 'discounts'
                  ? 'border-[var(--accent-subtle)] text-[var(--accent-subtle)]'
                  : 'border-transparent text-[var(--foreground-muted)] hover:text-[var(--accent-subtle)] hover:border-[var(--border-subtle)]'
              } whitespace-nowrap py-3 px-1 border-b font-medium tracking-[0.18em] uppercase transition-colors`}
            >
              Discounts ({discounts?.length || 0})
            </button>
          </nav>
        </div>

        {/* Products Tab */}
        {activeTab === 'products' && (
          <div>
            <div className="mb-6 flex justify-between items-center text-xs">
              <h2 className="tracking-[0.18em] uppercase text-[var(--foreground-muted)]">Products</h2>
              <button
                onClick={() => setActiveModal('product')}
                className="fp-pill-button flex items-center gap-2 text-[10px]"
              >
                <span>+</span> Add Product
              </button>
            </div>

            {productsLoading ? (
              <div className="text-center py-12 text-xs text-[var(--foreground-muted)]">Loading products...</div>
            ) : products && products.length > 0 ? (
              <div className="fp-panel overflow-hidden">
                <table className="min-w-full divide-y divide-[var(--border-subtle)] text-xs">
                  <thead className="bg-black/40">
                    <tr>
                      <th className="px-6 py-3 text-left text-[10px] font-medium text-[var(--foreground-muted)] uppercase tracking-[0.18em]">
                        SKU
                      </th>
                      <th className="px-6 py-3 text-left text-[10px] font-medium text-[var(--foreground-muted)] uppercase tracking-[0.18em]">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-[10px] font-medium text-[var(--foreground-muted)] uppercase tracking-[0.18em]">
                        Category
                      </th>
                      <th className="px-6 py-3 text-left text-[10px] font-medium text-[var(--foreground-muted)] uppercase tracking-[0.18em]">
                        Base Price
                      </th>
                      <th className="px-6 py-3 text-left text-[10px] font-medium text-[var(--foreground-muted)] uppercase tracking-[0.18em]">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--border-subtle)]">
                    {products.map((product) => (
                      <tr key={product.sku} className="hover:bg-black/40">
                        <td className="px-6 py-3 whitespace-nowrap font-medium">
                          {product.sku}
                        </td>
                        <td className="px-6 py-3 whitespace-nowrap">
                          {product.name}
                        </td>
                        <td className="px-6 py-3 whitespace-nowrap text-[var(--foreground-muted)]">
                          {product.category || '-'}
                        </td>
                        <td className="px-6 py-3 whitespace-nowrap">
                          ${product.base_price.toFixed(2)}
                        </td>
                        <td className="px-6 py-3 whitespace-nowrap">
                          <Link
                            href={`/product/${product.sku}`}
                            className="text-[11px] tracking-[0.16em] uppercase text-[var(--accent-subtle)] hover:text-[var(--accent)]"
                          >
                            View
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12 fp-panel">
                <p className="text-[var(--foreground-muted)] text-xs">No products found</p>
              </div>
            )}
          </div>
        )}

        {/* Discounts Tab */}
        {activeTab === 'discounts' && (
          <div>
            <div className="mb-6 flex justify-between items-center text-xs">
              <h2 className="tracking-[0.18em] uppercase text-[var(--foreground-muted)]">Discounts</h2>
            </div>

            {discountsLoading ? (
              <div className="text-center py-12 text-xs text-[var(--foreground-muted)]">Loading discounts...</div>
            ) : discounts && discounts.length > 0 ? (
              <div className="fp-panel overflow-hidden">
                <table className="min-w-full divide-y divide-[var(--border-subtle)] text-xs">
                  <thead className="bg-black/40">
                    <tr>
                      <th className="px-6 py-3 text-left text-[10px] font-medium text-[var(--foreground-muted)] uppercase tracking-[0.18em]">
                        SKU
                      </th>
                      <th className="px-6 py-3 text-left text-[10px] font-medium text-[var(--foreground-muted)] uppercase tracking-[0.18em]">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-[10px] font-medium text-[var(--foreground-muted)] uppercase tracking-[0.18em]">
                        Value
                      </th>
                      <th className="px-6 py-3 text-left text-[10px] font-medium text-[var(--foreground-muted)] uppercase tracking-[0.18em]">
                        Priority
                      </th>
                      <th className="px-6 py-3 text-left text-[10px] font-medium text-[var(--foreground-muted)] uppercase tracking-[0.18em]">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-[10px] font-medium text-[var(--foreground-muted)] uppercase tracking-[0.18em]">
                        Valid Until
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--border-subtle)]">
                    {discounts.map((discount) => (
                      <tr key={discount.id} className="hover:bg-black/40">
                        <td className="px-6 py-3 whitespace-nowrap font-medium">
                          {discount.sku}
                        </td>
                        <td className="px-6 py-3 whitespace-nowrap">
                          {discount.discount_type}
                        </td>
                        <td className="px-6 py-3 whitespace-nowrap">
                          {discount.discount_type === 'percentage' 
                            ? `${discount.value}%` 
                            : `$${discount.value}`}
                        </td>
                        <td className="px-6 py-3 whitespace-nowrap">
                          {discount.priority}
                        </td>
                        <td className="px-6 py-3 whitespace-nowrap">
                          <span
                            className={`px-2 inline-flex text-[10px] leading-5 font-semibold rounded-full border ${
                              discount.is_active
                                ? 'border-[var(--accent-subtle)] text-[var(--accent-subtle)]'
                                : 'border-[var(--foreground-muted)] text-[var(--foreground-muted)]'
                            }`}
                          >
                            {discount.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-3 whitespace-nowrap text-[var(--foreground-muted)]">
                          {discount.end_date 
                            ? new Date(discount.end_date).toLocaleDateString() 
                            : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12 fp-panel">
                <p className="text-[var(--foreground-muted)] text-xs">No discounts found</p>
              </div>
            )}
          </div>
        )}

        {/* Inventory Tab */}
        {activeTab === 'inventory' && (
          <div>
            <div className="mb-6 flex justify-between items-center text-xs">
              <h2 className="tracking-[0.18em] uppercase text-[var(--foreground-muted)]">Inventory Batches</h2>
              <button
                onClick={() => setActiveModal('inventory')}
                className="fp-pill-button flex items-center gap-2 text-[10px]"
              >
                <span>+</span> Add Inventory Batch
              </button>
            </div>

            <div className="fp-panel p-8 text-center text-xs">
              <p className="text-[var(--foreground-muted)]">
                Inventory batch management will be available here.
              </p>
              <p className="text-[var(--foreground-muted)] mt-2">
                Click &quot;Add Inventory Batch&quot; to add new inventory with expiry dates.
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Modals */}
      <Modal
        isOpen={activeModal === 'product'}
        onClose={() => setActiveModal(null)}
        title="Create New Product"
      >
        <ProductForm
          onSuccess={handleProductSuccess}
          onCancel={() => setActiveModal(null)}
        />
      </Modal>

      <Modal
        isOpen={activeModal === 'inventory'}
        onClose={() => setActiveModal(null)}
        title="Add Inventory Batch"
      >
        <InventoryForm
          onSuccess={handleInventorySuccess}
          onCancel={() => setActiveModal(null)}
        />
      </Modal>
    </div>
  );
}
