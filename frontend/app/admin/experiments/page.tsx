'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface ExperimentStatus {
  totalProducts: number;
  assignedProducts: number;
  unassignedProducts: number;
  controlCount: number;
  mlVariantCount: number;
  experimentActive: boolean;
}

interface ExperimentComparison {
  control: {
    experimentGroup: string;
    totalProducts: number;
    totalImpressions: number;
    totalConversions: number;
    totalRevenue: number;
    totalUnitsSold: number;
    avgDiscountPct: number;
    conversionRate: number;
    revenuePerProduct: number;
  };
  mlVariant: {
    experimentGroup: string;
    totalProducts: number;
    totalImpressions: number;
    totalConversions: number;
    totalRevenue: number;
    totalUnitsSold: number;
    avgDiscountPct: number;
    conversionRate: number;
    revenuePerProduct: number;
  };
  conversionLift: number;
  revenueLift: number;
  unitsLift: number;
  periodStart: string;
  periodEnd: string;
}

interface WinningVariant {
  winner: string | null;
  metric: string;
  controlValue: number;
  mlVariantValue: number;
  improvementPct: number;
  confidence: string;
  sampleSize: number;
  message: string;
  recommendation: string;
}

export default function ExperimentsPage() {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<ExperimentStatus | null>(null);
  const [comparison, setComparison] = useState<ExperimentComparison | null>(null);
  const [winner, setWinner] = useState<WinningVariant | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(7);

  const loadExperimentData = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [statusRes, comparisonRes, winnerRes] = await Promise.all([
        api.getExperimentStatus(),
        api.getExperimentComparison(days),
        api.getWinningVariant(days, 'conversion_rate'),
      ]);

      setStatus(statusRes.data);
      setComparison(comparisonRes.data);
      setWinner(winnerRes.data);
    } catch (err) {
      console.error('Failed to load experiment data:', err);
      const errorMessage = err && typeof err === 'object' && 'response' in err 
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail 
        : 'Failed to load experiment data';
      setError(errorMessage || 'Failed to load experiment data');
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => {
    loadExperimentData();
  }, [loadExperimentData]);

  const handleAssignRandom = async () => {
    try {
      await api.assignRandomExperiment(0.5);
      await loadExperimentData();
      alert('Products randomly assigned to experiment groups (50/50 split)');
    } catch {
      alert('Failed to assign experiments');
    }
  };

  const handleReset = async () => {
    if (confirm('Reset all experiment assignments? This cannot be undone.')) {
      try {
        await api.resetExperiments();
        await loadExperimentData();
        alert('Experiments reset successfully');
      } catch {
        alert('Failed to reset experiments');
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">A/B Experiments</h1>
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
          <h1 className="text-4xl font-bold text-gray-900 mb-8">A/B Experiments</h1>
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-red-800 mb-2">Error</h2>
            <p className="text-red-600">{error}</p>
            <button
              onClick={loadExperimentData}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">A/B Experiments</h1>
            <p className="text-gray-600">Compare ML vs Rule-Based Discount Recommendations</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleAssignRandom}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Assign Random (50/50)
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              Reset Experiments
            </button>
          </div>
        </div>

        {/* Time Period Selector */}
        <div className="mb-6 bg-white rounded-lg shadow p-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Analysis Period
          </label>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value={1}>Last 24 hours</option>
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
          </select>
        </div>

        {/* Status Cards */}
        {status && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Total Products</p>
              <p className="text-2xl font-bold text-gray-900">{status.totalProducts}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Assigned</p>
              <p className="text-2xl font-bold text-blue-600">{status.assignedProducts}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Unassigned</p>
              <p className="text-2xl font-bold text-gray-600">{status.unassignedProducts}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Control Group</p>
              <p className="text-2xl font-bold text-orange-600">{status.controlCount}</p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">ML Variant</p>
              <p className="text-2xl font-bold text-purple-600">{status.mlVariantCount}</p>
            </div>
          </div>
        )}

        {/* Winner Card */}
        {winner && (
          <div className={`mb-8 rounded-lg shadow-lg p-6 ${
            winner.winner === 'ML_VARIANT' ? 'bg-gradient-to-r from-purple-50 to-purple-100 border-2 border-purple-300' :
            winner.winner === 'CONTROL' ? 'bg-gradient-to-r from-orange-50 to-orange-100 border-2 border-orange-300' :
            'bg-gray-50'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  {winner.winner === 'ML_VARIANT' ? '🏆 ML Variant is Winning!' :
                   winner.winner === 'CONTROL' ? '🏆 Control is Winning!' :
                   '⚖️ Both Performing Equally'}
                </h2>
                <p className="text-gray-700 mb-1">{winner.message}</p>
                <p className="text-sm text-gray-600">Confidence: <span className="font-semibold">{winner.confidence}</span> (sample: {winner.sampleSize})</p>
              </div>
              <div className="text-right">
                <p className="text-4xl font-bold text-gray-900">
                  {winner.improvementPct > 0 ? '+' : ''}{winner.improvementPct.toFixed(1)}%
                </p>
                <p className="text-sm text-gray-600 mt-1">improvement</p>
              </div>
            </div>
            <div className="mt-4 p-3 bg-white rounded border border-gray-200">
              <p className="text-sm text-gray-700">
                <strong>💡 Recommendation:</strong> {winner.recommendation}
              </p>
            </div>
          </div>
        )}

        {/* Comparison Table */}
        {comparison && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Performance Comparison</h2>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Metric
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-orange-600 uppercase tracking-wider">
                      Control (Rule-Based)
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-purple-600 uppercase tracking-wider">
                      ML Variant
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-green-600 uppercase tracking-wider">
                      Lift
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      Conversion Rate
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      {comparison.control.conversionRate.toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      {comparison.mlVariant.conversionRate.toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold text-green-600">
                      {comparison.conversionLift > 0 ? '+' : ''}{comparison.conversionLift.toFixed(1)}%
                    </td>
                  </tr>
                  
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      Revenue per Product
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      ${comparison.control.revenuePerProduct.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      ${comparison.mlVariant.revenuePerProduct.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold text-green-600">
                      {comparison.revenueLift > 0 ? '+' : ''}{comparison.revenueLift.toFixed(1)}%
                    </td>
                  </tr>
                  
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      Units Sold
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      {comparison.control.totalUnitsSold}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      {comparison.mlVariant.totalUnitsSold}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold text-green-600">
                      {comparison.unitsLift > 0 ? '+' : ''}{comparison.unitsLift.toFixed(1)}%
                    </td>
                  </tr>
                  
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      Total Revenue
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      ${comparison.control.totalRevenue.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      ${comparison.mlVariant.totalRevenue.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      ${(comparison.mlVariant.totalRevenue - comparison.control.totalRevenue).toFixed(2)}
                    </td>
                  </tr>
                  
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      Avg Discount
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      {comparison.control.avgDiscountPct.toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      {comparison.mlVariant.avgDiscountPct.toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                      {(comparison.mlVariant.avgDiscountPct - comparison.control.avgDiscountPct).toFixed(1)}pp
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Insights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">How It Works</h3>
            <ul className="space-y-2 text-sm text-blue-800">
              <li className="flex items-start">
                <span className="mr-2">🎯</span>
                <span><strong>Control Group:</strong> Uses rule-based discount logic based on expiry, inventory, and category</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">🤖</span>
                <span><strong>ML Variant:</strong> Uses XGBoost model to predict optimal discount based on historical data</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">📊</span>
                <span>Products are randomly assigned 50/50 to each group for fair comparison</span>
              </li>
            </ul>
          </div>
          
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-green-900 mb-3">Success Metrics</h3>
            <ul className="space-y-2 text-sm text-green-800">
              <li className="flex items-start">
                <span className="mr-2">💰</span>
                <span><strong>Revenue Lift:</strong> Percentage increase in revenue per product</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">🎯</span>
                <span><strong>Conversion Lift:</strong> Improvement in purchase probability</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">📈</span>
                <span><strong>Units Lift:</strong> Additional units sold with ML recommendations</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
