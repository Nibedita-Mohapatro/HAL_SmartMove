import React, { useState } from 'react';
import DocumentManager from './DocumentManager';

const VehicleList = ({ vehicles, onEdit, onDelete, onToggleStatus }) => {
  const [showDocuments, setShowDocuments] = useState(null);
  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'available':
        return 'bg-green-100 text-green-800';
      case 'in_use':
        return 'bg-blue-100 text-blue-800';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800';
      case 'out_of_service':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'available':
        return 'Available';
      case 'in_use':
        return 'In Use';
      case 'maintenance':
        return 'Maintenance';
      case 'out_of_service':
        return 'Out of Service';
      default:
        return status;
    }
  };

  const getTypeIcon = (type) => {
    if (!type) return '🚗'; // Default icon if type is undefined

    switch (type.toLowerCase()) {
      case 'sedan':
        return '🚗';
      case 'suv':
        return '🚙';
      case 'bus':
        return '🚌';
      case 'van':
        return '🚐';
      case 'truck':
        return '🚚';
      default:
        return '🚗';
    }
  };

  const isMaintenanceDue = (nextMaintenance) => {
    if (!nextMaintenance) return false;
    const today = new Date();
    const maintenanceDate = new Date(nextMaintenance);
    const daysUntilMaintenance = Math.ceil((maintenanceDate - today) / (1000 * 60 * 60 * 24));
    return daysUntilMaintenance <= 7;
  };

  const isInsuranceExpiring = (insuranceExpiry) => {
    if (!insuranceExpiry) return false;
    const today = new Date();
    const expiryDate = new Date(insuranceExpiry);
    const daysUntilExpiry = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry <= 30;
  };

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Vehicle
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Details
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Maintenance
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {vehicles.map((vehicle) => (
              <tr key={vehicle.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="text-2xl mr-3">
                      {getTypeIcon(vehicle.type)}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {vehicle.registration_number || 'N/A'}
                      </div>
                      <div className="text-sm text-gray-500">
                        {vehicle.make || 'N/A'} {vehicle.model || 'N/A'} ({vehicle.year || 'N/A'})
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    Type: {vehicle.type ? vehicle.type.charAt(0).toUpperCase() + vehicle.type.slice(1) : 'N/A'}
                  </div>
                  <div className="text-sm text-gray-500">
                    Capacity: {vehicle.capacity || 'N/A'} • Fuel: {vehicle.fuel_type || 'N/A'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex flex-col space-y-1">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(vehicle.status)}`}>
                      {getStatusLabel(vehicle.status)}
                    </span>
                    {isInsuranceExpiring(vehicle.insurance_expiry) && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Insurance Expiring
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {vehicle.next_maintenance ? (
                      <div className={isMaintenanceDue(vehicle.next_maintenance) ? 'text-red-600' : ''}>
                        Next: {new Date(vehicle.next_maintenance).toLocaleDateString()}
                        {isMaintenanceDue(vehicle.next_maintenance) && (
                          <div className="text-xs text-red-600">Due Soon!</div>
                        )}
                      </div>
                    ) : (
                      <span className="text-gray-500">Not scheduled</span>
                    )}
                  </div>
                  {vehicle.last_maintenance && (
                    <div className="text-sm text-gray-500">
                      Last: {new Date(vehicle.last_maintenance).toLocaleDateString()}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => onEdit(vehicle)}
                      className="text-hal-blue hover:text-hal-navy"
                    >
                      Edit
                    </button>

                    <button
                      onClick={() => setShowDocuments(vehicle.id)}
                      className="text-purple-600 hover:text-purple-900"
                    >
                      Documents
                    </button>

                    <button
                      onClick={() => onToggleStatus(vehicle.id)}
                      className={`${
                        vehicle.status === 'available'
                          ? 'text-yellow-600 hover:text-yellow-900'
                          : 'text-green-600 hover:text-green-900'
                      }`}
                    >
                      {vehicle.status === 'available' ? 'Set Maintenance' : 'Set Available'}
                    </button>

                    <button
                      onClick={() => onDelete(vehicle.id)}
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

      {vehicles.length === 0 && (
        <div className="text-center py-8">
          <div className="text-gray-500">No vehicles found</div>
        </div>
      )}

      {/* Document Manager Modal */}
      {showDocuments && (
        <DocumentManager
          entityType="vehicle"
          entityId={showDocuments}
          onClose={() => setShowDocuments(null)}
        />
      )}
    </div>
  );
};

export default VehicleList;
