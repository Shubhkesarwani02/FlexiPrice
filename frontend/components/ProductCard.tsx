import Link from 'next/link';
import { ProductWithPrice } from '@/types';

interface ProductCardProps {
  product: ProductWithPrice;
}

export default function ProductCard({ product }: ProductCardProps) {
  const hasDiscount = product.computed_price && product.computed_price.savings > 0;
  const finalPrice = product.computed_price?.final_price ?? product.base_price;
  const savings = product.computed_price?.savings ?? 0;

  return (
    <Link href={`/product/${product.sku}`}>
      <div className="border rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer bg-white">
        <div className="aspect-square bg-gray-200 rounded-md mb-4 flex items-center justify-center">
          <span className="text-gray-400 text-4xl">📦</span>
        </div>
        
        <h3 className="font-semibold text-lg mb-2 truncate">{product.name}</h3>
        
        {product.category && (
          <p className="text-sm text-gray-500 mb-2">{product.category}</p>
        )}
        
        <div className="flex items-baseline gap-2 mb-2">
          {hasDiscount ? (
            <>
              <span className="text-2xl font-bold text-green-600">
                ${finalPrice.toFixed(2)}
              </span>
              <span className="text-sm text-gray-500 line-through">
                ${product.base_price.toFixed(2)}
              </span>
            </>
          ) : (
            <span className="text-2xl font-bold text-gray-900">
              ${finalPrice.toFixed(2)}
            </span>
          )}
        </div>
        
        {hasDiscount && (
          <div className="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded">
            Save ${savings.toFixed(2)} ({((savings / product.base_price) * 100).toFixed(0)}% off)
          </div>
        )}
        
        {product.inventory && (
          <p className="text-xs text-gray-500 mt-2">
            {product.inventory.quantity > 0 
              ? `${product.inventory.quantity} in stock` 
              : 'Out of stock'}
          </p>
        )}
      </div>
    </Link>
  );
}
