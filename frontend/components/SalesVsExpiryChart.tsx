'use client';

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface SalesVsExpiryData {
  daysToExpiry: number;
  totalUnitsSold: number;
  totalRevenue: number;
  avgDiscountPct: number;
  productCount: number;
}

interface Props {
  data: SalesVsExpiryData[];
}

export default function SalesVsExpiryChart({ data }: Props) {
  // Transform data for recharts
  const chartData = data.map((item) => ({
    days: item.daysToExpiry,
    units: item.totalUnitsSold,
    revenue: parseFloat(item.totalRevenue.toString()),
    discount: parseFloat(item.avgDiscountPct?.toString() || '0'),
  }));

  return (
    <div className="fp-panel p-6">
      <h2 className="text-sm font-semibold tracking-[0.18em] uppercase text-[var(--foreground-muted)] mb-2">
        Sales vs Days to Expiry
      </h2>
      <p className="text-[10px] text-[var(--foreground-muted)] mb-4 tracking-[0.12em] uppercase">
        How product sales correlate with proximity to expiration date
      </p>
      
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="days"
            label={{ value: 'Days to Expiry', position: 'insideBottom', offset: -5 }}
          />
          <YAxis
            yAxisId="left"
            label={{ value: 'Units Sold', angle: -90, position: 'insideLeft' }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            label={{ value: 'Avg Discount %', angle: 90, position: 'insideRight' }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                return (
                  <div className="fp-panel p-3 border border-[var(--border-strong)] text-xs">
                    <p className="font-semibold text-[var(--accent-subtle)]">
                      {payload[0].payload.days} days to expiry
                    </p>
                    <p className="text-[var(--accent-subtle)]">
                      Units Sold: {payload[0].payload.units}
                    </p>
                    <p className="text-[var(--accent-subtle)]">
                      Revenue: ${payload[0].payload.revenue.toFixed(2)}
                    </p>
                    <p className="text-[var(--foreground-muted)]">
                      Avg Discount: {payload[0].payload.discount.toFixed(1)}%
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="units"
            stroke="#f5f5f5"
            strokeWidth={2}
            name="Units Sold"
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="discount"
            stroke="#a3a3a3"
            strokeWidth={2}
            name="Avg Discount %"
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div className="mt-4 grid grid-cols-3 gap-4 text-center text-xs">
        <div className="border border-[var(--border-subtle)] bg-black/40 p-3 rounded">
          <p className="text-[10px] text-[var(--foreground-muted)] tracking-[0.16em] uppercase">Total Units</p>
          <p className="text-lg font-bold text-[var(--accent-subtle)] fp-card-price">
            {chartData.reduce((sum, item) => sum + item.units, 0)}
          </p>
        </div>
        <div className="border border-[var(--border-subtle)] bg-black/40 p-3 rounded">
          <p className="text-[10px] text-[var(--foreground-muted)] tracking-[0.16em] uppercase">Total Revenue</p>
          <p className="text-lg font-bold text-[var(--accent-subtle)] fp-card-price">
            ${chartData.reduce((sum, item) => sum + item.revenue, 0).toFixed(2)}
          </p>
        </div>
        <div className="border border-[var(--border-subtle)] bg-black/40 p-3 rounded">
          <p className="text-[10px] text-[var(--foreground-muted)] tracking-[0.16em] uppercase">Avg Discount</p>
          <p className="text-lg font-bold text-[var(--accent-subtle)] fp-card-price">
            {(chartData.reduce((sum, item) => sum + item.discount, 0) / chartData.length).toFixed(1)}%
          </p>
        </div>
      </div>
    </div>
  );
}
