"use client";

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Pie, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface ChartData {
  property_types: Array<{
    type: string;
    transaction_count: number;
    avg_price_aed: number;
    total_value_aed: number;
  }>;
  locations: Array<{
    location: string;
    transaction_count: number;
    avg_price_aed: number;
    total_value_aed: number;
  }>;
  developers: Array<{
    developer_name: string;
    transaction_count: number;
    total_value_aed: number;
  }>;
  price_ranges: Array<{
    range: string;
    transaction_count: number;
    avg_price_aed: number;
  }>;
}

interface DLDAnalyticsChartsProps {
  data: ChartData;
}

export function DLDAnalyticsCharts({ data }: DLDAnalyticsChartsProps) {
  const formatCurrency = (amount: number) => {
    if (amount >= 1e9) {
      return `${(amount / 1e9).toFixed(1)}B AED`;
    } else if (amount >= 1e6) {
      return `${(amount / 1e6).toFixed(1)}M AED`;
    }
    return `${amount.toFixed(0)} AED`;
  };

  // Property Types Pie Chart
  const propertyTypesData = {
    labels: data.property_types.map(pt => pt.type),
    datasets: [
      {
        data: data.property_types.map(pt => pt.transaction_count),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
        ],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  // Top Locations Bar Chart
  const topLocationsData = {
    labels: data.locations.slice(0, 10).map(loc => loc.location),
    datasets: [
      {
        label: 'Transaction Count',
        data: data.locations.slice(0, 10).map(loc => loc.transaction_count),
        backgroundColor: 'rgba(54, 162, 235, 0.8)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

  // Top Developers Bar Chart
  const topDevelopersData = {
    labels: data.developers.slice(0, 10).map(dev => dev.developer_name),
    datasets: [
      {
        label: 'Total Value (Billion AED)',
        data: data.developers.slice(0, 10).map(dev => dev.total_value_aed / 1e9),
        backgroundColor: 'rgba(75, 192, 192, 0.8)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  // Price Ranges Doughnut Chart
  const priceRangesData = {
    labels: data.price_ranges.map(pr => pr.range),
    datasets: [
      {
        data: data.price_ranges.map(pr => pr.transaction_count),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40',
        ],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.label || '';
            const value = context.parsed || context.raw;
            return `${label}: ${value.toLocaleString()}`;
          },
        },
      },
    },
  };

  const barChartOptions = {
    ...chartOptions,
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return value.toLocaleString();
          },
        },
      },
    },
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Property Types Distribution */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Property Types Distribution</h3>
        <div className="h-80">
          <Pie data={propertyTypesData} options={chartOptions} />
        </div>
        <div className="mt-4 space-y-2">
          {data.property_types.map((pt, index) => (
            <div key={pt.type} className="flex justify-between items-center">
              <span className="text-sm">{pt.type}</span>
              <span className="text-sm font-medium">
                {pt.transaction_count.toLocaleString()} transactions
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Top Locations */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Top 10 Locations by Transactions</h3>
        <div className="h-80">
          <Bar data={topLocationsData} options={barChartOptions} />
        </div>
        <div className="mt-4 space-y-2">
          {data.locations.slice(0, 5).map((loc, index) => (
            <div key={loc.location} className="flex justify-between items-center">
              <span className="text-sm">{loc.location}</span>
              <span className="text-sm font-medium">
                {formatCurrency(loc.avg_price_aed)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Top Developers */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Top 10 Developers by Volume</h3>
        <div className="h-80">
          <Bar data={topDevelopersData} options={barChartOptions} />
        </div>
        <div className="mt-4 space-y-2">
          {data.developers.slice(0, 5).map((dev, index) => (
            <div key={dev.developer_name} className="flex justify-between items-center">
              <span className="text-sm">{dev.developer_name}</span>
              <span className="text-sm font-medium">
                {formatCurrency(dev.total_value_aed)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Price Ranges */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Price Range Distribution</h3>
        <div className="h-80">
          <Doughnut data={priceRangesData} options={chartOptions} />
        </div>
        <div className="mt-4 space-y-2">
          {data.price_ranges.map((pr, index) => (
            <div key={pr.range} className="flex justify-between items-center">
              <span className="text-sm">{pr.range}</span>
              <span className="text-sm font-medium">
                {pr.transaction_count.toLocaleString()} transactions
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default DLDAnalyticsCharts; 