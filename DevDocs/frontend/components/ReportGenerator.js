import React, { useState, useEffect } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import { FiFileText, FiCalendar, FiDownload, FiMail, FiPlus, FiTrash2 } from 'react-icons/fi';
import reportController from '../controllers/reportController';

const ReportGenerator = ({ portfolio, document }) => {
  const [activeTab, setActiveTab] = useState('generate');
  const [reportType, setReportType] = useState('portfolio');
  const [template, setTemplate] = useState('standard');
  const [config, setConfig] = useState({
    timeframe: '1Y',
    includeBenchmark: true,
    benchmark: 'S&P 500',
    includeHoldings: true,
    includeCharts: true
  });
  const [schedules, setSchedules] = useState([]);
  const [newSchedule, setNewSchedule] = useState({
    name: '',
    type: 'portfolio',
    template: 'standard',
    frequency: 'monthly',
    nextRunDate: new Date().toISOString().split('T')[0],
    recipients: [''],
    config: {
      timeframe: '1Y',
      includeBenchmark: true,
      benchmark: 'S&P 500'
    }
  });
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    // Load report schedules
    const loadSchedules = async () => {
      setLoading(true);
      try {
        const scheduleData = await reportController.getReportSchedules();
        setSchedules(scheduleData);
      } catch (error) {
        console.error('Error loading report schedules:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSchedules();
  }, []);

  const handleConfigChange = (key, value) => {
    setConfig(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleNewScheduleChange = (key, value) => {
    setNewSchedule(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleNewScheduleConfigChange = (key, value) => {
    setNewSchedule(prev => ({
      ...prev,
      config: {
        ...prev.config,
        [key]: value
      }
    }));
  };

  const handleRecipientChange = (index, value) => {
    const newRecipients = [...newSchedule.recipients];
    newRecipients[index] = value;
    setNewSchedule(prev => ({
      ...prev,
      recipients: newRecipients
    }));
  };

  const addRecipient = () => {
    setNewSchedule(prev => ({
      ...prev,
      recipients: [...prev.recipients, '']
    }));
  };

  const removeRecipient = (index) => {
    const newRecipients = [...newSchedule.recipients];
    newRecipients.splice(index, 1);
    setNewSchedule(prev => ({
      ...prev,
      recipients: newRecipients
    }));
  };

  const handleGenerateReport = async (format) => {
    if (!portfolio && reportType === 'portfolio') {
      alert('Please select a portfolio');
      return;
    }

    if (!document && reportType === 'document') {
      alert('Please select a document');
      return;
    }

    setGenerating(true);

    try {
      let reportData;

      if (reportType === 'portfolio') {
        reportData = await reportController.generatePortfolioReport(
          portfolio,
          template,
          config
        );
      } else {
        reportData = await reportController.generateDocumentReport(
          document,
          template,
          config
        );
      }

      let blob;

      if (format === 'pdf') {
        blob = await reportController.generatePdfReport(reportData);
      } else {
        blob = await reportController.generateExcelReport(reportData);
      }

      // Create a download link
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportData.title}.${format === 'pdf' ? 'pdf' : 'xlsx'}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Error generating report');
    } finally {
      setGenerating(false);
    }
  };

  const handleCreateSchedule = async () => {
    if (!newSchedule.name) {
      alert('Please enter a schedule name');
      return;
    }

    if (newSchedule.recipients.some(r => !r)) {
      alert('Please enter all recipient email addresses');
      return;
    }

    setLoading(true);

    try {
      const schedule = {
        ...newSchedule,
        portfolioId: reportType === 'portfolio' ? portfolio?.id : undefined,
        documentId: reportType === 'document' ? document?.id : undefined
      };

      const createdSchedule = await reportController.scheduleReport(schedule);
      setSchedules(prev => [...prev, createdSchedule]);

      // Reset form
      setNewSchedule({
        name: '',
        type: 'portfolio',
        template: 'standard',
        frequency: 'monthly',
        nextRunDate: new Date().toISOString().split('T')[0],
        recipients: [''],
        config: {
          timeframe: '1Y',
          includeBenchmark: true,
          benchmark: 'S&P 500'
        }
      });
    } catch (error) {
      console.error('Error creating schedule:', error);
      alert('Error creating schedule');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSchedule = async (scheduleId) => {
    if (!confirm('Are you sure you want to delete this schedule?')) {
      return;
    }

    setLoading(true);

    try {
      const success = await reportController.deleteReportSchedule(scheduleId);

      if (success) {
        setSchedules(prev => prev.filter(s => s.id !== scheduleId));
      }
    } catch (error) {
      console.error('Error deleting schedule:', error);
      alert('Error deleting schedule');
    } finally {
      setLoading(false);
    }
  };

  const renderGenerateTab = () => {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Report Configuration</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Report Type</label>
              <div className="flex space-x-4">
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    className="form-radio h-4 w-4 text-blue-600"
                    checked={reportType === 'portfolio'}
                    onChange={() => setReportType('portfolio')}
                  />
                  <span className="ml-2 text-sm text-gray-700">Portfolio Report</span>
                </label>
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    className="form-radio h-4 w-4 text-blue-600"
                    checked={reportType === 'document'}
                    onChange={() => setReportType('document')}
                  />
                  <span className="ml-2 text-sm text-gray-700">Document Report</span>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Report Template</label>
              <select
                value={template}
                onChange={(e) => setTemplate(e.target.value)}
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="standard">Standard</option>
                <option value="performance">Performance</option>
                <option value="allocation">Allocation</option>
                <option value="risk">Risk</option>
              </select>
            </div>

            {reportType === 'portfolio' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Time Period</label>
                  <select
                    value={config.timeframe}
                    onChange={(e) => handleConfigChange('timeframe', e.target.value)}
                    className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  >
                    <option value="1M">1 Month</option>
                    <option value="3M">3 Months</option>
                    <option value="6M">6 Months</option>
                    <option value="1Y">1 Year</option>
                    <option value="5Y">5 Years</option>
                  </select>
                </div>

                <div className="flex items-center">
                  <input
                    id="include-benchmark"
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    checked={config.includeBenchmark}
                    onChange={(e) => handleConfigChange('includeBenchmark', e.target.checked)}
                  />
                  <label htmlFor="include-benchmark" className="ml-2 block text-sm text-gray-700">
                    Include Benchmark Comparison
                  </label>
                </div>

                {config.includeBenchmark && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Benchmark</label>
                    <select
                      value={config.benchmark}
                      onChange={(e) => handleConfigChange('benchmark', e.target.value)}
                      className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                    >
                      <option value="S&P 500">S&P 500</option>
                      <option value="NASDAQ">NASDAQ</option>
                      <option value="Dow Jones">Dow Jones</option>
                      <option value="Russell 2000">Russell 2000</option>
                      <option value="FTSE 100">FTSE 100</option>
                    </select>
                  </div>
                )}
              </>
            )}

            <div className="flex items-center">
              <input
                id="include-holdings"
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                checked={config.includeHoldings}
                onChange={(e) => handleConfigChange('includeHoldings', e.target.checked)}
              />
              <label htmlFor="include-holdings" className="ml-2 block text-sm text-gray-700">
                Include Holdings Details
              </label>
            </div>

            <div className="flex items-center">
              <input
                id="include-charts"
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                checked={config.includeCharts}
                onChange={(e) => handleConfigChange('includeCharts', e.target.checked)}
              />
              <label htmlFor="include-charts" className="ml-2 block text-sm text-gray-700">
                Include Charts
              </label>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Generate Report</h3>

          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => handleGenerateReport('pdf')}
              disabled={generating}
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                generating ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
              } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
            >
              <FiDownload className="mr-2 -ml-1 h-5 w-5" />
              {generating ? 'Generating...' : 'Download PDF'}
            </button>

            <button
              type="button"
              onClick={() => handleGenerateReport('excel')}
              disabled={generating}
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                generating ? 'bg-gray-400' : 'bg-green-600 hover:bg-green-700'
              } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500`}
            >
              <FiDownload className="mr-2 -ml-1 h-5 w-5" />
              {generating ? 'Generating...' : 'Download Excel'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderScheduleTab = () => {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Scheduled Reports</h3>

          {loading ? (
            <div className="flex justify-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          ) : schedules.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Template
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Frequency
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Next Run
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Recipients
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {schedules.map((schedule) => (
                    <tr key={schedule.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{schedule.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{schedule.type}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{schedule.template}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{schedule.frequency}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {new Date(schedule.nextRunDate).toLocaleDateString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {schedule.recipients.join(', ')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          type="button"
                          onClick={() => handleDeleteSchedule(schedule.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <FiTrash2 className="h-5 w-5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-gray-500">No scheduled reports</p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Create Schedule</h3>

          <div className="space-y-4">
            <div>
              <label htmlFor="schedule-name" className="block text-sm font-medium text-gray-700 mb-1">
                Schedule Name
              </label>
              <input
                type="text"
                id="schedule-name"
                value={newSchedule.name}
                onChange={(e) => handleNewScheduleChange('name', e.target.value)}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Monthly Portfolio Report"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Report Type</label>
              <div className="flex space-x-4">
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    className="form-radio h-4 w-4 text-blue-600"
                    checked={newSchedule.type === 'portfolio'}
                    onChange={() => handleNewScheduleChange('type', 'portfolio')}
                  />
                  <span className="ml-2 text-sm text-gray-700">Portfolio Report</span>
                </label>
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    className="form-radio h-4 w-4 text-blue-600"
                    checked={newSchedule.type === 'document'}
                    onChange={() => handleNewScheduleChange('type', 'document')}
                  />
                  <span className="ml-2 text-sm text-gray-700">Document Report</span>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Report Template</label>
              <select
                value={newSchedule.template}
                onChange={(e) => handleNewScheduleChange('template', e.target.value)}
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="standard">Standard</option>
                <option value="performance">Performance</option>
                <option value="allocation">Allocation</option>
                <option value="risk">Risk</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
              <select
                value={newSchedule.frequency}
                onChange={(e) => handleNewScheduleChange('frequency', e.target.value)}
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="annually">Annually</option>
              </select>
            </div>

            <div>
              <label htmlFor="next-run-date" className="block text-sm font-medium text-gray-700 mb-1">
                First Run Date
              </label>
              <input
                type="date"
                id="next-run-date"
                value={newSchedule.nextRunDate}
                onChange={(e) => handleNewScheduleChange('nextRunDate', e.target.value)}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Recipients</label>
              {newSchedule.recipients.map((recipient, index) => (
                <div key={index} className="flex space-x-2 mb-2">
                  <input
                    type="email"
                    value={recipient}
                    onChange={(e) => handleRecipientChange(index, e.target.value)}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="email@example.com"
                  />
                  {newSchedule.recipients.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeRecipient(index)}
                      className="inline-flex items-center p-1 border border-transparent rounded-full shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                      <FiTrash2 className="h-4 w-4" />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={addRecipient}
                className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <FiPlus className="mr-2 -ml-1 h-4 w-4" />
                Add Recipient
              </button>
            </div>

            {newSchedule.type === 'portfolio' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Time Period</label>
                  <select
                    value={newSchedule.config.timeframe}
                    onChange={(e) => handleNewScheduleConfigChange('timeframe', e.target.value)}
                    className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  >
                    <option value="1M">1 Month</option>
                    <option value="3M">3 Months</option>
                    <option value="6M">6 Months</option>
                    <option value="1Y">1 Year</option>
                    <option value="5Y">5 Years</option>
                  </select>
                </div>

                <div className="flex items-center">
                  <input
                    id="schedule-include-benchmark"
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    checked={newSchedule.config.includeBenchmark}
                    onChange={(e) => handleNewScheduleConfigChange('includeBenchmark', e.target.checked)}
                  />
                  <label htmlFor="schedule-include-benchmark" className="ml-2 block text-sm text-gray-700">
                    Include Benchmark Comparison
                  </label>
                </div>

                {newSchedule.config.includeBenchmark && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Benchmark</label>
                    <select
                      value={newSchedule.config.benchmark}
                      onChange={(e) => handleNewScheduleConfigChange('benchmark', e.target.value)}
                      className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                    >
                      <option value="S&P 500">S&P 500</option>
                      <option value="NASDAQ">NASDAQ</option>
                      <option value="Dow Jones">Dow Jones</option>
                      <option value="Russell 2000">Russell 2000</option>
                      <option value="FTSE 100">FTSE 100</option>
                    </select>
                  </div>
                )}
              </>
            )}

            <div className="pt-4">
              <button
                type="button"
                onClick={handleCreateSchedule}
                disabled={loading}
                className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                  loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
                } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
              >
                <FiCalendar className="mr-2 -ml-1 h-5 w-5" />
                {loading ? 'Creating...' : 'Create Schedule'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <AccessibilityWrapper>
      <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('generate')}
              className={`py-4 px-6 text-sm font-medium flex items-center ${
                activeTab === 'generate'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <FiFileText className="mr-2 h-5 w-5" />
              Generate Report
            </button>
            <button
              onClick={() => setActiveTab('schedule')}
              className={`py-4 px-6 text-sm font-medium flex items-center ${
                activeTab === 'schedule'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <FiCalendar className="mr-2 h-5 w-5" />
              Schedule Reports
            </button>
          </nav>
        </div>
      </div>

      {activeTab === 'generate' ? renderGenerateTab() : renderScheduleTab()}
    </div>
    </AccessibilityWrapper>
  );
};

export default ReportGenerator;
