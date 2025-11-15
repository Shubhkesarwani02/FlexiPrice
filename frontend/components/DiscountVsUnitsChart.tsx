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

// Color palette for bars
const COLORS = ['#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16', '#22c55e'];

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
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">
        Discount Percentage vs Units Sold
      </h2>
      <p className="text-sm text-gray-600 mb-4">
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
                  <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
                    <p className="font-semibold mb-2">{data.range}</p>
                    <p className="text-blue-600">
                      Units Sold: {data.units}
                    </p>
                    <p className="text-green-600">
                      Revenue: ${data.revenue.toFixed(2)}
                    </p>
                    <p className="text-purple-600">
                      Transactions: {data.transactions}
                    </p>
                    <p className="text-orange-600">
                      Conversion: {data.conversion.toFixed(1)}%
                    </p>
                    <p className="text-gray-600 text-sm mt-1">
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
            fill="#8b5cf6"
            radius={[8, 8, 0, 0]}
            opacity={0.6}
          />
        </BarChart>
      </ResponsiveContainer>
      
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div className="bg-gradient-to-r from-blue-50 to-green-50 p-4 rounded">
          <p className="text-sm text-gray-600 mb-2">Best Performing Discount</p>
          {chartData.length > 0 && (() => {
            const best = chartData.reduce((max, item) =>
              item.units > max.units ? item : max
            );
            return (
              <>
                <p className="text-2xl font-bold text-blue-600">{best.range}</p>
                <p className="text-sm text-gray-600">
                  {best.units} units • {best.conversion.toFixed(1)}% conversion
                </p>
              </>
            );
          })()}
        </div>
        
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded">
          <p className="text-sm text-gray-600 mb-2">Highest Revenue</p>
          {chartData.length > 0 && (() => {
            const best = chartData.reduce((max, item) =>
              item.revenue > max.revenue ? item : max
            );
            return (
              <>
                <p className="text-2xl font-bold text-green-600">
                  ${best.revenue.toFixed(2)}
                </p>
                <p className="text-sm text-gray-600">
                  {best.range} • {best.transactions} transactions
                </p>
              </>
            );
          })()}
        </div>
      </div>
      
      <div className="mt-4 p-4 bg-amber-50 rounded border border-amber-200">
        <p className="text-sm text-amber-800">
          <strong>💡 Insight:</strong> Higher discounts generally increase unit sales but may reduce total revenue. 
          Find the sweet spot that balances conversion and profitability.
        </p>
      </div>
    </div>
  );
}
