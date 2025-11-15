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
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">Analytics Dashboard</h1>
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">Analytics Dashboard</h1>
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading Analytics</h2>
            <p className="text-red-600">{error}</p>
            <button
              onClick={loadAnalytics}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
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
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">Analytics Dashboard</h1>
          <p className="text-gray-600">No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
          <p className="text-gray-600">
            Sales performance and discount effectiveness insights
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Total Revenue</p>
            <p className="text-2xl font-bold text-green-600">
              ${parseFloat(data.summary.totalRevenue.toString()).toFixed(2)}
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Units Sold</p>
            <p className="text-2xl font-bold text-blue-600">
              {data.summary.totalUnitsSold}
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Avg Discount</p>
            <p className="text-2xl font-bold text-orange-600">
              {parseFloat(data.summary.avgDiscountPct.toString()).toFixed(1)}%
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">With Discount</p>
            <p className="text-2xl font-bold text-purple-600">
              {data.summary.productsWithDiscount}
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-1">Expiring Soon</p>
            <p className="text-2xl font-bold text-red-600">
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
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">
                Category Performance
              </h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Category
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Units Sold
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Revenue
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Discount
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {data.categoryPerformance.map((category, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {category.category}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                          {category.totalUnitsSold}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-green-600 font-semibold">
                          ${parseFloat(category.totalRevenue.toString()).toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-orange-600">
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
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh Analytics
          </button>
        </div>
      </div>
    </div>
  );
}
