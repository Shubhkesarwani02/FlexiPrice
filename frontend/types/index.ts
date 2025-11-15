export interface Product {
  sku: string;
  name: string;
  base_price: number;
  category?: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
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
