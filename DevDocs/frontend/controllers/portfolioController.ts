import { Portfolio, PortfolioSummary, AssetAllocation, PerformanceMetrics, RiskMetrics } from '../models/types';

class PortfolioController {
  /**
   * Analyze a portfolio and generate summary metrics
   * @param portfolio The portfolio to analyze
   * @returns Portfolio summary with key metrics
   */
  async analyzePortfolio(portfolio: Portfolio): Promise<PortfolioSummary> {
    try {
      // Calculate asset allocation
      const assetAllocation = this.calculateAssetAllocation(portfolio);
      
      // Calculate performance metrics
      const performanceMetrics = this.calculatePerformanceMetrics(portfolio);
      
      // Calculate risk metrics
      const riskMetrics = this.calculateRiskMetrics(portfolio);
      
      // Generate portfolio summary
      const summary: PortfolioSummary = {
        totalValue: this.calculateTotalValue(portfolio),
        assetAllocation,
        performanceMetrics,
        riskMetrics,
        lastUpdated: new Date().toISOString()
      };
      
      return summary;
    } catch (error) {
      console.error('Error analyzing portfolio:', error);
      throw error;
    }
  }
  
  /**
   * Calculate the total value of a portfolio
   * @param portfolio The portfolio to calculate total value for
   * @returns The total value of the portfolio
   */
  calculateTotalValue(portfolio: Portfolio): number {
    return portfolio.holdings.reduce((total, holding) => total + holding.value, 0);
  }
  
  /**
   * Calculate asset allocation for a portfolio
   * @param portfolio The portfolio to calculate asset allocation for
   * @returns Asset allocation breakdown
   */
  calculateAssetAllocation(portfolio: Portfolio): AssetAllocation {
    const totalValue = this.calculateTotalValue(portfolio);
    
    // Group holdings by asset class
    const assetClasses: Record<string, number> = {};
    const sectors: Record<string, number> = {};
    const regions: Record<string, number> = {};
    
    // Calculate allocations
    portfolio.holdings.forEach(holding => {
      // Asset class allocation
      const assetClass = holding.assetClass || 'Unknown';
      assetClasses[assetClass] = (assetClasses[assetClass] || 0) + holding.value;
      
      // Sector allocation
      const sector = holding.sector || 'Unknown';
      sectors[sector] = (sectors[sector] || 0) + holding.value;
      
      // Region allocation
      const region = holding.region || 'Unknown';
      regions[region] = (regions[region] || 0) + holding.value;
    });
    
    // Convert to percentages
    const assetClassAllocation = Object.entries(assetClasses).map(([name, value]) => ({
      name,
      value,
      percentage: (value / totalValue) * 100
    }));
    
    const sectorAllocation = Object.entries(sectors).map(([name, value]) => ({
      name,
      value,
      percentage: (value / totalValue) * 100
    }));
    
    const regionAllocation = Object.entries(regions).map(([name, value]) => ({
      name,
      value,
      percentage: (value / totalValue) * 100
    }));
    
    return {
      assetClass: assetClassAllocation,
      sector: sectorAllocation,
      region: regionAllocation
    };
  }
  
  /**
   * Calculate performance metrics for a portfolio
   * @param portfolio The portfolio to calculate performance for
   * @returns Performance metrics
   */
  calculatePerformanceMetrics(portfolio: Portfolio): PerformanceMetrics {
    // In a real implementation, this would use historical data
    // For this demo, we'll use the provided performance data if available
    
    if (portfolio.performanceData) {
      const { startValue, currentValue, startDate, currentDate } = portfolio.performanceData;
      
      // Calculate absolute return
      const absoluteReturn = currentValue - startValue;
      
      // Calculate percentage return
      const percentageReturn = (absoluteReturn / startValue) * 100;
      
      // Calculate annualized return
      const startDateObj = new Date(startDate);
      const currentDateObj = new Date(currentDate);
      const yearDiff = (currentDateObj.getTime() - startDateObj.getTime()) / (1000 * 60 * 60 * 24 * 365);
      const annualizedReturn = (Math.pow((currentValue / startValue), (1 / yearDiff)) - 1) * 100;
      
      return {
        absoluteReturn,
        percentageReturn,
        annualizedReturn,
        startDate,
        currentDate
      };
    }
    
    // If no performance data is available, return placeholder values
    return {
      absoluteReturn: 0,
      percentageReturn: 0,
      annualizedReturn: 0,
      startDate: new Date().toISOString(),
      currentDate: new Date().toISOString()
    };
  }
  
