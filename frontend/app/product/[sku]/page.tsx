'use client';

import { useParams } from 'next/navigation';
import useSWR from 'swr';
import { api } from '@/lib/api';
import { Product, Inventory, Discount } from '@/types';
import Link from 'next/link';

const productFetcher = (sku: string) => api.getProduct(sku).then(res => res.data);
const inventoryFetcher = (sku: string) => api.getInventory(sku).then(res => res.data);
const discountsFetcher = (sku: string) => api.getActiveDiscounts(sku).then(res => res.data);

export default function ProductDetailPage() {
  const params = useParams();
  const sku = params.sku as string;

  const { data: product, error: productError, isLoading: productLoading } = useSWR<Product>(
    sku ? `/product/${sku}` : null,
    () => productFetcher(sku),
    { refreshInterval: 30000 }
  );

  const { data: inventory } = useSWR<Inventory>(
    sku ? `/inventory/${sku}` : null,
    () => inventoryFetcher(sku),
    { refreshInterval: 10000 }
  );

  const { data: discounts } = useSWR<Discount[]>(
    sku ? `/discounts/${sku}` : null,
    () => discountsFetcher(sku),
    { refreshInterval: 30000 }
  );

  if (productLoading) {
    return (
      <div className="min-h-screen fp-shell">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-white/10 rounded w-1/4 mb-8" />
            <div className="grid md:grid-cols-2 gap-8">
              <div className="aspect-square bg-white/10 rounded-lg" />
              <div className="space-y-4">
                <div className="h-8 bg-white/10 rounded w-3/4" />
                <div className="h-4 bg-white/10 rounded w-1/4" />
                <div className="h-12 bg-white/10 rounded w-1/2" />
                <div className="h-24 bg-white/10 rounded" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (productError || !product) {
    return (
      <div className="min-h-screen fp-shell">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <p className="text-[var(--danger)] text-xs tracking-[0.12em] uppercase mb-4">Product not found</p>
            <Link href="/" className="text-[var(--accent-subtle)] text-xs tracking-[0.12em] uppercase hover:text-[var(--accent)]">
              ← Back to products
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const activeDiscounts = discounts?.filter(d => d.is_active) || [];
  const totalDiscount = activeDiscounts.reduce((sum, d) => {
    if (d.discount_type === 'percentage') {
      return sum + (product.base_price * d.value / 100);
    } else if (d.discount_type === 'fixed') {
      return sum + d.value;
    }
    return sum;
  }, 0);

  const finalPrice = Math.max(0, product.base_price - totalDiscount);
  const inStock = inventory && inventory.quantity > 0;

  return (
    <div className="min-h-screen fp-shell">
      <header className="fp-shell-header">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link href="/" className="text-[var(--accent-subtle)] hover:text-[var(--accent)] flex items-center gap-2 text-xs tracking-[0.12em] uppercase">
            <span>←</span> Back to products
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Product Image */}
          <div className="aspect-square fp-panel flex items-center justify-center border border-[var(--border-subtle)]">
            <span className="text-[var(--foreground-muted)] text-9xl">📦</span>
          </div>

          {/* Product Details */}
          <div className="fp-panel p-6">
            <h1 className="text-2xl font-bold text-[var(--accent-subtle)] tracking-[0.12em] uppercase mb-2">{product.name}</h1>
            
            {product.category && (
              <p className="text-[10px] text-[var(--foreground-muted)] mb-4 uppercase tracking-[0.16em]">
                {product.category}
              </p>
            )}

            <div className="mb-6">
              {activeDiscounts.length > 0 ? (
                <>
                  <div className="flex items-baseline gap-3 mb-2">
                    <span className="text-3xl font-bold text-[var(--accent-subtle)] fp-card-price">
                      ${finalPrice.toFixed(2)}
                    </span>
                    <span className="text-lg text-[var(--foreground-muted)] line-through fp-card-price">
                      ${product.base_price.toFixed(2)}
                    </span>
                  </div>
                  <p className="text-xs text-[var(--accent-subtle)] font-medium tracking-[0.12em] uppercase">
                    Save ${totalDiscount.toFixed(2)} ({((totalDiscount / product.base_price) * 100).toFixed(0)}% off)
                  </p>
                </>
              ) : (
                <span className="text-3xl font-bold text-[var(--accent-subtle)] fp-card-price">
                  ${product.base_price.toFixed(2)}
                </span>
              )}
            </div>

            {/* Stock Status */}
            {inventory && (
              <div className="mb-6">
                {inStock ? (
                  <div className="flex items-center gap-2 text-[var(--accent-subtle)]">
                    <span className="w-2 h-2 bg-[var(--accent-subtle)] rounded-full" />
                    <span className="text-[10px] font-medium tracking-[0.12em] uppercase">In Stock ({inventory.quantity} available)</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-[var(--danger)]">
                    <span className="w-2 h-2 bg-[var(--danger)] rounded-full" />
                    <span className="text-[10px] font-medium tracking-[0.12em] uppercase">Out of Stock</span>
                  </div>
                )}
              </div>
            )}

            {/* Description */}
            {product.description && (
              <div className="mb-6">
                <h2 className="text-[10px] font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-2">Description</h2>
                <p className="text-xs text-[var(--foreground)]">{product.description}</p>
              </div>
            )}

            {/* Product Details */}
            <div className="border-t border-[var(--border-subtle)] pt-6 mb-6">
              <h2 className="text-[10px] font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-3">Product Details</h2>
              <dl className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <dt className="text-[var(--foreground-muted)] tracking-[0.12em] uppercase">SKU:</dt>
                  <dd className="font-medium text-[var(--accent-subtle)] fp-card-price">{product.sku}</dd>
                </div>
                {product.category && (
                  <div className="flex justify-between">
                    <dt className="text-[var(--foreground-muted)] tracking-[0.12em] uppercase">Category:</dt>
                    <dd className="font-medium text-[var(--accent-subtle)]">{product.category}</dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Active Discounts */}
            {activeDiscounts.length > 0 && (
              <div className="border-t border-[var(--border-subtle)] pt-6">
                <h2 className="text-[10px] font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-3">Active Discounts</h2>
                <div className="space-y-2">
                  {activeDiscounts.map((discount, idx) => (
                    <div key={idx} className="bg-white/5 border border-[var(--border-subtle)] rounded-lg p-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-xs font-medium text-[var(--accent-subtle)] tracking-[0.12em] uppercase">
                            {discount.discount_type === 'percentage' 
                              ? `${discount.value}% off` 
                              : `$${discount.value} off`}
                          </p>
                          {discount.min_quantity && (
                            <p className="text-[10px] text-[var(--foreground-muted)] tracking-[0.12em] uppercase">
                              Min. quantity: {discount.min_quantity}
                            </p>
                          )}
                        </div>
                        <span className="text-[10px] bg-white/10 text-[var(--foreground-muted)] px-2 py-1 rounded tracking-[0.12em] uppercase">
                          Priority: {discount.priority}
                        </span>
                      </div>
                      {discount.end_date && (
                        <p className="text-[10px] text-[var(--foreground-muted)] mt-1 tracking-[0.12em] uppercase">
                          Valid until: {new Date(discount.end_date).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
