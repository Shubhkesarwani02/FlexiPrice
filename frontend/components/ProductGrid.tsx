'use client';

import { ProductWithStorefrontPrice } from '@/types';
import useSWR from 'swr';
import { api } from '@/lib/api';
import ProductCard from '@/components/ProductCard';

const fetcher = () => api.getProducts().then(res => res.data);

export default function ProductGrid() {
  const { data: products, error, isLoading, mutate } = useSWR<ProductWithStorefrontPrice[]>(
    '/products',
    fetcher,
    {
      refreshInterval: 30000, // Refresh every 30 seconds for real-time pricing
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
    }
  );

  if (isLoading) {
    return (
      <div className="fp-grid">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="fp-card animate-pulse">
            <div className="h-24 w-full rounded-md bg-[#111111] mb-4" />
            <div className="space-y-3">
              <div className="h-4 bg-[#111111] rounded w-3/4" />
              <div className="h-3 bg-[#111111] rounded w-1/2" />
              <div className="h-6 bg-[#111111] rounded w-2/3" />
              <div className="h-5 bg-[#111111] rounded w-1/3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-16 px-4">
        <div className="fp-panel max-w-md mx-auto p-8 border border-[var(--danger)]">
          <h3 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--danger)] mb-3">
            Error Loading Products
          </h3>
          <p className="text-xs text-[var(--foreground-muted)] mb-4 fp-card-price">
            {error.message}
          </p>
          <button
            onClick={() => mutate()}
            className="fp-pill-button text-[10px] tracking-[0.18em] uppercase border-[var(--danger)]"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!products || products.length === 0) {
    return (
      <div className="text-center py-16 px-4">
        <div className="fp-panel max-w-md mx-auto p-10">
          <h3 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--foreground-muted)] mb-3">
            No Products Available
          </h3>
          <p className="text-xs text-[var(--foreground-muted)]">
            Once products exist in the system, they will appear here with
            live pricing and discount signals.
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Results Count */}
      <div className="mb-4 flex items-center justify-between">
        <p className="text-[11px] text-[var(--foreground-muted)] tracking-[0.16em] uppercase">
          Showing <span className="text-[var(--accent)]">{products.length}</span> products
        </p>
        <button
          onClick={() => mutate()}
          className="fp-pill-button text-[10px] tracking-[0.18em] uppercase"
        >
          Refresh Prices
        </button>
      </div>

      {/* Product Grid */}
      <div className="fp-grid">
        {products.map((product) => (
          <ProductCard key={product.sku} product={product} />
        ))}
      </div>
    </>
  );
}