  /**
   * Calculate risk metrics for a portfolio
   * @param portfolio The portfolio to calculate risk for
   * @returns Risk metrics
   */
  calculateRiskMetrics(portfolio: Portfolio): RiskMetrics {
    // In a real implementation, this would use historical price data
    // For this demo, we'll use the provided risk data if available
    
    if (portfolio.riskData) {
      return {
        volatility: portfolio.riskData.volatility,
        sharpeRatio: portfolio.riskData.sharpeRatio,
        maxDrawdown: portfolio.riskData.maxDrawdown,
        beta: portfolio.riskData.beta,
        alpha: portfolio.riskData.alpha
      };
    }
    
    // If no risk data is available, return placeholder values
    return {
      volatility: 0,
      sharpeRatio: 0,
      maxDrawdown: 0,
      beta: 0,
      alpha: 0
    };
  }
  
  /**
   * Get historical performance data for a portfolio
   * @param portfolio The portfolio to get historical data for
   * @param timeframe The timeframe to get data for (e.g., '1M', '3M', '1Y', '5Y')
   * @returns Historical performance data
   */
  async getHistoricalPerformance(portfolio: Portfolio, timeframe: string): Promise<any> {
    try {
      // In a real implementation, this would fetch data from an API
      // For this demo, we'll generate sample data
      
      let dataPoints = 0;
      let startDate = new Date();
      
      // Determine number of data points and start date based on timeframe
      switch (timeframe) {
        case '1M':
          dataPoints = 30;
          startDate.setMonth(startDate.getMonth() - 1);
          break;
        case '3M':
          dataPoints = 90;
          startDate.setMonth(startDate.getMonth() - 3);
          break;
        case '1Y':
          dataPoints = 365;
          startDate.setFullYear(startDate.getFullYear() - 1);
          break;
        case '5Y':
          dataPoints = 60; // Monthly data points for 5 years
          startDate.setFullYear(startDate.getFullYear() - 5);
          break;
        default:
          dataPoints = 30;
          startDate.setMonth(startDate.getMonth() - 1);
      }
      
      // Generate sample data
      const totalValue = this.calculateTotalValue(portfolio);
      const dates: string[] = [];
      const values: number[] = [];
      
      for (let i = 0; i < dataPoints; i++) {
        const date = new Date(startDate);
        date.setDate(startDate.getDate() + i);
        dates.push(date.toISOString().split('T')[0]);
        
        // Generate a random value with a slight upward trend
        const randomFactor = 0.98 + (Math.random() * 0.04); // Random between 0.98 and 1.02
        const trendFactor = 1 + (i / dataPoints) * 0.1; // Slight upward trend
        
        if (i === 0) {
          values.push(totalValue * 0.8); // Start at 80% of current value
        } else {
          values.push(values[i - 1] * randomFactor * trendFactor);
        }
      }
      
      return {
        dates,
        values
      };
    } catch (error) {
      console.error('Error getting historical performance:', error);
      throw error;
    }
  }
  
  /**
   * Compare a portfolio to a benchmark
   * @param portfolio The portfolio to compare
   * @param benchmark The benchmark to compare against
   * @returns Comparison data
   */
  async compareToIndex(portfolio: Portfolio, benchmark: string): Promise<any> {
    try {
      // In a real implementation, this would fetch benchmark data from an API
      // For this demo, we'll generate sample data
      
      const portfolioPerformance = await this.getHistoricalPerformance(portfolio, '1Y');
      
      // Generate benchmark data with a similar pattern but different values
      const benchmarkValues = portfolioPerformance.values.map((value: number, index: number) => {
        const randomFactor = 0.97 + (Math.random() * 0.06); // Random between 0.97 and 1.03
        return value * randomFactor;
      });
      
      // Normalize both datasets to start at 100
      const startPortfolioValue = portfolioPerformance.values[0];
      const startBenchmarkValue = benchmarkValues[0];
      
      const normalizedPortfolioValues = portfolioPerformance.values.map((value: number) => 
        (value / startPortfolioValue) * 100
      );
      
      const normalizedBenchmarkValues = benchmarkValues.map((value: number) => 
        (value / startBenchmarkValue) * 100
      );
      
      return {
        dates: portfolioPerformance.dates,
        portfolio: normalizedPortfolioValues,
        benchmark: normalizedBenchmarkValues,
        benchmarkName: benchmark
      };
    } catch (error) {
      console.error('Error comparing to index:', error);
      throw error;
    }
  }
}

const portfolioController = new PortfolioController();
export default portfolioController;
