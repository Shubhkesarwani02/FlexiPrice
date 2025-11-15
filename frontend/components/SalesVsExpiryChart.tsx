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
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">
        Sales vs Days to Expiry
      </h2>
      <p className="text-sm text-gray-600 mb-4">
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
                  <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
                    <p className="font-semibold">
                      {payload[0].payload.days} days to expiry
                    </p>
                    <p className="text-blue-600">
                      Units Sold: {payload[0].payload.units}
                    </p>
                    <p className="text-green-600">
                      Revenue: ${payload[0].payload.revenue.toFixed(2)}
                    </p>
                    <p className="text-orange-600">
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
            stroke="#3b82f6"
            strokeWidth={2}
            name="Units Sold"
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="discount"
            stroke="#f97316"
            strokeWidth={2}
            name="Avg Discount %"
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        <div className="bg-blue-50 p-3 rounded">
          <p className="text-sm text-gray-600">Total Units</p>
          <p className="text-xl font-bold text-blue-600">
            {chartData.reduce((sum, item) => sum + item.units, 0)}
          </p>
        </div>
        <div className="bg-green-50 p-3 rounded">
          <p className="text-sm text-gray-600">Total Revenue</p>
          <p className="text-xl font-bold text-green-600">
            ${chartData.reduce((sum, item) => sum + item.revenue, 0).toFixed(2)}
          </p>
        </div>
        <div className="bg-orange-50 p-3 rounded">
          <p className="text-sm text-gray-600">Avg Discount</p>
          <p className="text-xl font-bold text-orange-600">
            {(chartData.reduce((sum, item) => sum + item.discount, 0) / chartData.length).toFixed(1)}%
          </p>
        </div>
      </div>
    </div>
  );
}
