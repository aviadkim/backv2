import React, { useState, useEffect } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Bar, Pie, Doughnut, Line } from 'react-chartjs-2';
import { FiBarChart2, FiPieChart, FiTrendingUp, FiGrid } from 'react-icons/fi';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Generate random colors for charts
const generateColors = (count) => {
  const colors = [];
  for (let i = 0; i < count; i++) {
    const hue = (i * 137) % 360; // Use golden angle approximation for better distribution
    colors.push(`hsla(${hue}, 70%, 60%, 0.8)`);
  }
  return colors;
};

const FinancialDataVisualization = ({ data, type = 'portfolio' }) => {
  const [chartType, setChartType] = useState('doughnut');
  const [chartData, setChartData] = useState(null);
  const [chartOptions, setChartOptions] = useState({});

  useEffect(() => {
    if (!data) return;

    prepareChartData();
  }, [data, chartType]);

  const prepareChartData = () => {
    if (type === 'portfolio') {
      preparePortfolioData();
    } else if (type === 'timeSeries') {
      prepareTimeSeriesData();
    } else if (type === 'comparison') {
      prepareComparisonData();
    }
  };

  const preparePortfolioData = () => {
    if (!data || !data.holdings) return;

    const holdings = data.holdings;
    const labels = holdings.map(h => h.name || h.isin);
    const values = holdings.map(h => h.value);
    const backgroundColors = generateColors(labels.length);

    // Prepare data based on chart type
    if (chartType === 'doughnut' || chartType === 'pie') {
      setChartData({
        labels,
        datasets: [
          {
            data: values,
            backgroundColor: backgroundColors,
            borderColor: backgroundColors.map(color => color.replace('0.8', '1')),
            borderWidth: 1
          }
        ]
      });

      setChartOptions({
        responsive: true,
        plugins: {
          legend: {
            position: 'right',
            labels: {
              boxWidth: 15,
              font: {
                size: 12
              }
            }
          },
          title: {
            display: true,
            text: 'Portfolio Allocation',
            font: {
              size: 16
            }
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.label || '';
                const value = context.raw;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                return `${label}: ${value.toLocaleString()} (${percentage}%)`;
              }
            }
          }
        }
      });
    } else if (chartType === 'bar') {
      setChartData({
        labels,
        datasets: [
          {
            label: 'Value',
            data: values,
            backgroundColor: backgroundColors,
            borderColor: backgroundColors.map(color => color.replace('0.8', '1')),
            borderWidth: 1
          }
        ]
      });

      setChartOptions({
        responsive: true,
        plugins: {
          legend: {
            display: false
          },
          title: {
            display: true,
            text: 'Portfolio Holdings',
            font: {
              size: 16
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Value'
            }
          }
        }
      });
    }
  };

  const prepareTimeSeriesData = () => {
    if (!data || !data.timeSeries) return;

    const { dates, values } = data.timeSeries;

    setChartData({
      labels: dates,
      datasets: [
        {
          label: 'Portfolio Value',
          data: values,
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.4,
          fill: true
        }
      ]
    });

    setChartOptions({
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'Portfolio Performance Over Time',
          font: {
            size: 16
          }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          title: {
            display: true,
            text: 'Value'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Date'
          }
        }
      }
    });
  };

  const prepareComparisonData = () => {
    if (!data || !data.comparison) return;

    const { categories, series } = data.comparison;

    setChartData({
      labels: categories,
      datasets: series.map((s, index) => ({
        label: s.name,
        data: s.data,
        backgroundColor: generateColors(series.length)[index],
        borderColor: generateColors(series.length)[index].replace('0.8', '1'),
        borderWidth: 1
      }))
    });

    setChartOptions({
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'Comparison',
          font: {
            size: 16
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Value'
          }
        }
      }
    });
  };

  const renderChart = () => {
    if (!chartData) return <div className="flex justify-center items-center h-64 bg-gray-100 rounded-lg">No data available</div>;

    switch (chartType) {
      case 'bar':
        return <Bar data={chartData} options={chartOptions} />;
      case 'pie':
        return <Pie data={chartData} options={chartOptions} />;
      case 'doughnut':
        return <Doughnut data={chartData} options={chartOptions} />;
      case 'line':
        return <Line data={chartData} options={chartOptions} />;
      default:
        return <Doughnut data={chartData} options={chartOptions} />;
    }
  };

  return (
    <AccessibilityWrapper>
      <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">Financial Data Visualization</h3>
        <div className="flex space-x-2">
          <button
            type="button"
            onClick={() => setChartType('doughnut')}
            className={`p-2 rounded-md ${chartType === 'doughnut' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-100'}`}
            title="Doughnut Chart"
          >
            <FiPieChart className="h-5 w-5" />
          </button>
          <button
            type="button"
            onClick={() => setChartType('pie')}
            className={`p-2 rounded-md ${chartType === 'pie' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-100'}`}
            title="Pie Chart"
          >
            <FiPieChart className="h-5 w-5" />
          </button>
          <button
            type="button"
            onClick={() => setChartType('bar')}
            className={`p-2 rounded-md ${chartType === 'bar' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-100'}`}
            title="Bar Chart"
          >
            <FiBarChart2 className="h-5 w-5" />
          </button>
          <button
            type="button"
            onClick={() => setChartType('line')}
            className={`p-2 rounded-md ${chartType === 'line' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-100'}`}
            title="Line Chart"
          >
            <FiTrendingUp className="h-5 w-5" />
          </button>
        </div>
      </div>

      <div className="h-80">
        {renderChart()}
      </div>

      {data && data.summary && (
        <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
          {Object.entries(data.summary).map(([key, value]) => {
            if (key === 'totalValue') {
              return (
                <div key={key} className="bg-blue-50 p-3 rounded-lg">
                  <h4 className="text-xs font-medium text-blue-500 uppercase">Total Value</h4>
                  <p className="mt-1 text-lg font-semibold text-blue-700">{value}</p>
                </div>
              );
            }

            if (typeof value === 'object') {
              return null; // Skip nested objects, they're visualized in the chart
            }

            return (
              <div key={key} className="bg-gray-50 p-3 rounded-lg">
                <h4 className="text-xs font-medium text-gray-500 uppercase">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </h4>
                <p className="mt-1 text-lg font-semibold text-gray-700">{value}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
    </AccessibilityWrapper>
  );
};

export default FinancialDataVisualization;
