import React from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';

import { useState, useEffect } from 'react';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend,
  ArcElement
} from 'chart.js';
import { Line, Bar, Pie } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Chart = ({ type = 'line', data, options = {}, height = 300 }) => {
  const [chartData, setChartData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    try {
      // Handle empty data
      if (!data || !data.labels || !data.datasets || data.labels.length === 0) {
        // Create default empty data
        const emptyData = {
          labels: ['No Data'],
          datasets: [
            {
              label: 'No Data Available',
              data: [0],
              backgroundColor: 'rgba(200, 200, 200, 0.5)',
              borderColor: 'rgba(200, 200, 200, 1)',
              borderWidth: 1,
            },
          ],
        };
        setChartData(emptyData);
        setError('No data available for chart');
      } else {
        setChartData(data);
        setError(null);
      }
    } catch (err) {
      console.error('Error processing chart data:', err);
      setError('Error processing chart data');
    }
  }, [data]);

  if (error) {
    return (
    <AccessibilityWrapper>
      
      <div className="flex flex-col items-center justify-center" style={{ height }}>
        <div className="text-gray-400 text-sm">{error}</div>
        {chartData && renderChart(type, chartData, options, height)}
      </div>
    );
  }

  if (!chartData) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return renderChart(type, chartData, options, height);
};

const renderChart = (type, data, options, height) => {
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    ...options,
  };

  switch (type.toLowerCase()) {
    case 'bar':
      return <Bar data={data} options={chartOptions} height={height} />;
    case 'pie':
      return <Pie data={data} options={chartOptions} height={height} />;
    case 'line':
    default:
      return <Line data={data} options={chartOptions} height={height} />;
  }
};

export default Chart;
