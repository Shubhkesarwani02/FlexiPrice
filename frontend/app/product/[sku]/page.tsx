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
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-8" />
            <div className="grid md:grid-cols-2 gap-8">
              <div className="aspect-square bg-gray-200 rounded-lg" />
              <div className="space-y-4">
                <div className="h-8 bg-gray-200 rounded w-3/4" />
                <div className="h-4 bg-gray-200 rounded w-1/4" />
                <div className="h-12 bg-gray-200 rounded w-1/2" />
                <div className="h-24 bg-gray-200 rounded" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (productError || !product) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <p className="text-red-600 mb-4">Product not found</p>
            <Link href="/" className="text-blue-600 hover:underline">
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
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link href="/" className="text-blue-600 hover:underline flex items-center gap-2">
            <span>←</span> Back to products
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Product Image */}
          <div className="aspect-square bg-white rounded-lg shadow-sm flex items-center justify-center">
            <span className="text-gray-300 text-9xl">📦</span>
          </div>

          {/* Product Details */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h1>
            
            {product.category && (
              <p className="text-sm text-gray-500 mb-4 uppercase tracking-wide">
                {product.category}
              </p>
            )}

            <div className="mb-6">
              {activeDiscounts.length > 0 ? (
                <>
                  <div className="flex items-baseline gap-3 mb-2">
                    <span className="text-4xl font-bold text-green-600">
                      ${finalPrice.toFixed(2)}
                    </span>
                    <span className="text-xl text-gray-500 line-through">
                      ${product.base_price.toFixed(2)}
                    </span>
                  </div>
                  <p className="text-green-600 font-medium">
                    Save ${totalDiscount.toFixed(2)} ({((totalDiscount / product.base_price) * 100).toFixed(0)}% off)
                  </p>
                </>
              ) : (
                <span className="text-4xl font-bold text-gray-900">
                  ${product.base_price.toFixed(2)}
                </span>
              )}
            </div>

            {/* Stock Status */}
            {inventory && (
              <div className="mb-6">
                {inStock ? (
                  <div className="flex items-center gap-2 text-green-600">
                    <span className="w-2 h-2 bg-green-600 rounded-full" />
                    <span className="font-medium">In Stock ({inventory.quantity} available)</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-red-600">
                    <span className="w-2 h-2 bg-red-600 rounded-full" />
                    <span className="font-medium">Out of Stock</span>
                  </div>
                )}
              </div>
            )}

            {/* Description */}
            {product.description && (
              <div className="mb-6">
                <h2 className="text-lg font-semibold mb-2">Description</h2>
                <p className="text-gray-600">{product.description}</p>
              </div>
            )}

            {/* Product Details */}
            <div className="border-t pt-6 mb-6">
              <h2 className="text-lg font-semibold mb-3">Product Details</h2>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-600">SKU:</dt>
                  <dd className="font-medium">{product.sku}</dd>
                </div>
                {product.category && (
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Category:</dt>
                    <dd className="font-medium">{product.category}</dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Active Discounts */}
            {activeDiscounts.length > 0 && (
              <div className="border-t pt-6">
                <h2 className="text-lg font-semibold mb-3">Active Discounts</h2>
                <div className="space-y-2">
                  {activeDiscounts.map((discount, idx) => (
                    <div key={idx} className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-green-900">
                            {discount.discount_type === 'percentage' 
                              ? `${discount.value}% off` 
                              : `$${discount.value} off`}
                          </p>
                          {discount.min_quantity && (
                            <p className="text-xs text-green-700">
                              Min. quantity: {discount.min_quantity}
                            </p>
                          )}
                        </div>
                        <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded">
                          Priority: {discount.priority}
                        </span>
                      </div>
                      {discount.end_date && (
                        <p className="text-xs text-green-600 mt-1">
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
