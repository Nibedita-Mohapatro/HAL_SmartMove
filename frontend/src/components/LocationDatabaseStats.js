import React, { useState } from 'react';
import locationService from '../services/locationService';

const LocationDatabaseStats = () => {
  const [showStats, setShowStats] = useState(false);
  
  const locations = locationService.getPopularLocations();
  
  // Calculate statistics
  const calculateStats = () => {
    const stats = {
      odisha: {
        tier1_cities: locations.odisha.tier1_cities.length,
        tier2_cities: locations.odisha.tier2_cities.length,
        tier3_towns: locations.odisha.tier3_towns.length,
        villages: locations.odisha.villages.length,
        airports: locations.odisha.airports.length,
        transport: locations.odisha.transport.length,
        government: locations.odisha.government.length,
        total: locations.odisha.tier1_cities.length + 
               locations.odisha.tier2_cities.length + 
               locations.odisha.tier3_towns.length + 
               locations.odisha.villages.length +
               locations.odisha.airports.length +
               locations.odisha.transport.length +
               locations.odisha.government.length
      },
      andhra_pradesh: {
        tier1_cities: locations.andhra_pradesh.tier1_cities.length,
        tier2_cities: locations.andhra_pradesh.tier2_cities.length,
        tier3_towns: locations.andhra_pradesh.tier3_towns.length,
        villages: locations.andhra_pradesh.villages.length,
        airports: locations.andhra_pradesh.airports.length,
        total: locations.andhra_pradesh.tier1_cities.length + 
               locations.andhra_pradesh.tier2_cities.length + 
               locations.andhra_pradesh.tier3_towns.length + 
               locations.andhra_pradesh.villages.length +
               locations.andhra_pradesh.airports.length
      },
      telangana: {
        tier1_cities: locations.telangana.tier1_cities.length,
        tier2_cities: locations.telangana.tier2_cities.length,
        tier3_towns: locations.telangana.tier3_towns.length,
        villages: locations.telangana.villages.length,
        airports: locations.telangana.airports.length,
        transport: locations.telangana.transport.length,
        government: locations.telangana.government.length,
        tech_hubs: locations.telangana.tech_hubs.length,
        total: locations.telangana.tier1_cities.length + 
               locations.telangana.tier2_cities.length + 
               locations.telangana.tier3_towns.length + 
               locations.telangana.villages.length +
               locations.telangana.airports.length +
               locations.telangana.transport.length +
               locations.telangana.government.length +
               locations.telangana.tech_hubs.length
      },
      chhattisgarh: {
        tier1_cities: locations.chhattisgarh.tier1_cities.length,
        tier2_cities: locations.chhattisgarh.tier2_cities.length,
        tier3_towns: locations.chhattisgarh.tier3_towns.length,
        villages: locations.chhattisgarh.villages.length,
        airports: locations.chhattisgarh.airports.length,
        transport: locations.chhattisgarh.transport.length,
        government: locations.chhattisgarh.government.length,
        total: locations.chhattisgarh.tier1_cities.length + 
               locations.chhattisgarh.tier2_cities.length + 
               locations.chhattisgarh.tier3_towns.length + 
               locations.chhattisgarh.villages.length +
               locations.chhattisgarh.airports.length +
               locations.chhattisgarh.transport.length +
               locations.chhattisgarh.government.length
      }
    };
    
    stats.grandTotal = stats.odisha.total + stats.andhra_pradesh.total + 
                      stats.telangana.total + stats.chhattisgarh.total;
    
    return stats;
  };
  
  const stats = calculateStats();
  
  if (!showStats) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setShowStats(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg shadow-lg text-sm font-medium"
        >
          📊 Location Database Stats
        </button>
      </div>
    );
  }
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-11/12 max-w-4xl max-h-5/6 overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              🇮🇳 Comprehensive Indian Location Database
            </h2>
            <p className="text-gray-600 mt-1">
              Complete coverage of {stats.grandTotal} locations across 4 major states
            </p>
          </div>
          <button
            onClick={() => setShowStats(false)}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>
        
        {/* Statistics Grid */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Odisha */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg border border-blue-200">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold mr-3">
                  O
                </div>
                <div>
                  <h3 className="text-lg font-bold text-blue-900">Odisha</h3>
                  <p className="text-blue-700 text-sm">{stats.odisha.total} locations</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-blue-700">🏙️ Tier 1 Cities:</span>
                  <span className="font-medium">{stats.odisha.tier1_cities}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">🏘️ Tier 2 Cities:</span>
                  <span className="font-medium">{stats.odisha.tier2_cities}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">🏡 Towns:</span>
                  <span className="font-medium">{stats.odisha.tier3_towns}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">🏠 Villages:</span>
                  <span className="font-medium">{stats.odisha.villages}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">✈️ Airports:</span>
                  <span className="font-medium">{stats.odisha.airports}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">🚌 Transport:</span>
                  <span className="font-medium">{stats.odisha.transport}</span>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-blue-200">
                <div className="text-xs text-blue-600">
                  <strong>Famous Places:</strong> Konark Sun Temple, Chilika Lake, Puri Jagannath Temple
                </div>
              </div>
            </div>
            
            {/* Andhra Pradesh */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg border border-green-200">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white font-bold mr-3">
                  A
                </div>
                <div>
                  <h3 className="text-lg font-bold text-green-900">Andhra Pradesh</h3>
                  <p className="text-green-700 text-sm">{stats.andhra_pradesh.total} locations</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-green-700">🏙️ Tier 1 Cities:</span>
                  <span className="font-medium">{stats.andhra_pradesh.tier1_cities}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">🏘️ Tier 2 Cities:</span>
                  <span className="font-medium">{stats.andhra_pradesh.tier2_cities}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">🏡 Towns:</span>
                  <span className="font-medium">{stats.andhra_pradesh.tier3_towns}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">🏠 Villages:</span>
                  <span className="font-medium">{stats.andhra_pradesh.villages}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">✈️ Airports:</span>
                  <span className="font-medium">{stats.andhra_pradesh.airports}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">🚌 Transport:</span>
                  <span className="font-medium">Multiple</span>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-green-200">
                <div className="text-xs text-green-600">
                  <strong>Famous Places:</strong> Tirupati Temple, Araku Valley, Gandikota Canyon
                </div>
              </div>
            </div>
            
            {/* Telangana */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg border border-purple-200">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold mr-3">
                  T
                </div>
                <div>
                  <h3 className="text-lg font-bold text-purple-900">Telangana</h3>
                  <p className="text-purple-700 text-sm">{stats.telangana.total} locations</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-purple-700">🏙️ Tier 1 Cities:</span>
                  <span className="font-medium">{stats.telangana.tier1_cities}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">🏘️ Tier 2 Cities:</span>
                  <span className="font-medium">{stats.telangana.tier2_cities}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">🏡 Towns:</span>
                  <span className="font-medium">{stats.telangana.tier3_towns}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">🏠 Villages:</span>
                  <span className="font-medium">{stats.telangana.villages}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">💻 Tech Hubs:</span>
                  <span className="font-medium">{stats.telangana.tech_hubs}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">✈️ Airports:</span>
                  <span className="font-medium">{stats.telangana.airports}</span>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-purple-200">
                <div className="text-xs text-purple-600">
                  <strong>Famous Places:</strong> HITEC City, Ramoji Film City, Charminar
                </div>
              </div>
            </div>
            
            {/* Chhattisgarh */}
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-lg border border-orange-200">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-orange-600 rounded-full flex items-center justify-center text-white font-bold mr-3">
                  C
                </div>
                <div>
                  <h3 className="text-lg font-bold text-orange-900">Chhattisgarh</h3>
                  <p className="text-orange-700 text-sm">{stats.chhattisgarh.total} locations</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-orange-700">🏙️ Tier 1 Cities:</span>
                  <span className="font-medium">{stats.chhattisgarh.tier1_cities}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-orange-700">🏘️ Tier 2 Cities:</span>
                  <span className="font-medium">{stats.chhattisgarh.tier2_cities}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-orange-700">🏡 Towns:</span>
                  <span className="font-medium">{stats.chhattisgarh.tier3_towns}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-orange-700">🏠 Villages:</span>
                  <span className="font-medium">{stats.chhattisgarh.villages}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-orange-700">✈️ Airports:</span>
                  <span className="font-medium">{stats.chhattisgarh.airports}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-orange-700">🚌 Transport:</span>
                  <span className="font-medium">{stats.chhattisgarh.transport}</span>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-orange-200">
                <div className="text-xs text-orange-600">
                  <strong>Famous Places:</strong> Chitrakote Falls, Kanger Valley, Mainpat Hill Station
                </div>
              </div>
            </div>
          </div>
          
          {/* Summary */}
          <div className="mt-6 bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-lg border border-indigo-200">
            <h3 className="text-lg font-bold text-indigo-900 mb-4">📊 Database Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <div className="text-2xl font-bold text-indigo-600">{stats.grandTotal}</div>
                <div className="text-sm text-gray-600">Total Locations</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <div className="text-2xl font-bold text-green-600">4</div>
                <div className="text-sm text-gray-600">States Covered</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <div className="text-2xl font-bold text-purple-600">100%</div>
                <div className="text-sm text-gray-600">GPS Accurate</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <div className="text-2xl font-bold text-orange-600">Real-time</div>
                <div className="text-sm text-gray-600">Search Ready</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LocationDatabaseStats;
