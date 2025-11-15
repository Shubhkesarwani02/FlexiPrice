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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="border border-gray-200 rounded-xl p-5 animate-pulse bg-white">
            <div className="aspect-square bg-gradient-to-br from-gray-200 to-gray-300 rounded-lg mb-4" />
            <div className="space-y-3">
              <div className="h-5 bg-gray-200 rounded w-3/4" />
              <div className="h-3 bg-gray-200 rounded w-1/2" />
              <div className="h-8 bg-gray-200 rounded w-2/3" />
              <div className="h-6 bg-gray-200 rounded w-1/3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-16 px-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 max-w-md mx-auto">
          <div className="text-5xl mb-4">⚠️</div>
          <h3 className="text-xl font-semibold text-red-800 mb-2">Error Loading Products</h3>
          <p className="text-red-600 text-sm mb-4">{error.message}</p>
          <button
            onClick={() => mutate()}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!products || products.length === 0) {
    return (
      <div className="text-center py-16 px-4">
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 max-w-md mx-auto">
          <div className="text-6xl mb-4">📦</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">No Products Available</h3>
          <p className="text-gray-600 text-sm">Check back later for new products</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Results Count */}
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm text-gray-600">
          Showing <span className="font-semibold text-gray-900">{products.length}</span> products
        </p>
        <button
          onClick={() => mutate()}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
        >
          <span>🔄</span> Refresh Prices
        </button>
      </div>

      {/* Product Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {products.map((product) => (
          <ProductCard key={product.sku} product={product} />
        ))}
      </div>
    </>
  );
}
