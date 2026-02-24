import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import UploadResume from './components/UploadResume';
import ResumeDetail from './components/ResumeDetail';
import ResumeOptimizer from './components/ResumeOptimizer';
import CareerMentor from './components/CareerMentor';
import MarketInsights from './components/MarketInsights';
import DashboardLayout from './components/layout/DashboardLayout';
import './index.css';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: false,
            retry: 1,
            staleTime: 5 * 60 * 1000, // 5 minutes
        },
    },
});

function PrivateRoute({ children }) {
    const token = localStorage.getItem('access_token');
    return token ? <DashboardLayout>{children}</DashboardLayout> : <Navigate to="/" />;
}

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <Router>
                <Routes>
                    <Route path="/" element={<Login />} />
                    <Route
                        path="/dashboard"
                        element={
                            <PrivateRoute>
                                <Dashboard />
                            </PrivateRoute>
                        }
                    />
                    <Route
                        path="/upload"
                        element={
                            <PrivateRoute>
                                <UploadResume />
                            </PrivateRoute>
                        }
                    />
                    <Route
                        path="/resume/:id"
                        element={
                            <PrivateRoute>
                                <ResumeDetail />
                            </PrivateRoute>
                        }
                    />
                    <Route
                        path="/optimizer/:id"
                        element={
                            <PrivateRoute>
                                <ResumeOptimizer />
                            </PrivateRoute>
                        }
                    />
                    <Route
                        path="/mentor"
                        element={
                            <PrivateRoute>
                                <CareerMentor />
                            </PrivateRoute>
                        }
                    />
                    <Route
                        path="/insights"
                        element={
                            <PrivateRoute>
                                <MarketInsights />
                            </PrivateRoute>
                        }
                    />
                </Routes>
            </Router>
        </QueryClientProvider>
    );
}

export default App;
