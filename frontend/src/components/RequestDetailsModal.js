import React, { useState } from 'react';
import AssignmentModal from './AssignmentModal';

const RequestDetailsModal = ({ request, onClose, onAction, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [showAssignmentModal, setShowAssignmentModal] = useState(false);

  const handleAction = async (action) => {
    setLoading(true);
    try {
      await onAction(request.id, action);
      onRefresh();
      onClose();
    } catch (error) {
      console.error(`Error ${action}ing request:`, error);
    } finally {
      setLoading(false);
    }
  };

  // Get current user role
  const getCurrentUserRole = () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      return user.role;
    }
    return null;
  };

  const userRole = getCurrentUserRole();

  const handleAssignment = async (requestId, assignmentData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/admin/requests/${requestId}/assign`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(assignmentData),
      });

      if (response.ok) {
        return { success: true, message: 'Resources assigned successfully' };
      } else {
        const errorData = await response.json();
        return { success: false, message: errorData.detail || 'Failed to assign resources' };
      }
    } catch (error) {
      console.error('Error assigning resources:', error);
      return { success: false, message: 'Network error while assigning resources' };
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

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-medium text-gray-900">Transport Request Details</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            &times;
          </button>
        </div>

        {/* Request Information */}
        <div className="space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Request ID</label>
              <div className="mt-1 text-sm text-gray-900">#{request.id}</div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Status</label>
              <div className="mt-1">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(request.status)}`}>
                  {request.status}
                </span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Priority</label>
              <div className="mt-1">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityBadgeColor(request.priority)}`}>
                  {request.priority}
                </span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Passenger Count</label>
              <div className="mt-1 text-sm text-gray-900">{request.passenger_count}</div>
            </div>
          </div>

          {/* Route Information */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-3">Route Information</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Origin</label>
                <div className="mt-1 text-sm text-gray-900">{request.origin}</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Destination</label>
                <div className="mt-1 text-sm text-gray-900">{request.destination}</div>
              </div>
            </div>
          </div>

          {/* Schedule Information */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-3">Schedule</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Date</label>
                <div className="mt-1 text-sm text-gray-900">{request.request_date}</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Time</label>
                <div className="mt-1 text-sm text-gray-900">{request.request_time}</div>
              </div>
            </div>
          </div>

          {/* Purpose */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Purpose</label>
            <div className="mt-1 text-sm text-gray-900">{request.purpose}</div>
          </div>

          {/* Timestamps */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-3">Request History</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Created At</label>
                <div className="mt-1 text-sm text-gray-900">
                  {request.created_at ? new Date(request.created_at).toLocaleString() : 'N/A'}
                </div>
              </div>
              {request.updated_at && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Last Updated</label>
                  <div className="mt-1 text-sm text-gray-900">
                    {new Date(request.updated_at).toLocaleString()}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Assignment Section (for approved requests) */}
          {request.status === 'approved' && (
            <div>
              <h4 className="text-md font-medium text-gray-900 mb-3">Assignment</h4>
              <div className="bg-gray-50 p-4 rounded-md">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Assigned Vehicle</label>
                    <div className="mt-1 text-sm text-gray-900">
                      {request.assigned_vehicle || 'Not assigned yet'}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Assigned Driver</label>
                    <div className="mt-1 text-sm text-gray-900">
                      {request.assigned_driver || 'Not assigned yet'}
                    </div>
                  </div>
                </div>
                {request.assignment_notes && (
                  <div className="mt-3">
                    <label className="block text-sm font-medium text-gray-700">Assignment Notes</label>
                    <div className="mt-1 text-sm text-gray-900">{request.assignment_notes}</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Close
            </button>
            
            {request.status === 'pending' && userRole === 'admin' && (
              <>
                <button
                  onClick={() => handleAction('approve')}
                  disabled={loading}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Processing...' : 'Approve'}
                </button>
                <button
                  onClick={() => handleAction('reject')}
                  disabled={loading}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Processing...' : 'Reject'}
                </button>
              </>
            )}
            
            {request.status === 'approved' && (
              <>
                <button
                  onClick={() => setShowAssignmentModal(true)}
                  disabled={loading}
                  className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Assign Resources
                </button>
                <button
                  onClick={() => handleAction('complete')}
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Processing...' : 'Mark Complete'}
                </button>
              </>
            )}
            
            {['pending', 'approved'].includes(request.status) && (
              <button
                onClick={() => handleAction('cancel')}
                disabled={loading}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Processing...' : 'Cancel'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Assignment Modal */}
      {showAssignmentModal && (
        <AssignmentModal
          request={request}
          onClose={() => setShowAssignmentModal(false)}
          onAssign={handleAssignment}
          onRefresh={onRefresh}
        />
      )}
    </div>
  );
};

export default RequestDetailsModal;
