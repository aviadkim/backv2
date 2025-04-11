import { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

// Register the required chart components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const LineChart = ({ data, title, height = 300, isPercentage = false }) => {
  const [chartData, setChartData] = useState(null);
  
  useEffect(() => {
    if (data) {
      // Extract labels and values from data
      const labels = Object.keys(data);
      const values = Object.values(data).map(val => {
        // If value is a string with a percentage, convert to number
        if (typeof val === 'string' && val.includes('%')) {
          return parseFloat(val.replace('%', ''));
        }
        return val;
      });
      
      setChartData({
        labels,
        datasets: [
          {
            data: values,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.1,
            fill: true,
          },
        ],
      });
    }
  }, [data]);
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 16
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.dataset.label || '';
            const value = context.raw || 0;
            return `${label} ${value}${isPercentage ? '%' : ''}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return value + (isPercentage ? '%' : '');
          }
        }
      }
    }
  };
  
  return (
    <div style={{ height: height, position: 'relative' }}>
      {chartData ? (
        <Line data={chartData} options={options} />
      ) : (
        <div className="chart-loading">Loading chart data...</div>
      )}
    </div>
  );
};

export default LineChart;
