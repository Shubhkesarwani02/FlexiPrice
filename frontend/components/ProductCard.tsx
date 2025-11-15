import Link from 'next/link';
import { ProductWithStorefrontPrice } from '@/types';

interface ProductCardProps {
  product: ProductWithStorefrontPrice;
}

export default function ProductCard({ product }: ProductCardProps) {
  const basePrice = product.base_price || product.basePrice;
  const storefrontPrice = product.storefront_price;
  const discountPct = product.discount_pct;
  const hasDiscount = discountPct && discountPct > 0;
  const savings = basePrice - storefrontPrice;

  return (
    <Link href={`/product/${product.sku}`}>
      <div className="group border border-gray-200 rounded-xl p-5 hover:shadow-xl hover:border-blue-300 transition-all duration-300 cursor-pointer bg-white">
        {/* Product Image */}
        <div className="relative aspect-square bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg mb-4 flex items-center justify-center overflow-hidden">
          <span className="text-6xl group-hover:scale-110 transition-transform duration-300">📦</span>
          {hasDiscount && (
            <div className="absolute top-2 right-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-lg">
              -{discountPct.toFixed(0)}%
            </div>
          )}
        </div>
        
        {/* Product Info */}
        <div className="space-y-2">
          <h3 className="font-semibold text-lg mb-1 truncate text-gray-900 group-hover:text-blue-600 transition-colors">
            {product.name}
          </h3>
          
          {product.category && (
            <p className="text-xs text-gray-500 uppercase tracking-wider font-medium">
              {product.category}
            </p>
          )}
          
          {/* Price Display */}
          <div className="pt-2">
            {hasDiscount ? (
              <>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl font-bold text-green-600">
                    ${storefrontPrice.toFixed(2)}
                  </span>
                  <span className="text-base text-gray-400 line-through font-medium">
                    ${basePrice.toFixed(2)}
                  </span>
                </div>
                <div className="inline-block bg-green-100 text-green-800 text-xs font-semibold px-2.5 py-1 rounded-md">
                  💰 Save ${savings.toFixed(2)}
                </div>
              </>
            ) : (
              <span className="text-2xl font-bold text-gray-900">
                ${storefrontPrice.toFixed(2)}
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
