import { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

// Register the required chart components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const BarChart = ({ data, title, height = 300, horizontal = false }) => {
  const [chartData, setChartData] = useState(null);
  
  useEffect(() => {
    if (data) {
      // Generate random colors for each bar
      const generateColors = (count) => {
        const colors = [];
        for (let i = 0; i < count; i++) {
          const r = Math.floor(Math.random() * 200);
          const g = Math.floor(Math.random() * 200);
          const b = Math.floor(Math.random() * 200);
          colors.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
        }
        return colors;
      };
      
      // Extract labels and values from data
      const labels = Object.keys(data);
      const values = Object.values(data).map(val => {
        // If value is a string with a percentage, convert to number
        if (typeof val === 'string' && val.includes('%')) {
          return parseFloat(val.replace('%', ''));
        }
        return val;
      });
      
      // Generate colors
      const backgroundColor = generateColors(labels.length);
      const borderColor = backgroundColor.map(color => color.replace('0.7', '1'));
      
      setChartData({
        labels,
        datasets: [
          {
            data: values,
            backgroundColor,
            borderColor,
            borderWidth: 1,
          },
        ],
      });
    }
  }, [data]);
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: horizontal ? 'y' : 'x',
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
            const label = context.label || '';
            const value = context.raw || 0;
            return `${label}: ${value}${typeof data[label] === 'string' && data[label].includes('%') ? '%' : ''}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return value + (horizontal ? '' : '%');
          }
        }
      },
      x: {
        ticks: {
          callback: function(value) {
            return value + (horizontal ? '%' : '');
          }
        }
      }
    }
  };
  
  return (
    <div style={{ height: height, position: 'relative' }}>
      {chartData ? (
        <Bar data={chartData} options={options} />
      ) : (
        <div className="chart-loading">Loading chart data...</div>
      )}
    </div>
  );
};

export default BarChart;
