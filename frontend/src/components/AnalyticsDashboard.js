import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const AnalyticsDashboard = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [timeRange, setTimeRange] = useState('7days');

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/admin/analytics?range=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAnalyticsData(data);
      } else {
        // For demo purposes, use mock data if endpoint doesn't exist
        setAnalyticsData(getMockAnalyticsData());
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
      // Use mock data for demo
      setAnalyticsData(getMockAnalyticsData());
    } finally {
      setLoading(false);
    }
  };

  const getMockAnalyticsData = () => {
    return {
      summary: {
        total_requests: 156,
        completed_trips: 142,
        active_vehicles: 4,
        active_drivers: 3,
        utilization_rate: 89.2,
        avg_response_time: 12.5
      },
      request_trends: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        data: [12, 19, 15, 25, 22, 18, 16]
      },
      vehicle_utilization: {
        labels: ['KA01AB1234', 'KA01CD5678', 'KA01EF9012', 'KA01GH3456'],
        data: [85, 92, 78, 95]
      },
      route_popularity: {
        labels: ['Office to Airport', 'Office to Station', 'Office to Hotel', 'Inter-office', 'Client Visits'],
        data: [35, 28, 22, 18, 15]
      },
      status_distribution: {
        labels: ['Completed', 'Pending', 'In Progress', 'Cancelled'],
        data: [142, 8, 4, 2],
        colors: ['#10B981', '#F59E0B', '#3B82F6', '#EF4444']
      },
      driver_performance: [
        { name: 'Rajesh Kumar', rating: 4.8, trips: 45, efficiency: 94 },
        { name: 'Suresh Reddy', rating: 4.6, trips: 38, efficiency: 91 },
        { name: 'Mohammed Ali', rating: 4.7, trips: 42, efficiency: 93 }
      ],
      monthly_trends: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        requests: [120, 135, 148, 162, 155, 171, 156],
        completed: [115, 128, 142, 158, 148, 165, 142]
      }
    };
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
      },
    },
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading analytics...</div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500">No analytics data available</div>
      </div>
    );
  }

  const requestTrendsData = {
    labels: analyticsData.request_trends.labels,
    datasets: [
      {
        label: 'Transport Requests',
        data: analyticsData.request_trends.data,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const vehicleUtilizationData = {
    labels: analyticsData.vehicle_utilization.labels,
    datasets: [
      {
        label: 'Utilization %',
        data: analyticsData.vehicle_utilization.data,
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1,
      },
    ],
  };

  const statusDistributionData = {
    labels: analyticsData.status_distribution.labels,
    datasets: [
      {
        data: analyticsData.status_distribution.data,
        backgroundColor: analyticsData.status_distribution.colors,
        borderWidth: 2,
        borderColor: '#ffffff',
      },
    ],
  };

  const monthlyTrendsData = {
    labels: analyticsData.monthly_trends.labels,
    datasets: [
      {
        label: 'Requests',
        data: analyticsData.monthly_trends.requests,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Completed',
        data: analyticsData.monthly_trends.completed,
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
      },
    ],
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
          <p className="text-gray-600">Transport system performance and insights</p>
        </div>
        <div className="flex space-x-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
          >
            <option value="7days">Last 7 Days</option>
            <option value="30days">Last 30 Days</option>
            <option value="90days">Last 90 Days</option>
          </select>
          <button
            onClick={() => window.print()}
            className="bg-hal-blue hover:bg-hal-navy text-white px-4 py-2 rounded-md font-medium"
          >
            Export Report
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-blue-600">{analyticsData.summary.total_requests}</div>
          <div className="text-sm text-gray-600">Total Requests</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-green-600">{analyticsData.summary.completed_trips}</div>
          <div className="text-sm text-gray-600">Completed Trips</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-purple-600">{analyticsData.summary.active_vehicles}</div>
          <div className="text-sm text-gray-600">Active Vehicles</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-orange-600">{analyticsData.summary.active_drivers}</div>
          <div className="text-sm text-gray-600">Active Drivers</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-indigo-600">{analyticsData.summary.utilization_rate}%</div>
          <div className="text-sm text-gray-600">Utilization Rate</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-teal-600">{analyticsData.summary.avg_response_time}m</div>
          <div className="text-sm text-gray-600">Avg Response</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Request Trends */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Weekly Request Trends</h3>
          <Line data={requestTrendsData} options={chartOptions} />
        </div>

        {/* Vehicle Utilization */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Vehicle Utilization</h3>
          <Bar data={vehicleUtilizationData} options={chartOptions} />
        </div>

        {/* Status Distribution */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Request Status Distribution</h3>
          <Doughnut data={statusDistributionData} options={doughnutOptions} />
        </div>

        {/* Monthly Trends */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Monthly Performance</h3>
          <Line data={monthlyTrendsData} options={chartOptions} />
        </div>
      </div>

      {/* Driver Performance Table */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Driver Performance</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Driver
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rating
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Trips
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Efficiency
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {analyticsData.driver_performance.map((driver, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {driver.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center">
                      <span className="text-yellow-400">★</span>
                      <span className="ml-1">{driver.rating}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {driver.trips}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${driver.efficiency}%` }}
                        ></div>
                      </div>
                      <span>{driver.efficiency}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Popular Routes */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Popular Routes</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {analyticsData.route_popularity.labels.map((route, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="text-sm font-medium text-gray-900">{route}</div>
                <div className="flex items-center">
                  <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                    <div 
                      className="bg-hal-blue h-2 rounded-full" 
                      style={{ width: `${(analyticsData.route_popularity.data[index] / Math.max(...analyticsData.route_popularity.data)) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-500">{analyticsData.route_popularity.data[index]} trips</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
