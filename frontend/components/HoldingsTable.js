import React from 'react';

const HoldingsTable = ({ holdings }) => {
  if (!holdings || holdings.length === 0) {
    return <p>No holdings data available.</p>;
  }

  return (
    <div className="holdings-table">
      <h2>Top Holdings</h2>
      <table>
        <thead>
          <tr>
            <th>ISIN</th>
            <th>Description</th>
            <th>Nominal</th>
            <th>Acquisition Price</th>
            <th>Current Price</th>
            <th>Valuation</th>
            <th>Percentage</th>
            <th>Change (1M)</th>
            <th>Change (YTD)</th>
          </tr>
        </thead>
        <tbody>
          {holdings.map((holding, index) => (
            <tr key={holding.isin || index}>
              <td>{holding.isin}</td>
              <td>{holding.description || 'N/A'}</td>
              <td>{holding.nominal ? formatNumber(holding.nominal) : 'N/A'}</td>
              <td>{holding.acquisition_price ? formatNumber(holding.acquisition_price, 2) : 'N/A'}</td>
              <td>{holding.current_price ? formatNumber(holding.current_price, 2) : 'N/A'}</td>
              <td>{holding.valuation ? formatCurrency(holding.valuation) : 'N/A'}</td>
              <td>{holding.percentage ? `${formatNumber(holding.percentage, 2)}%` : 'N/A'}</td>
              <td className={getChangeClass(holding.change_1m)}>
                {holding.change_1m ? `${formatNumber(holding.change_1m, 2)}%` : 'N/A'}
              </td>
              <td className={getChangeClass(holding.change_ytd)}>
                {holding.change_ytd ? `${formatNumber(holding.change_ytd, 2)}%` : 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      <style jsx>{`
        .holdings-table {
          margin-top: 30px;
          overflow-x: auto;
        }
        
        table {
          width: 100%;
          border-collapse: collapse;
          font-size: 14px;
        }
        
        th, td {
          padding: 10px;
          text-align: left;
          border-bottom: 1px solid #ddd;
        }
        
        th {
          background-color: #f2f2f2;
          font-weight: bold;
        }
        
        tr:hover {
          background-color: #f5f5f5;
        }
        
        .positive {
          color: #4caf50;
        }
        
        .negative {
          color: #f44336;
        }
      `}</style>
    </div>
  );
};

// Helper functions
const formatNumber = (value, decimals = 0) => {
  if (value === null || value === undefined) return 'N/A';
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
};

const formatCurrency = (value) => {
  if (value === null || value === undefined) return 'N/A';
  return `$${Number(value).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`;
};

const getChangeClass = (value) => {
  if (value === null || value === undefined) return '';
  return value >= 0 ? 'positive' : 'negative';
};

export default HoldingsTable;
