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
      <div className="min-h-screen fp-shell p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-8">A/B Experiments</h1>
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
          <h1 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-8">A/B Experiments</h1>
          <div className="fp-panel p-6 border border-[var(--danger)]">
            <h2 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--danger)] mb-2">Error</h2>
            <p className="text-xs text-[var(--foreground-muted)] mb-4">{error}</p>
            <button
              onClick={loadExperimentData}
              className="fp-pill-button text-[10px] border-[var(--danger)]"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen fp-shell p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-2">A/B Experiments</h1>
            <p className="text-[10px] text-[var(--foreground-muted)] tracking-[0.12em] uppercase">Compare ML vs Rule-Based Discount Recommendations</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleAssignRandom}
              className="fp-pill-button text-[10px]"
            >
              Assign Random (50/50)
            </button>
            <button
              onClick={handleReset}
              className="fp-pill-button text-[10px] border-[var(--foreground-muted)]"
            >
              Reset Experiments
            </button>
          </div>
        </div>

        {/* Time Period Selector */}
        <div className="mb-6 fp-panel p-4">
          <label className="block text-[10px] font-medium text-[var(--foreground-muted)] tracking-[0.16em] uppercase mb-2">
            Analysis Period
          </label>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-4 py-2 bg-black/40 border border-[var(--border-subtle)] text-[var(--foreground)] text-xs rounded"
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
            <div className="fp-panel p-6 border border-[var(--border-subtle)]">
              <p className="text-[10px] text-[var(--foreground-muted)] mb-1 tracking-[0.16em] uppercase">Total Products</p>
              <p className="text-xl font-bold text-[var(--accent-subtle)] fp-card-price">{status.totalProducts}</p>
            </div>
            
            <div className="fp-panel p-6 border border-[var(--border-subtle)]">
              <p className="text-[10px] text-[var(--foreground-muted)] mb-1 tracking-[0.16em] uppercase">Assigned</p>
              <p className="text-xl font-bold text-[var(--accent-subtle)] fp-card-price">{status.assignedProducts}</p>
            </div>
            
            <div className="fp-panel p-6 border border-[var(--border-subtle)]">
              <p className="text-[10px] text-[var(--foreground-muted)] mb-1 tracking-[0.16em] uppercase">Unassigned</p>
              <p className="text-xl font-bold text-[var(--accent-subtle)] fp-card-price">{status.unassignedProducts}</p>
            </div>
            
            <div className="fp-panel p-6 border border-[var(--border-subtle)]">
              <p className="text-[10px] text-[var(--foreground-muted)] mb-1 tracking-[0.16em] uppercase">Control Group</p>
              <p className="text-xl font-bold text-[var(--accent-subtle)] fp-card-price">{status.controlCount}</p>
            </div>
            
            <div className="fp-panel p-6 border border-[var(--border-subtle)]">
              <p className="text-[10px] text-[var(--foreground-muted)] mb-1 tracking-[0.16em] uppercase">ML Variant</p>
              <p className="text-xl font-bold text-[var(--accent-subtle)] fp-card-price">{status.mlVariantCount}</p>
            </div>
          </div>
        )}

        {/* Winner Card */}
        {winner && (
          <div className="mb-8 fp-panel p-6 border-2 border-[var(--accent-subtle)]">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-2">
                  {winner.winner === 'ML_VARIANT' ? '🏆 ML Variant is Winning!' :
                   winner.winner === 'CONTROL' ? '🏆 Control is Winning!' :
                   '⚖️ Both Performing Equally'}
                </h2>
                <p className="text-xs text-[var(--foreground)] mb-1">{winner.message}</p>
                <p className="text-[10px] text-[var(--foreground-muted)] tracking-[0.12em] uppercase">Confidence: <span className="font-semibold">{winner.confidence}</span> (sample: {winner.sampleSize})</p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-[var(--accent-subtle)] fp-card-price">
                  {winner.improvementPct > 0 ? '+' : ''}{winner.improvementPct.toFixed(1)}%
                </p>
                <p className="text-[10px] text-[var(--foreground-muted)] mt-1 tracking-[0.12em] uppercase">improvement</p>
              </div>
            </div>
            <div className="mt-4 p-3 bg-white/5 border border-[var(--border-subtle)] rounded">
              <p className="text-xs text-[var(--foreground)]">
                <strong className="tracking-[0.12em] uppercase">💡 Recommendation:</strong> {winner.recommendation}
              </p>
            </div>
          </div>
        )}

        {/* Comparison Table */}
        {comparison && (
          <div className="fp-panel p-6 mb-8">
            <h2 className="text-[10px] font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-4">Performance Comparison</h2>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-[var(--border-subtle)]">
                <thead>
                  <tr>
                    <th className="px-6 py-3 text-left text-[10px] font-semibold text-[var(--foreground-muted)] tracking-[0.16em] uppercase">
                      Metric
                    </th>
                    <th className="px-6 py-3 text-right text-[10px] font-semibold text-[var(--foreground-muted)] tracking-[0.16em] uppercase">
                      Control (Rule-Based)
                    </th>
                    <th className="px-6 py-3 text-right text-[10px] font-semibold text-[var(--foreground-muted)] tracking-[0.16em] uppercase">
                      ML Variant
                    </th>
                    <th className="px-6 py-3 text-right text-[10px] font-semibold text-[var(--foreground-muted)] tracking-[0.16em] uppercase">
                      Lift
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--border-subtle)]">
                  <tr className="hover:bg-white/5">
                    <td className="px-6 py-4 whitespace-nowrap text-xs font-medium text-[var(--foreground)]">
                      Conversion Rate
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                      {comparison.control.conversionRate.toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                      {comparison.mlVariant.conversionRate.toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right font-semibold text-[var(--accent-subtle)] fp-card-price">
                      {comparison.conversionLift > 0 ? '+' : ''}{comparison.conversionLift.toFixed(1)}%
                    </td>
                  </tr>
                  
                  <tr className="hover:bg-white/5">
                    <td className="px-6 py-4 whitespace-nowrap text-xs font-medium text-[var(--foreground)]">
                      Revenue per Product
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                      ${comparison.control.revenuePerProduct.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                      ${comparison.mlVariant.revenuePerProduct.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right font-semibold text-[var(--accent-subtle)] fp-card-price">
                      {comparison.revenueLift > 0 ? '+' : ''}{comparison.revenueLift.toFixed(1)}%
                    </td>
                  </tr>
                  
                  <tr className="hover:bg-white/5">
                    <td className="px-6 py-4 whitespace-nowrap text-xs font-medium text-[var(--foreground)]">
                      Units Sold
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                      {comparison.control.totalUnitsSold}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                      {comparison.mlVariant.totalUnitsSold}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right font-semibold text-[var(--accent-subtle)] fp-card-price">
                      {comparison.unitsLift > 0 ? '+' : ''}{comparison.unitsLift.toFixed(1)}%
                    </td>
                  </tr>
                  
                  <tr className="hover:bg-white/5">
                    <td className="px-6 py-4 whitespace-nowrap text-xs font-medium text-[var(--foreground)]">
                      Total Revenue
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                      ${comparison.control.totalRevenue.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                      ${comparison.mlVariant.totalRevenue.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                      ${(comparison.mlVariant.totalRevenue - comparison.control.totalRevenue).toFixed(2)}
                    </td>
                  </tr>
                  
                  <tr className="hover:bg-white/5">
                    <td className="px-6 py-4 whitespace-nowrap text-xs font-medium text-[var(--foreground)]">
                      Avg Discount
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                      {comparison.control.avgDiscountPct.toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
                      {comparison.mlVariant.avgDiscountPct.toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-right text-[var(--accent-subtle)] fp-card-price">
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
          <div className="fp-panel p-6 border border-[var(--border-subtle)]">
            <h3 className="text-[10px] font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-3">How It Works</h3>
            <ul className="space-y-2 text-xs text-[var(--foreground)]">
              <li className="flex items-start">
                <span className="mr-2">🎯</span>
                <span><strong className="tracking-[0.12em] uppercase text-[var(--foreground-muted)]">Control Group:</strong> Uses rule-based discount logic based on expiry, inventory, and category</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">🤖</span>
                <span><strong className="tracking-[0.12em] uppercase text-[var(--foreground-muted)]">ML Variant:</strong> Uses XGBoost model to predict optimal discount based on historical data</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">📊</span>
                <span>Products are randomly assigned 50/50 to each group for fair comparison</span>
              </li>
            </ul>
          </div>
          
          <div className="fp-panel p-6 border border-[var(--border-subtle)]">
            <h3 className="text-[10px] font-semibold tracking-[0.18em] uppercase text-[var(--accent-subtle)] mb-3">Success Metrics</h3>
            <ul className="space-y-2 text-xs text-[var(--foreground)]">
              <li className="flex items-start">
                <span className="mr-2">💰</span>
                <span><strong className="tracking-[0.12em] uppercase text-[var(--foreground-muted)]">Revenue Lift:</strong> Percentage increase in revenue per product</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">🎯</span>
                <span><strong className="tracking-[0.12em] uppercase text-[var(--foreground-muted)]">Conversion Lift:</strong> Improvement in purchase probability</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">📈</span>
                <span><strong className="tracking-[0.12em] uppercase text-[var(--foreground-muted)]">Units Lift:</strong> Additional units sold with ML recommendations</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
