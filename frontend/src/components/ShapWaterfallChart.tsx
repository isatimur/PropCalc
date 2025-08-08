'use client';

import React, { useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';
import 'chartjs-adapter-date-fns';

Chart.register(...registerables);

interface ShapWaterfallChartProps {
  shapExplanation: {
    base_value: number;
    shap_values: { [key: string]: number };
  };
}

const ShapWaterfallChart: React.FC<ShapWaterfallChartProps> = ({ shapExplanation }) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    if (chartRef.current && shapExplanation) {
      const ctx = chartRef.current.getContext('2d');
      if (ctx) {
        const { base_value, shap_values } = shapExplanation;
        const features = Object.keys(shap_values);
        const values = Object.values(shap_values);

        let cumulative = base_value;
        const data = values.map(value => {
          const start = cumulative;
          const end = cumulative + value;
          cumulative = end;
          return [start, end];
        });

        chartInstance.current = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: features,
            datasets: [{
              label: 'SHAP Value',
              data: data as any,
              backgroundColor: values.map(v => v > 0 ? 'rgba(255, 99, 132, 0.5)' : 'rgba(54, 162, 235, 0.5)'),
              borderColor: values.map(v => v > 0 ? 'rgba(255, 99, 132, 1)' : 'rgba(54, 162, 235, 1)'),
              borderWidth: 1,
              barPercentage: 0.8,
            }]
          },
          options: {
            indexAxis: 'y',
            scales: {
              y: {
                beginAtZero: false,
                grid: {
                  display: false,
                },
              },
              x: {
                title: {
                  display: true,
                  text: 'Vantage Score',
                },
              },
            },
            plugins: {
              legend: {
                display: false,
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const value = context.raw as number[];
                    const feature = context.label;
                    const shapValue = value[1] - value[0];
                    return `${feature}: ${shapValue.toFixed(2)}`;
                  }
                }
              },
              title: {
                display: true,
                text: 'Vantage Score Explanation'
              }
            }
          }
        });
      }
    }

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [shapExplanation]);

  return <canvas ref={chartRef} />;
};

export default ShapWaterfallChart;
