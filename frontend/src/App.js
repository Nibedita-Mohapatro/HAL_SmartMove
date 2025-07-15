import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import Login from './components/Login';
import EmployeeDashboard from './components/EmployeeDashboard';
import AdminDashboard from './components/AdminDashboard';
import TransportDashboard from './components/TransportDashboard';
import RequestForm from './components/RequestForm';
import LocationDatabaseStats from './components/LocationDatabaseStats';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/employee" element={<EmployeeDashboard />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/transport" element={<TransportDashboard />} />
          <Route path="/employee/request" element={<RequestForm />} />
        </Routes>

        {/* Location Database Stats - Available on all pages */}
        <LocationDatabaseStats />
      </div>
    </Router>
  );
}

export default App;
