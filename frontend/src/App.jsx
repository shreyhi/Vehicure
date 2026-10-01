import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import FleetOverview from './pages/FleetOverview';
import LiveMonitoring from './pages/LiveMonitoring';
import VehicleHealth from './pages/VehicleHealth';
import AlertsPage from './pages/AlertsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import VehicleDetails from './pages/VehicleDetails';
import SystemHealth from './pages/SystemHealth';

export default function App() {
  const [activePage, setActivePage] = useState('overview');
  const [selectedVin, setSelectedVin] = useState(null);

  const handleSelectVehicle = (vin) => {
    setSelectedVin(vin);
    setActivePage('vehicle');
  };

  const handleBackToOverview = () => {
    setActivePage('overview');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      <Navbar activePage={activePage} setActivePage={setActivePage} />

      <div className="flex flex-1">
        <Sidebar activePage={activePage} setActivePage={setActivePage} />

        <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
          {activePage === 'overview' && <FleetOverview onSelectVehicle={handleSelectVehicle} />}
          {activePage === 'monitoring' && <LiveMonitoring onSelectVehicle={handleSelectVehicle} />}
          {activePage === 'health' && <VehicleHealth onSelectVehicle={handleSelectVehicle} />}
          {activePage === 'alerts' && <AlertsPage onSelectVehicle={handleSelectVehicle} />}
          {activePage === 'analytics' && <AnalyticsPage />}
          {activePage === 'vehicle' && <VehicleDetails vin={selectedVin} onBack={handleBackToOverview} />}
          {activePage === 'system' && <SystemHealth />}
        </main>
      </div>
    </div>
  );
}
