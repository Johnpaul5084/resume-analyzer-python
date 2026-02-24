import React from 'react';
import Sidebar from './Sidebar';
import { motion, AnimatePresence } from 'framer-motion';

export default function DashboardLayout({ children }) {
    return (
        <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30">
            {/* SaaS Sidebar */}
            <Sidebar />

            {/* Main Content Area */}
            <main className="flex-1 overflow-x-hidden relative">
                {/* Background Ambient Glows */}
                <div className="fixed top-0 right-0 -translate-y-1/2 translate-x-1/2 w-[800px] h-[800px] bg-indigo-600/5 rounded-full blur-[120px] pointer-events-none"></div>
                <div className="fixed bottom-0 left-0 translate-y-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-blue-600/5 rounded-full blur-[100px] pointer-events-none"></div>

                <div className="relative z-10 min-h-screen flex flex-col">
                    {/* Topbar Placeholder / Header Section */}
                    <div className="h-20 border-b border-white/5 flex items-center justify-between px-8 lg:px-12 backdrop-blur-md bg-slate-950/20 sticky top-0 z-50">
                        <div className="flex items-center gap-4">
                            <h2 className="text-xs font-black uppercase tracking-[0.4em] text-slate-500">AI RESUME ANALYZER: Career Operating System</h2>
                        </div>
                        <div className="flex items-center gap-6">
                            <div className="hidden md:flex flex-col text-right">
                                <span className="text-sm font-black text-white px-2">Operator_01</span>
                                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Active Session</span>
                            </div>
                            <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center cursor-pointer hover:bg-white/10 transition-colors">
                                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                            </div>
                        </div>
                    </div>

                    {/* Page Content with Entrance Animation */}
                    <motion.div
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, ease: "easeOut" }}
                        className="p-8 lg:p-12 flex-1"
                    >
                        <AnimatePresence mode="wait">
                            {children}
                        </AnimatePresence>
                    </motion.div>

                    {/* Footer / Status Bar */}
                    <footer className="h-12 border-t border-white/5 px-12 flex items-center justify-between bg-slate-950/40 backdrop-blur-sm">
                        <span className="text-[9px] font-bold text-slate-600 uppercase tracking-widest leading-none">Powered by Hybrid RAG Intelligence</span>
                        <div className="flex items-center gap-4">
                            <span className="text-[9px] font-bold text-slate-600 uppercase tracking-widest">Latency: 24ms</span>
                            <span className="text-[9px] font-bold text-slate-600 uppercase tracking-widest text-indigo-500/50 hover:text-indigo-400 transition-colors cursor-pointer">v2.4.0-Stable</span>
                        </div>
                    </footer>
                </div>
            </main>
        </div>
    );
}
