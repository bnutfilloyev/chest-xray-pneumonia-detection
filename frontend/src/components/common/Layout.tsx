import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Home, 
  Users, 
  Activity, 
  Settings, 
  Moon, 
  Sun, 
  Menu,
  X,
  HeartPulse,
  BarChart3,
  Stethoscope
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Separator } from '../ui/separator';
import { uzbekTexts } from '../../localization/uzbek';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const t = uzbekTexts;

  const menuItems = [
    { 
      text: t.navigation.dashboard, 
      icon: Home, 
      path: '/',
      color: 'text-blue-600'
    },
    { 
      text: t.navigation.patients, 
      icon: Users, 
      path: '/patients',
      color: 'text-green-600'
    },
    { 
      text: t.navigation.predictions, 
      icon: Activity, 
      path: '/predictions',
      color: 'text-purple-600'
    },
  ];

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('dark');
  };

  const currentPage = menuItems.find(item => item.path === location.pathname);

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 ${isDarkMode ? 'dark' : ''}`}>
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="lg:hidden"
              >
                {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
              </Button>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <HeartPulse size={20} className="text-white" />
                </div>
                <div className="hidden sm:block">
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                    {t.dashboard.title}
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {t.dashboard.subtitle}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleDarkMode}
                className="rounded-full"
              >
                {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
              </Button>
              
              <div className="hidden sm:flex items-center space-x-3">
                <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                </div>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {t.dashboard.online}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          fixed lg:static lg:translate-x-0
          z-40 w-64 h-[calc(100vh-4rem)] bg-white dark:bg-gray-800 
          border-r border-gray-200 dark:border-gray-700
          transition-transform duration-300 ease-in-out
        `}>
          <div className="p-6">
            <div className="space-y-2">
              {menuItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                
                return (
                  <Button
                    key={item.path}
                    variant={isActive ? "default" : "ghost"}
                    className={`
                      w-full justify-start h-12 px-4
                      ${isActive 
                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800' 
                        : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                      }
                    `}
                    onClick={() => {
                      navigate(item.path);
                      setIsSidebarOpen(false); // Close sidebar on mobile
                    }}
                  >
                    <Icon size={20} className={`mr-3 ${isActive ? item.color : 'text-gray-500'}`} />
                    <span className="font-medium">{item.text}</span>
                  </Button>
                );
              })}
            </div>

            <Separator className="my-6" />

            {/* Quick Stats */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Tizim holati
              </h3>
              
              <Card className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <BarChart3 size={16} className="text-green-600" />
                    <span className="text-sm font-medium">ML Model</span>
                  </div>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">98.5% aniqlik</p>
              </Card>

              <Card className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Stethoscope size={16} className="text-blue-600" />
                    <span className="text-sm font-medium">API</span>
                  </div>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">Faol</p>
              </Card>
            </div>
          </div>
        </aside>

        {/* Overlay for mobile */}
        {isSidebarOpen && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}

        {/* Main Content */}
        <main className="flex-1 min-h-[calc(100vh-4rem)] p-4 lg:p-6 w-0">
          {/* Breadcrumb */}
          <div className="mb-4 lg:mb-6">
            <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
              <Home size={16} />
              <span>/</span>
              <span className="text-gray-900 dark:text-white font-medium">
                {currentPage?.text || t.navigation.dashboard}
              </span>
            </div>
          </div>

          {/* Page Content */}
          <div className="w-full max-w-none">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;