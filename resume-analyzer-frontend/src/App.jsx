import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import UploadResume from './components/UploadResume';
import ResumeDetail from './components/ResumeDetail';
import './index.css';

function PrivateRoute({ children }) {
    const token = localStorage.getItem('access_token');
    return token ? children : <Navigate to="/" />;
}

function App() {
    return (
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
            </Routes>
        </Router>
    );
}

export default App;
