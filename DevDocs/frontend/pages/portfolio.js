import { useState, useEffect } from 'react';
import Head from 'next/head';
import FinDocLayout from '../components/FinDocLayout';
import { PieChart, BarChart, LineChart } from '../components/charts';

export default function PortfolioPage() {
  const [portfolio, setPortfolio] = useState([]);
  const [portfolioSummary, setPortfolioSummary] = useState(null);
  const [riskMetrics, setRiskMetrics] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch portfolio data on component mount
  useEffect(() => {
    const fetchPortfolioData = async () => {
      try {
        setLoading(true);

        // Fetch portfolio data
        const portfolioResponse = await fetch('http://localhost:24125/api/portfolio');
        if (!portfolioResponse.ok) {
          throw new Error(`API error: ${portfolioResponse.status}`);
        }
        const portfolioData = await portfolioResponse.json();
        setPortfolio(portfolioData.portfolio || []);

        // Fetch portfolio summary
        const summaryResponse = await fetch('http://localhost:24125/api/portfolio/summary');
        if (!summaryResponse.ok) {
          throw new Error(`API error: ${summaryResponse.status}`);
        }
        const summaryData = await summaryResponse.json();

        console.log('Portfolio summary data:', summaryData);
        if (summaryData.status === 'success') {
          setPortfolioSummary(summaryData.allocation || {});
          setRiskMetrics(summaryData.risk_metrics || {});
          setPerformance(summaryData.performance || {});
        } else {
          throw new Error('Failed to get portfolio summary');
        }
      } catch (error) {
        console.error('Error fetching portfolio data:', error);
        setError('Failed to load portfolio data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolioData();
  }, []);

  // Calculate total portfolio value
  const totalValue = portfolio.reduce((sum, item) => sum + item.value, 0);

  // Format currency
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  // Format percentage
  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  return (
    <FinDocLayout>
      <Head>
        <title>Portfolio Analysis | FinDoc Analyzer</title>
      </Head>

      <div className="portfolio-page">
        <h1 className="page-title">Portfolio Analysis</h1>

        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading portfolio data...</p>
          </div>
        ) : error ? (
          <div className="error-container">
            <p className="error-message">{error}</p>
            <button
              className="retry-button"
              onClick={() => window.location.reload()}
            >
              Retry
            </button>
          </div>
        ) : (
          <>
            {/* Portfolio Summary Cards */}
            <div className="summary-cards">
              <div className="summary-card">
                <h3>Total Value</h3>
                <div className="summary-value">{formatCurrency(totalValue)}</div>
              </div>

              <div className="summary-card">
                <h3>Holdings</h3>
                <div className="summary-value">{portfolio.length}</div>
              </div>

              {riskMetrics && (
                <>
                  <div className="summary-card">
                    <h3>Volatility</h3>
                    <div className="summary-value">{formatPercentage(riskMetrics.volatility)}</div>
                  </div>

                  <div className="summary-card">
                    <h3>Sharpe Ratio</h3>
                    <div className="summary-value">{riskMetrics.sharpe_ratio.toFixed(2)}</div>
                  </div>
                </>
              )}
            </div>

            {/* Tab Navigation */}
            <div className="tab-navigation">
              <button
                className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                Overview
              </button>
              <button
                className={`tab-button ${activeTab === 'allocation' ? 'active' : ''}`}
                onClick={() => setActiveTab('allocation')}
              >
                Allocation
              </button>
              <button
                className={`tab-button ${activeTab === 'performance' ? 'active' : ''}`}
                onClick={() => setActiveTab('performance')}
              >
                Performance
              </button>
              <button
                className={`tab-button ${activeTab === 'risk' ? 'active' : ''}`}
                onClick={() => setActiveTab('risk')}
              >
                Risk Analysis
              </button>
              <button
                className={`tab-button ${activeTab === 'holdings' ? 'active' : ''}`}
                onClick={() => setActiveTab('holdings')}
              >
                Holdings
              </button>
            </div>

            {/* Tab Content */}
            <div className="tab-content">
              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div className="tab-pane">
                  <div className="overview-grid">
                    {portfolioSummary && (
                      <>
                        <div className="chart-card">
                          <h3>Asset Allocation</h3>
                          <PieChart data={portfolioSummary.asset_allocation} height={250} />
                        </div>

                        <div className="chart-card">
                          <h3>Geographic Allocation</h3>
                          <PieChart data={portfolioSummary.geographic_allocation} height={250} />
                        </div>

                        <div className="chart-card">
                          <h3>Sector Allocation</h3>
                          <PieChart data={portfolioSummary.sector_allocation} height={250} />
                        </div>
                      </>
                    )}

                    {riskMetrics && (
                      <div className="chart-card">
                        <h3>Risk Metrics</h3>
                        <div className="metrics-grid">
                          <div className="metric">
                            <div className="metric-label">Volatility</div>
                            <div className="metric-value">{formatPercentage(riskMetrics.volatility)}</div>
                          </div>
                          <div className="metric">
                            <div className="metric-label">Sharpe Ratio</div>
                            <div className="metric-value">{riskMetrics.sharpe_ratio.toFixed(2)}</div>
                          </div>
                          <div className="metric">
                            <div className="metric-label">Beta</div>
                            <div className="metric-value">{riskMetrics.beta.toFixed(2)}</div>
                          </div>
                          <div className="metric">
                            <div className="metric-label">Alpha</div>
                            <div className="metric-value">{formatPercentage(riskMetrics.alpha)}</div>
                          </div>
                          <div className="metric">
                            <div className="metric-label">Max Drawdown</div>
                            <div className="metric-value">{formatPercentage(riskMetrics.max_drawdown)}</div>
                          </div>
                          <div className="metric">
                            <div className="metric-label">VaR (95%)</div>
                            <div className="metric-value">{formatPercentage(riskMetrics.var_95)}</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Allocation Tab */}
              {activeTab === 'allocation' && (
                <div className="tab-pane">
                  {portfolioSummary && (
                    <div className="allocation-grid">
                      <div className="chart-card">
                        <h3>Asset Allocation</h3>
                        <PieChart data={portfolioSummary.asset_allocation} height={300} />
                      </div>

                      <div className="chart-card">
                        <h3>Asset Allocation</h3>
                        <BarChart data={portfolioSummary.asset_allocation} height={300} />
                      </div>

                      <div className="chart-card">
                        <h3>Geographic Allocation</h3>
                        <PieChart data={portfolioSummary.geographic_allocation} height={300} />
                      </div>

                      <div className="chart-card">
                        <h3>Geographic Allocation</h3>
                        <BarChart data={portfolioSummary.geographic_allocation} height={300} horizontal={true} />
                      </div>

                      <div className="chart-card">
                        <h3>Sector Allocation</h3>
                        <PieChart data={portfolioSummary.sector_allocation} height={300} />
                      </div>

                      <div className="chart-card">
                        <h3>Sector Allocation</h3>
                        <BarChart data={portfolioSummary.sector_allocation} height={300} horizontal={true} />
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Performance Tab */}
              {activeTab === 'performance' && (
                <div className="tab-pane">
                  {performance && (
                    <>
                      <div className="chart-card">
                        <h3>Performance</h3>
                        <LineChart data={performance} height={300} isPercentage={true} />
                      </div>

                      <div className="performance-table">
                        <h3>Performance Summary</h3>
                        <table>
                          <thead>
                            <tr>
                              <th>Period</th>
                              <th>Return</th>
                            </tr>
                          </thead>
                          <tbody>
                            {Object.entries(performance).map(([period, value]) => (
                              <tr key={period}>
                                <td>
                                  {period === '1m' ? '1 Month' :
                                   period === '3m' ? '3 Months' :
                                   period === '6m' ? '6 Months' :
                                   period === '1y' ? '1 Year' :
                                   period === '3y' ? '3 Years' :
                                   period === '5y' ? '5 Years' :
                                   period === 'ytd' ? 'Year to Date' : period}
                                </td>
                                <td className={value >= 0 ? 'positive' : 'negative'}>
                                  {formatPercentage(value)}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Risk Analysis Tab */}
              {activeTab === 'risk' && (
                <div className="tab-pane">
                  {riskMetrics && (
                    <>
                      <div className="chart-card">
                        <h3>Risk Metrics</h3>
                        <BarChart
                          data={{
                            'Volatility': riskMetrics.volatility * 100,
                            'Beta': riskMetrics.beta,
                            'Alpha': riskMetrics.alpha * 100,
                            'Max Drawdown': riskMetrics.max_drawdown * 100,
                            'VaR (95%)': riskMetrics.var_95 * 100
                          }}
                          height={300}
                        />
                      </div>

                      <div className="risk-metrics-table">
                        <h3>Risk Metrics Details</h3>
                        <table>
                          <thead>
                            <tr>
                              <th>Metric</th>
                              <th>Value</th>
                              <th>Description</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr>
                              <td>Volatility</td>
                              <td>{formatPercentage(riskMetrics.volatility)}</td>
                              <td>Measures the dispersion of returns for the portfolio</td>
                            </tr>
                            <tr>
                              <td>Sharpe Ratio</td>
                              <td>{riskMetrics.sharpe_ratio.toFixed(2)}</td>
                              <td>Measures risk-adjusted return (higher is better)</td>
                            </tr>
                            <tr>
                              <td>Beta</td>
                              <td>{riskMetrics.beta.toFixed(2)}</td>
                              <td>Measures portfolio's volatility compared to the market</td>
                            </tr>
                            <tr>
                              <td>Alpha</td>
                              <td>{formatPercentage(riskMetrics.alpha)}</td>
                              <td>Measures excess return compared to benchmark</td>
                            </tr>
                            <tr>
                              <td>Max Drawdown</td>
                              <td>{formatPercentage(riskMetrics.max_drawdown)}</td>
                              <td>Maximum observed loss from a peak to a trough</td>
                            </tr>
                            <tr>
                              <td>VaR (95%)</td>
                              <td>{formatPercentage(riskMetrics.var_95)}</td>
                              <td>Maximum potential loss with 95% confidence</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Holdings Tab */}
              {activeTab === 'holdings' && (
                <div className="tab-pane">
                  <div className="holdings-table">
                    <h3>Portfolio Holdings</h3>
                    <table>
                      <thead>
                        <tr>
                          <th>Security</th>
                          <th>ISIN</th>
                          <th>Asset Class</th>
                          <th>Sector</th>
                          <th>Quantity</th>
                          <th>Price</th>
                          <th>Value</th>
                          <th>Weight</th>
                        </tr>
                      </thead>
                      <tbody>
                        {portfolio.map((holding) => (
                          <tr key={holding.isin}>
                            <td>{holding.name}</td>
                            <td>{holding.isin}</td>
                            <td>{holding.asset_class}</td>
                            <td>{holding.sector}</td>
                            <td>{holding.quantity.toLocaleString()}</td>
                            <td>{formatCurrency(holding.price)}</td>
                            <td>{formatCurrency(holding.value)}</td>
                            <td>{formatPercentage(holding.value / totalValue)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>

      <style jsx>{`
        .portfolio-page {
          display: flex;
          flex-direction: column;
          gap: 30px;
        }

        .page-title {
          margin: 0 0 20px 0;
          font-size: 1.8rem;
          color: #2d3748;
        }

        .summary-cards {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 20px;
          margin-bottom: 10px;
        }

        .summary-card {
          background-color: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
          text-align: center;
        }

        .summary-card h3 {
          margin: 0 0 10px 0;
          font-size: 0.9rem;
          color: #718096;
          font-weight: 500;
        }

        .summary-value {
          font-size: 1.5rem;
          font-weight: 600;
          color: #2d3748;
        }

        .tab-navigation {
          display: flex;
          border-bottom: 1px solid #e2e8f0;
          margin-bottom: 20px;
          overflow-x: auto;
        }

        .tab-button {
          padding: 10px 20px;
          background: none;
          border: none;
          border-bottom: 2px solid transparent;
          cursor: pointer;
          font-size: 0.9rem;
          font-weight: 500;
          color: #718096;
          transition: all 0.2s ease;
          white-space: nowrap;
        }

        .tab-button:hover {
          color: #4299e1;
        }

        .tab-button.active {
          color: #4299e1;
          border-bottom-color: #4299e1;
        }

        .tab-content {
          background-color: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .tab-pane {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .overview-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 20px;
        }

        .allocation-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
          gap: 20px;
        }

        .chart-card {
          background-color: #f8fafc;
          border-radius: 8px;
          padding: 20px;
          border: 1px solid #e2e8f0;
        }

        .chart-card h3 {
          margin: 0 0 15px 0;
          font-size: 1rem;
          color: #4a5568;
          font-weight: 500;
          text-align: center;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
          gap: 15px;
        }

        .metric {
          background-color: white;
          border-radius: 8px;
          padding: 10px;
          border: 1px solid #e2e8f0;
          text-align: center;
        }

        .metric-label {
          font-size: 0.8rem;
          color: #718096;
          margin-bottom: 5px;
        }

        .metric-value {
          font-size: 1.1rem;
          font-weight: 600;
          color: #2d3748;
        }

        .performance-table,
        .risk-metrics-table,
        .holdings-table {
          overflow-x: auto;
        }

        .performance-table h3,
        .risk-metrics-table h3,
        .holdings-table h3 {
          margin: 0 0 15px 0;
          font-size: 1rem;
          color: #4a5568;
          font-weight: 500;
        }

        table {
          width: 100%;
          border-collapse: collapse;
        }

        th {
          text-align: left;
          padding: 12px 15px;
          background-color: #f8fafc;
          color: #4a5568;
          font-weight: 600;
          font-size: 0.9rem;
          border-bottom: 1px solid #e2e8f0;
        }

        td {
          padding: 12px 15px;
          border-bottom: 1px solid #e2e8f0;
          color: #4a5568;
          font-size: 0.9rem;
        }

        tr:last-child td {
          border-bottom: none;
        }

        .positive {
          color: #38a169;
        }

        .negative {
          color: #e53e3e;
        }

        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 300px;
        }

        .loading-spinner {
          border: 4px solid rgba(0, 0, 0, 0.1);
          border-radius: 50%;
          border-top: 4px solid #3498db;
          width: 30px;
          height: 30px;
          animation: spin 1s linear infinite;
          margin-bottom: 15px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .error-container {
          background-color: #fff5f5;
          border: 1px solid #fed7d7;
          border-radius: 8px;
          padding: 20px;
          text-align: center;
          color: #c53030;
        }

        .retry-button {
          background-color: #3182ce;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 10px;
        }

        .retry-button:hover {
          background-color: #2c5282;
        }

        @media (max-width: 768px) {
          .overview-grid,
          .allocation-grid {
            grid-template-columns: 1fr;
          }

          .summary-cards {
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          }
        }
      `}</style>
    </FinDocLayout>
  );
}
