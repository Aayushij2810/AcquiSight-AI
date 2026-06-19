import React, { useState } from 'react';
import { Layout } from './components/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { ScreenPage } from './pages/ScreenPage';
import { PortfolioPage } from './pages/PortfolioPage';
import { SettingsPage } from './pages/SettingsPage';
import { AppView } from './types';

export default function App() {
  const [view, setView] = useState<AppView>('dashboard');

  return (
    <Layout view={view} onNavigate={setView}>
      {view === 'dashboard' && <DashboardPage onNavigate={setView} />}
      {view === 'screen' && <ScreenPage />}
      {view === 'portfolio' && <PortfolioPage />}
      {view === 'settings' && <SettingsPage />}
    </Layout>
  );
}
