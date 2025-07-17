import React, { useState, useEffect } from 'react';
import RequestDetailsModal from './RequestDetailsModal';
import BulkActionToolbar from './BulkActionToolbar';
import AssignmentModal from './AssignmentModal';

const RequestManagement = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRequests, setSelectedRequests] = useState([]);
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    dateRange: 'all',
    searchTerm: ''
  });
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showAssignmentModal, setShowAssignmentModal] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/admin/requests', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setRequests(data.requests || []);
      } else {
        setError('Failed to fetch requests');
      }
    } catch (error) {
      console.error('Error fetching requests:', error);
      setError('Network error while fetching requests');
    } finally {
      setLoading(false);
    }
  };

  const handleBulkAction = async (action) => {
    if (selectedRequests.length === 0) {
      alert('Please select requests to perform bulk action');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const promises = selectedRequests.map(requestId =>
        fetch(`http://localhost:8000/api/v1/admin/requests/${requestId}/${action}`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        })
      );

      const results = await Promise.all(promises);
      const successCount = results.filter(r => r.ok).length;
      
      if (successCount === selectedRequests.length) {
        alert(`Successfully ${action}d ${successCount} requests`);
        setSelectedRequests([]);
        fetchRequests();
      } else {
        alert(`${action}d ${successCount} out of ${selectedRequests.length} requests`);
        fetchRequests();
      }
    } catch (error) {
      console.error('Error performing bulk action:', error);
      alert('Error performing bulk action');
    }
  };

  const handleRequestAction = async (requestId, action) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/admin/requests/${requestId}/${action}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message || `Request ${action}d successfully`);
        fetchRequests();
      } else {
        const errorData = await response.json();
        // Handle FastAPI validation errors
        if (Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map(err => err.msg || err.message || 'Validation error').join(', ');
          alert(errorMessages);
        } else {
          alert(errorData.detail || `Failed to ${action} request`);
        }
      }
    } catch (error) {
      console.error(`Error ${action}ing request:`, error);
      alert(`Network error while ${action}ing request`);
    }
  };

  const handleAssignRequest = async (requestId, assignmentData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/admin/requests/${requestId}/approve-with-assignment`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          vehicle_id: assignmentData.vehicle_id,
          driver_id: assignmentData.driver_id,
          estimated_departure: "08:00:00",
          estimated_arrival: "09:00:00",
          notes: assignmentData.notes || "Assigned via request management"
        })
      });

      if (response.ok) {
        const result = await response.json();
        return { success: true, message: result.message || 'Request approved and assigned successfully' };
      } else {
        const errorData = await response.json();
        if (Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map(err => err.msg || err.message || 'Validation error').join(', ');
          return { success: false, message: errorMessages };
        } else {
          return { success: false, message: errorData.detail || 'Failed to assign request' };
        }
      }
    } catch (error) {
      console.error('Error assigning request:', error);
      return { success: false, message: 'Network error while assigning request' };
    }
  };

  const filteredRequests = requests.filter(request => {
    const matchesStatus = filters.status === 'all' || request.status === filters.status;
    const matchesPriority = filters.priority === 'all' || request.priority === filters.priority;
    const matchesSearch = !filters.searchTerm || 
      request.origin.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
      request.destination.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
      request.purpose.toLowerCase().includes(filters.searchTerm.toLowerCase());

    return matchesStatus && matchesPriority && matchesSearch;
  });

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedRequests(filteredRequests.map(r => r.id));
    } else {
      setSelectedRequests([]);
    }
  };

  const handleSelectRequest = (requestId, checked) => {
    if (checked) {
      setSelectedRequests([...selectedRequests, requestId]);
    } else {
      setSelectedRequests(selectedRequests.filter(id => id !== requestId));
    }
  };

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityBadgeColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading requests...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Transport Request Management</h2>
          <p className="text-gray-600">Manage and approve transport requests</p>
        </div>
        <div className="text-sm text-gray-500">
          Total: {requests.length} | Filtered: {filteredRequests.length}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-red-800">{error}</div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search origin, destination, purpose..."
              value={filters.searchTerm}
              onChange={(e) => setFilters({...filters, searchTerm: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={filters.priority}
              onChange={(e) => setFilters({...filters, priority: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-hal-blue focus:border-transparent"
            >
              <option value="all">All Priority</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => setFilters({status: 'all', priority: 'all', dateRange: 'all', searchTerm: ''})}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Bulk Action Toolbar */}
      {selectedRequests.length > 0 && (
        <BulkActionToolbar
          selectedCount={selectedRequests.length}
          onBulkAction={handleBulkAction}
          onClearSelection={() => setSelectedRequests([])}
        />
      )}

      {/* Requests Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedRequests.length === filteredRequests.length && filteredRequests.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-gray-300 text-hal-blue focus:ring-hal-blue"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Request Details
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date & Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredRequests.map((request) => (
                <tr key={request.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="checkbox"
                      checked={selectedRequests.includes(request.id)}
                      onChange={(e) => handleSelectRequest(request.id, e.target.checked)}
                      className="rounded border-gray-300 text-hal-blue focus:ring-hal-blue"
                    />
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {request.origin} → {request.destination}
                      </div>
                      <div className="text-sm text-gray-500">
                        {request.passenger_count} passengers • {request.purpose}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{request.request_date}</div>
                    <div className="text-sm text-gray-500">{request.request_time}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(request.status)}`}>
                      {request.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityBadgeColor(request.priority)}`}>
                      {request.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          setSelectedRequest(request);
                          setShowDetailsModal(true);
                        }}
                        className="text-hal-blue hover:text-hal-navy"
                      >
                        View
                      </button>
                      {request.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleRequestAction(request.id, 'approve')}
                            className="text-green-600 hover:text-green-900"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => {
                              setSelectedRequest(request);
                              setShowAssignmentModal(true);
                            }}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Assign
                          </button>
                          <button
                            onClick={() => handleRequestAction(request.id, 'reject')}
                            className="text-red-600 hover:text-red-900"
                          >
                            Reject
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredRequests.length === 0 && (
          <div className="text-center py-8">
            <div className="text-gray-500">No requests found matching your criteria</div>
          </div>
        )}
      </div>

      {/* Request Details Modal */}
      {showDetailsModal && selectedRequest && (
        <RequestDetailsModal
          request={selectedRequest}
          onClose={() => {
            setShowDetailsModal(false);
            setSelectedRequest(null);
          }}
          onAction={handleRequestAction}
          onRefresh={fetchRequests}
        />
      )}

      {/* Assignment Modal */}
      {showAssignmentModal && selectedRequest && (
        <AssignmentModal
          request={selectedRequest}
          onClose={() => {
            setShowAssignmentModal(false);
            setSelectedRequest(null);
          }}
          onAssign={handleAssignRequest}
          onRefresh={fetchRequests}
        />
      )}
    </div>
  );
};

export default RequestManagement;
