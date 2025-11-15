'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import SalesVsExpiryChart from '@/components/SalesVsExpiryChart';
import DiscountVsUnitsChart from '@/components/DiscountVsUnitsChart';

interface AnalyticsSummary {
  totalRevenue: number;
  totalUnitsSold: number;
  avgDiscountPct: number;
  productsWithDiscount: number;
  productsExpiringSoon: number;
}

interface SalesVsExpiryData {
  daysToExpiry: number;
  totalUnitsSold: number;
  totalRevenue: number;
  avgDiscountPct: number;
  productCount: number;
}

interface DiscountVsUnitsData {
  discountRange: string;
  discountAvg: number;
  totalUnitsSold: number;
  totalRevenue: number;
  transactionCount: number;
  conversionRate: number;
}

interface CategoryPerformance {
  category: string;
  totalUnitsSold: number;
  totalRevenue: number;
  avgDiscountPct: number;
}

interface AnalyticsDashboard {
  summary: AnalyticsSummary;
  salesVsExpiry: SalesVsExpiryData[];
  discountVsUnits: DiscountVsUnitsData[];
  categoryPerformance: CategoryPerformance[];
}

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AnalyticsDashboard | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getAnalyticsDashboard();
      setData(response.data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
      const errorMessage = err && typeof err === 'object' && 'response' in err 
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail 
        : 'Failed to load analytics data';
      setError(errorMessage || 'Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen fp-shell p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-8">Analytics Dashboard</h1>
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--accent-subtle)]"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen fp-shell p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-8">Analytics Dashboard</h1>
          <div className="fp-panel p-6 border border-[var(--danger)]">
            <h2 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--danger)] mb-2">Error Loading Analytics</h2>
            <p className="text-xs text-[var(--foreground-muted)] mb-4">{error}</p>
            <button
              onClick={loadAnalytics}
              className="fp-pill-button text-[10px] border-[var(--danger)]"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen fp-shell p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-8">Analytics Dashboard</h1>
          <p className="text-xs text-[var(--foreground-muted)]">No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen fp-shell p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-2">Analytics Dashboard</h1>
          <p className="text-[10px] text-[var(--foreground-muted)] tracking-[0.12em] uppercase">
            Sales performance and discount effectiveness insights
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8 text-xs">
          <div className="fp-panel p-6 border border-[var(--border-subtle)]">
            <p className="text-[10px] text-[var(--foreground-muted)] mb-1 tracking-[0.16em] uppercase">Total Revenue</p>
            <p className="text-xl font-bold text-[var(--accent-subtle)] fp-card-price">
              ${parseFloat(data.summary.totalRevenue.toString()).toFixed(2)}
            </p>
          </div>
          
          <div className="fp-panel p-6 border border-[var(--border-subtle)]">
            <p className="text-[10px] text-[var(--foreground-muted)] mb-1 tracking-[0.16em] uppercase">Units Sold</p>
            <p className="text-xl font-bold text-[var(--accent-subtle)] fp-card-price">
              {data.summary.totalUnitsSold}
            </p>
          </div>
          
          <div className="fp-panel p-6 border border-[var(--border-subtle)]">
            <p className="text-[10px] text-[var(--foreground-muted)] mb-1 tracking-[0.16em] uppercase">Avg Discount</p>
            <p className="text-xl font-bold text-[var(--accent-subtle)] fp-card-price">
              {parseFloat(data.summary.avgDiscountPct.toString()).toFixed(1)}%
            </p>
          </div>
          
          <div className="fp-panel p-6 border border-[var(--border-subtle)]">
            <p className="text-[10px] text-[var(--foreground-muted)] mb-1 tracking-[0.16em] uppercase">With Discount</p>
            <p className="text-xl font-bold text-[var(--accent-subtle)] fp-card-price">
              {data.summary.productsWithDiscount}
            </p>
          </div>
          
          <div className="fp-panel p-6 border border-[var(--border-subtle)]">
            <p className="text-[10px] text-[var(--foreground-muted)] mb-1 tracking-[0.16em] uppercase">Expiring Soon</p>
            <p className="text-xl font-bold text-[var(--accent-subtle)] fp-card-price">
              {data.summary.productsExpiringSoon}
            </p>
          </div>
        </div>

        {/* Charts */}
        <div className="space-y-8">
          {/* Sales vs Expiry Chart */}
          {data.salesVsExpiry.length > 0 && (
            <SalesVsExpiryChart data={data.salesVsExpiry} />
          )}

          {/* Discount vs Units Chart */}
          {data.discountVsUnits.length > 0 && (
            <DiscountVsUnitsChart data={data.discountVsUnits} />
          )}

          {/* Category Performance Table */}
          {data.categoryPerformance.length > 0 && (
            <div className="fp-panel">
              <h2 className="text-[10px] font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-6 px-6 pt-6">
                Category Performance
              </h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-[var(--border-subtle)]">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-[10px] font-semibold text-[var(--foreground-muted)] tracking-[0.16em] uppercase">
                        Category
                      </th>
                      <th className="px-6 py-3 text-right text-[10px] font-semibold text-[var(--foreground-muted)] tracking-[0.16em] uppercase">
                        Units Sold
                      </th>
                      <th className="px-6 py-3 text-right text-[10px] font-semibold text-[var(--foreground-muted)] tracking-[0.16em] uppercase">
                        Revenue
                      </th>
                      <th className="px-6 py-3 text-right text-[10px] font-semibold text-[var(--foreground-muted)] tracking-[0.16em] uppercase">
                        Avg Discount
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--border-subtle)]">
                    {data.categoryPerformance.map((category, idx) => (
                      <tr key={idx} className="hover:bg-white/5">
                        <td className="px-6 py-4 whitespace-nowrap text-xs font-medium text-[var(--foreground)]">
                          {category.category}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                          {category.totalUnitsSold}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] font-semibold fp-card-price">
                          ${parseFloat(category.totalRevenue.toString()).toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                          {parseFloat(category.avgDiscountPct.toString()).toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Refresh Button */}
        <div className="mt-8 flex justify-center">
          <button
            onClick={loadAnalytics}
            className="fp-pill-button text-[10px]"
          >
            Refresh Analytics
          </button>
        </div>
      </div>
    </div>
  );
}
