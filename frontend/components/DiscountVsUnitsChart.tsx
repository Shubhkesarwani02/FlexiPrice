'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface DiscountVsUnitsData {
  discountRange: string;
  discountAvg: number;
  totalUnitsSold: number;
  totalRevenue: number;
  transactionCount: number;
  conversionRate: number;
}

interface Props {
  data: DiscountVsUnitsData[];
}

// Color palette for bars - monochrome gradients
const COLORS = ['#f5f5f5', '#d4d4d4', '#a3a3a3', '#737373', '#525252', '#404040'];

export default function DiscountVsUnitsChart({ data }: Props) {
  // Transform data for recharts
  const chartData = data.map((item) => ({
    range: item.discountRange,
    units: item.totalUnitsSold,
    revenue: parseFloat(item.totalRevenue.toString()),
    transactions: item.transactionCount,
    conversion: parseFloat(item.conversionRate?.toString() || '0'),
    avgDiscount: parseFloat(item.discountAvg.toString()),
  }));

  return (
    <div className="fp-panel p-6">
      <h2 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--foreground-muted)] mb-2">
        Discount Percentage vs Units Sold
      </h2>
      <p className="text-[10px] text-[var(--foreground-muted)] mb-4 tracking-[0.12em] uppercase">
        Impact of different discount levels on sales performance
      </p>
      
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="range"
            label={{ value: 'Discount Range', position: 'insideBottom', offset: -5 }}
          />
          <YAxis
            yAxisId="left"
            label={{ value: 'Units Sold', angle: -90, position: 'insideLeft' }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            label={{ value: 'Conversion Rate %', angle: 90, position: 'insideRight' }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="fp-panel p-3 border border-[var(--border-strong)] text-xs">
                    <p className="font-semibold mb-2 text-[var(--accent-subtle)]">{data.range}</p>
                    <p className="text-[var(--accent-subtle)]">
                      Units Sold: {data.units}
                    </p>
                    <p className="text-[var(--accent-subtle)]">
                      Revenue: ${data.revenue.toFixed(2)}
                    </p>
                    <p className="text-[var(--foreground-muted)]">
                      Transactions: {data.transactions}
                    </p>
                    <p className="text-[var(--foreground-muted)]">
                      Conversion: {data.conversion.toFixed(1)}%
                    </p>
                    <p className="text-[var(--foreground-muted)] text-[10px] mt-1">
                      Avg: {data.avgDiscount.toFixed(1)}%
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend />
          <Bar
            yAxisId="left"
            dataKey="units"
            name="Units Sold"
            radius={[8, 8, 0, 0]}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
          <Bar
            yAxisId="right"
            dataKey="conversion"
            name="Conversion Rate %"
            fill="#737373"
            radius={[8, 8, 0, 0]}
            opacity={0.6}
          />
        </BarChart>
      </ResponsiveContainer>
      
      <div className="mt-4 grid grid-cols-2 gap-4 text-xs">
        <div className="border border-[var(--border-subtle)] bg-black/40 p-4 rounded">
          <p className="text-[10px] text-[var(--foreground-muted)] mb-2 tracking-[0.16em] uppercase">Best Performing Discount</p>
          {chartData.length > 0 && (() => {
            const best = chartData.reduce((max, item) =>
              item.units > max.units ? item : max
            );
            return (
              <>
                <p className="text-xl font-bold text-[var(--accent-subtle)]">{best.range}</p>
                <p className="text-[10px] text-[var(--foreground-muted)]">
                  {best.units} units • {best.conversion.toFixed(1)}% conversion
                </p>
              </>
            );
          })()}
        </div>
        
        <div className="border border-[var(--border-subtle)] bg-black/40 p-4 rounded">
          <p className="text-[10px] text-[var(--foreground-muted)] mb-2 tracking-[0.16em] uppercase">Highest Revenue</p>
          {chartData.length > 0 && (() => {
            const best = chartData.reduce((max, item) =>
              item.revenue > max.revenue ? item : max
            );
            return (
              <>
                <p className="text-xl font-bold text-[var(--accent-subtle)] fp-card-price">
                  ${best.revenue.toFixed(2)}
                </p>
                <p className="text-[10px] text-[var(--foreground-muted)]">
                  {best.range} • {best.transactions} transactions
                </p>
              </>
            );
          })()}
        </div>
      </div>
      
      <div className="mt-4 p-4 border border-[var(--border-subtle)] bg-black/40 rounded text-xs">
        <p className="text-[var(--foreground-muted)]">
          <strong className="text-[var(--accent-subtle)]">Insight:</strong> Higher discounts generally increase unit sales but may reduce total revenue. 
          Find the sweet spot that balances conversion and profitability.
        </p>
      </div>
    </div>
  );
}
