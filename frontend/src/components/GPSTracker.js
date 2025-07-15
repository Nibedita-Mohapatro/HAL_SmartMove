import React from 'react';
import OpenStreetMapTracker from './OpenStreetMapTracker';

const GPSTracker = ({ tripId, userRole, onClose }) => {
  // Always use OpenStreetMap for free, secure mapping
  return (
    <OpenStreetMapTracker
      tripId={tripId}
      userRole={userRole}
      onClose={onClose}
    />
  );
};

export default GPSTracker;