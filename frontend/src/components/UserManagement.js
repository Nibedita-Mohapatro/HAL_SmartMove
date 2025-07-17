import React, { useState, useEffect } from 'react';
import CreateUserForm from './CreateUserForm';
import UserList from './UserList';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        setLoading(false);
        return;
      }

      const response = await fetch('http://localhost:8000/api/v1/admin/users/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
        setError('');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch users');
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('Network error while fetching users');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (userData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/admin/users/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const result = await response.json();
        setUsers([...users, result.user]);
        setShowCreateForm(false);
        setError('');
        return { success: true, message: 'User created successfully' };
      } else {
        const errorData = await response.json();
        return { success: false, message: errorData.detail || 'Failed to create user' };
      }
    } catch (error) {
      console.error('Error creating user:', error);
      return { success: false, message: 'Network error while creating user' };
    }
  };

  const handleDeleteUser = async (employeeId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/admin/users/by-employee-id/${employeeId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setUsers(users.filter(user => user.employee_id !== employeeId));
        setError('');
      } else {
        const errorData = await response.json();
        // Handle FastAPI validation errors
        if (Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map(err => err.msg || err.message || 'Validation error').join(', ');
          setError(errorMessages);
        } else {
          setError(errorData.detail || 'Failed to delete user');
        }
      }
    } catch (error) {
      console.error('Error deleting user:', error);
      setError('Network error while deleting user');
    }
  };

  const handleToggleStatus = async (employeeId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/admin/users/${employeeId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        setUsers(users.map(user => 
          user.employee_id === employeeId 
            ? { ...user, is_active: result.is_active }
            : user
        ));
        setError('');
      } else {
        const errorData = await response.json();
        // Handle FastAPI validation errors
        if (Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map(err => err.msg || err.message || 'Validation error').join(', ');
          setError(errorMessages);
        } else {
          setError(errorData.detail || 'Failed to update user status');
        }
      }
    } catch (error) {
      console.error('Error updating user status:', error);
      setError('Network error while updating user status');
    }
  };

  const handleResetPassword = async (employeeId, newPassword) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/admin/users/${employeeId}/reset-password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ new_password: newPassword }),
      });

      if (response.ok) {
        setError('');
        return { success: true, message: 'Password reset successfully' };
      } else {
        const errorData = await response.json();
        return { success: false, message: errorData.detail || 'Failed to reset password' };
      }
    } catch (error) {
      console.error('Error resetting password:', error);
      return { success: false, message: 'Network error while resetting password' };
    }
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading users...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-red-800">
            <span className="font-medium">Error:</span> {error}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4">

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
          <p className="text-gray-600">Manage admin, transport, and employee accounts</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-hal-blue hover:bg-hal-navy text-white px-4 py-2 rounded-md font-medium"
        >
          Create New User
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="text-red-800">
              <span className="font-medium">Error:</span> {error}
            </div>
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-gray-900">{users.length}</div>
          <div className="text-sm text-gray-600">Total Users</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-green-600">
            {users.filter(u => u.is_active).length}
          </div>
          <div className="text-sm text-gray-600">Active Users</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-red-600">
            {users.filter(u => u.role === 'admin').length}
          </div>
          <div className="text-sm text-gray-600">🔧 Admins</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-green-600">
            {users.filter(u => u.role === 'transport').length}
          </div>
          <div className="text-sm text-gray-600">🚗 Transport</div>
        </div>
      </div>

      {/* Additional Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-blue-600">
            {users.filter(u => u.role === 'employee').length}
          </div>
          <div className="text-sm text-gray-600">👤 Employees</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-red-600">
            {users.filter(u => !u.is_active).length}
          </div>
          <div className="text-sm text-gray-600">❌ Inactive</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-purple-600">
            {users.filter(u => u.permissions && u.permissions.includes('safety_override')).length}
          </div>
          <div className="text-sm text-gray-600">🛡️ Safety Override</div>
        </div>
      </div>

      {/* Create User Form Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <CreateUserForm
              onSubmit={handleCreateUser}
              onCancel={() => setShowCreateForm(false)}
            />
          </div>
        </div>
      )}

      {/* User List */}
      <UserList
        users={users}
        onDelete={handleDeleteUser}
        onToggleStatus={handleToggleStatus}
        onResetPassword={handleResetPassword}
      />
    </div>
  );
};

export default UserManagement;
