export interface Product {
  id: number;
  sku: string;
  name: string;
  base_price: number | string;
  basePrice: number | string; // API alias
  category?: string;
  description?: string;
  created_at?: string;
  createdAt?: string; // API alias
  updated_at?: string;
  updatedAt?: string; // API alias
}

export interface ProductWithStorefrontPrice extends Product {
  storefront_price: number | string;
  discount_pct?: number | string | null;
}

export interface Inventory {
  sku: string;
  quantity: number;
  reserved_quantity: number;
  last_updated: string;
}

export interface Discount {
  id: string;
  sku: string;
  discount_type: 'percentage' | 'fixed' | 'bundle' | 'tiered';
  value: number;
  min_quantity?: number;
  start_date?: string;
  end_date?: string;
  is_active: boolean;
  priority: number;
}

export interface ComputedPrice {
  sku: string;
  base_price: number;
  final_price: number;
  discounts_applied: Discount[];
  savings: number;
}

export interface ProductWithPrice extends Product {
  computed_price?: ComputedPrice;
  inventory?: Inventory;
}
