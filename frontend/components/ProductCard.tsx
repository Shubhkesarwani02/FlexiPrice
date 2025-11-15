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
      <div className="group fp-card cursor-pointer">
        {/* Product Image / Glyph */}
        <div className="relative mb-4 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="h-10 w-10 rounded-md border border-[var(--border-strong)] flex items-center justify-center text-xs tracking-[0.16em] uppercase text-[var(--foreground-muted)]">
              SKU
            </div>
            <div className="min-w-0">
              <h3 className="fp-card-title truncate group-hover:text-[var(--accent)] transition-colors">
                {product.name}
              </h3>
              {product.category && (
                <p className="fp-card-meta mt-1 truncate">
                  {product.category}
                </p>
              )}
            </div>
          </div>
          {hasDiscount && (
            <div className="fp-badge fp-badge-danger">
              -{discountPct.toFixed(0)}%
            </div>
          )}
        </div>

        {/* Price Display */}
        <div className="flex items-end justify-between gap-4 fp-card-price">
          <div>
            {hasDiscount ? (
              <>
                <div className="flex items-baseline gap-2 mb-1">
                  <span className="text-lg font-semibold text-[var(--accent)]">
                    ${storefrontPrice.toFixed(2)}
                  </span>
                  <span className="text-xs line-through text-[var(--foreground-muted)]">
                    ${basePrice.toFixed(2)}
                  </span>
                </div>
                <div className="fp-chip-save text-[var(--accent-subtle)]">
                  Save ${savings.toFixed(2)}
                </div>
              </>
            ) : (
              <span className="text-lg font-semibold text-[var(--accent)]">
                ${storefrontPrice.toFixed(2)}
              </span>
            )}
          </div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--foreground-muted)]">
            View details
          </div>
        </div>
      </div>
    </Link>
  );
}
