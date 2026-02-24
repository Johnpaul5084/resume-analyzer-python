import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Upload, MessageSquare, Edit3, TrendingUp, User, LogOut } from 'lucide-react';

const navConfig = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "Analyze Resume", path: "/upload", icon: Upload },
    { name: "Career Mentor", path: "/mentor", icon: MessageSquare },
    { name: "Market Insights", path: "/insights", icon: TrendingUp },
    { name: "Profile", path: "/dashboard", icon: User },
];

export default function Sidebar() {
    const handleLogout = () => {
        localStorage.removeItem('access_token');
        window.location.href = '/';
    };

    return (
        <div className="w-72 bg-slate-950/50 backdrop-blur-2xl border-r border-white/5 p-8 hidden lg:flex flex-col h-screen sticky top-0">
            <div className="mb-12 flex items-center gap-3 px-2">
                <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(79,70,229,0.4)]">
                    <span className="text-white font-black text-xl italic">A</span>
                </div>
                <h1 className="text-xl font-black tracking-tighter text-white">AI RESUME ANALYZER</h1>
            </div>

            <nav className="space-y-2 flex-1">
                <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500 mb-6 px-2">Intelligence Suite</p>
                {navConfig.map((item) => (
                    <NavLink
                        key={item.name}
                        to={item.path}
                        className={({ isActive }) =>
                            `flex items-center gap-4 px-4 py-4 rounded-2xl transition-all duration-300 group ${isActive
                                ? "bg-indigo-600/10 text-indigo-400 border border-indigo-600/20 shadow-[0_0_15px_rgba(79,70,229,0.1)]"
                                : "text-slate-400 hover:text-white hover:bg-white/5 border border-transparent"
                            }`
                        }
                    >
                        <item.icon size={20} className="group-hover:scale-110 transition-transform" />
                        <span className="font-bold text-sm tracking-wide">{item.name}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="mt-auto pt-8 border-t border-white/5">
                <button
                    onClick={handleLogout}
                    className="flex items-center gap-4 px-4 py-4 rounded-2xl text-slate-500 hover:text-rose-400 hover:bg-rose-500/5 transition-all w-full group"
                >
                    <LogOut size={20} className="group-hover:translate-x-1 transition-transform" />
                    <span className="font-bold text-sm">Disconnect Link</span>
                </button>

                <div className="mt-8 bg-gradient-to-br from-indigo-600/20 to-transparent p-6 rounded-3xl border border-indigo-500/20">
                    <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2">System Status</p>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                        <span className="text-xs font-bold text-slate-300 tracking-tight">Neural Link Active</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
