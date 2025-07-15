import React from 'react';

const BulkActionToolbar = ({ selectedCount, onBulkAction, onClearSelection }) => {
  return (
    <div className="bg-hal-blue text-white p-4 rounded-lg shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <span className="text-sm font-medium">
              {selectedCount} request{selectedCount !== 1 ? 's' : ''} selected
            </span>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => onBulkAction('approve')}
              className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
            >
              Bulk Approve
            </button>
            
            <button
              onClick={() => onBulkAction('reject')}
              className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
            >
              Bulk Reject
            </button>
            
            <button
              onClick={() => onBulkAction('cancel')}
              className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
            >
              Bulk Cancel
            </button>
          </div>
        </div>
        
        <button
          onClick={onClearSelection}
          className="text-white hover:text-gray-200 text-sm underline"
        >
          Clear Selection
        </button>
      </div>
    </div>
  );
};

export default BulkActionToolbar;
