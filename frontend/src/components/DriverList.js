import React, { useState } from 'react';
import DocumentManager from './DocumentManager';

const DriverList = ({ drivers, onEdit, onDelete, onToggleStatus }) => {
  const [showDocuments, setShowDocuments] = useState(null);
  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-red-100 text-red-800';
      case 'on_leave':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'active':
        return 'Active';
      case 'inactive':
        return 'Inactive';
      case 'on_leave':
        return 'On Leave';
      default:
        return status;
    }
  };

  const isLicenseExpiring = (expiryDate) => {
    if (!expiryDate) return false;
    const today = new Date();
    const expiry = new Date(expiryDate);
    const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry <= 30;
  };

  const calculateAge = (birthDate) => {
    if (!birthDate) return 'N/A';
    const today = new Date();
    const birth = new Date(birthDate);
    const age = Math.floor((today - birth) / (365.25 * 24 * 60 * 60 * 1000));
    return age;
  };

  const getRatingStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="text-yellow-400">★</span>);
    }

    if (hasHalfStar) {
      stars.push(<span key="half" className="text-yellow-400">☆</span>);
    }

    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<span key={`empty-${i}`} className="text-gray-300">★</span>);
    }

    return stars;
  };

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Driver
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Contact
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                License
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Performance
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {drivers.map((driver) => (
              <tr key={driver.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10">
                      <div className="h-10 w-10 rounded-full bg-hal-blue flex items-center justify-center text-white font-medium">
                        {driver.first_name?.charAt(0)}{driver.last_name?.charAt(0)}
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {driver.first_name} {driver.last_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {driver.employee_id} • Age: {calculateAge(driver.date_of_birth)}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{driver.phone}</div>
                  <div className="text-sm text-gray-500">{driver.email}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {driver.license_number}
                  </div>
                  <div className="text-sm text-gray-500">
                    {driver.license_type}
                  </div>
                  <div className={`text-xs ${isLicenseExpiring(driver.license_expiry) ? 'text-red-600 font-medium' : 'text-gray-500'}`}>
                    Expires: {driver.license_expiry ? new Date(driver.license_expiry).toLocaleDateString() : 'N/A'}
                    {isLicenseExpiring(driver.license_expiry) && (
                      <span className="ml-1">⚠️</span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex flex-col space-y-1">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(driver.status)}`}>
                      {getStatusLabel(driver.status)}
                    </span>
                    {isLicenseExpiring(driver.license_expiry) && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        License Expiring
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    <div className="flex items-center">
                      {getRatingStars(driver.rating || 0)}
                      <span className="ml-2 text-gray-600">
                        {driver.rating ? driver.rating.toFixed(1) : '0.0'}
                      </span>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    {driver.total_trips || 0} trips completed
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => onEdit(driver)}
                      className="text-hal-blue hover:text-hal-navy"
                    >
                      Edit
                    </button>

                    <button
                      onClick={() => setShowDocuments(driver.id)}
                      className="text-purple-600 hover:text-purple-900"
                    >
                      Documents
                    </button>

                    <button
                      onClick={() => onToggleStatus(driver.id)}
                      className={`${
                        driver.status === 'active'
                          ? 'text-yellow-600 hover:text-yellow-900'
                          : 'text-green-600 hover:text-green-900'
                      }`}
                    >
                      {driver.status === 'active' ? 'Deactivate' : 'Activate'}
                    </button>

                    <button
                      onClick={() => onDelete(driver.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {drivers.length === 0 && (
        <div className="text-center py-8">
          <div className="text-gray-500">No drivers found</div>
        </div>
      )}

      {/* Document Manager Modal */}
      {showDocuments && (
        <DocumentManager
          entityType="driver"
          entityId={showDocuments}
          onClose={() => setShowDocuments(null)}
        />
      )}
    </div>
  );
};

export default DriverList;
