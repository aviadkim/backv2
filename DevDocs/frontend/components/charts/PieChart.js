import { useState, useEffect } from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

// Register the required chart components
ChartJS.register(ArcElement, Tooltip, Legend);

const PieChart = ({ data, title, height = 300 }) => {
  const [chartData, setChartData] = useState(null);
  
  useEffect(() => {
    if (data) {
      // Generate random colors for each segment
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
    plugins: {
      legend: {
        position: 'right',
        labels: {
          boxWidth: 15,
          padding: 15,
          font: {
            size: 12
          }
        }
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
            return `${label}: ${value}%`;
          }
        }
      }
    }
  };
  
  return (
    <div style={{ height: height, position: 'relative' }}>
      {chartData ? (
        <Pie data={chartData} options={options} />
      ) : (
        <div className="chart-loading">Loading chart data...</div>
      )}
    </div>
  );
};

export default PieChart;
