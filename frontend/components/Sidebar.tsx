
import React from 'react';
import {
  LayoutGrid, Plus, FolderKanban, Settings, HelpCircle,
  Activity, Box, Database, GitBranch, ShieldCheck,
  Cpu, Terminal, Zap, Compass
} from 'lucide-react';
import { Project } from '../types';

interface SidebarProps {
  currentProject: string | null;
  onProjectSelect: (id: string | null) => void;
  onNewProject: () => void;
  projects: Project[];
  isWizardOpen?: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ currentProject, onProjectSelect, onNewProject, projects, isWizardOpen = false }) => {
  const isHomeActive = currentProject === null && !isWizardOpen;

  return (
    <div className="w-72 h-full bg-[#0d0d0d] border-r border-white/5 flex flex-col">
      {/* Brand - Heroic Heterogeneity */}
      <div className="p-8">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="w-10 h-10 bg-gradient-to-tr from-blue-600 to-indigo-500 rounded-xl flex items-center justify-center shadow-[0_0_25px_rgba(37,99,235,0.4)] animate-pulse">
              <Box className="text-white w-5 h-5" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full border-2 border-[#0d0d0d] flex items-center justify-center">
              <Zap className="w-2 h-2 text-white fill-current" />
            </div>
          </div>
          <div>
            <span className="font-black text-base tracking-tight text-white">SemantiCore</span>
            <div className="flex items-center gap-1.5">
              <div className="w-1 h-1 bg-blue-500 rounded-full"></div>
              <span className="text-[8px] font-bold text-blue-500/80 tracking-wider uppercase">PLATFORM</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar px-4 space-y-10 pb-8">
        
        {/* Navigation - Section 1: Orchestration */}
        <div className="space-y-1.5">
          <button
            onClick={() => onProjectSelect(null)}
            className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl transition-all group ${
              isHomeActive
              ? 'bg-blue-600 text-white shadow-[0_0_20px_rgba(37,99,235,0.4)] border border-blue-400/50'
              : 'text-blue-400/80 hover:text-blue-400 bg-blue-500/[0.03] border border-blue-500/10 hover:border-blue-500/30'
            }`}
          >
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-all ${
              isHomeActive ? 'bg-blue-500' : 'bg-blue-500/10'
            }`}>
              <Compass className={`w-4 h-4 transition-all ${isHomeActive ? 'text-white' : 'text-blue-400/60 group-hover:text-blue-400 group-hover:scale-110'}`} />
            </div>
            <span className="text-xs font-black uppercase tracking-widest">Overview</span>
          </button>

          <button
            onClick={onNewProject}
            className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl transition-all group ${
              isWizardOpen
              ? 'bg-blue-600 text-white shadow-[0_0_20px_rgba(37,99,235,0.4)] border border-blue-400/50'
              : 'text-blue-400/80 hover:text-blue-400 bg-blue-500/[0.03] border border-blue-500/10 hover:border-blue-500/30'
            }`}
          >
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-all ${
              isWizardOpen ? 'bg-blue-500' : 'bg-blue-500/10'
            }`}>
              <Plus className={`w-4 h-4 transition-transform ${isWizardOpen ? 'text-white rotate-45' : 'text-blue-400/60 group-hover:text-blue-400 group-hover:rotate-90'}`} />
            </div>
            <span className="text-xs font-black uppercase tracking-widest">New Deployment</span>
          </button>
        </div>

        {/* Section 2: Projects */}
        <div className="space-y-4">
          <div className="flex items-center justify-between px-2">
            <span className="text-[10px] font-bold text-white/30 uppercase tracking-wider">Projects</span>
            <span className="text-[9px] font-mono text-white/20">{projects.length}</span>
          </div>

          <div className="space-y-2">
            {projects.map(project => (
              <button
                key={project.id}
                onClick={() => onProjectSelect(project.id)}
                className={`w-full group p-1 transition-all rounded-2xl ${
                  currentProject === project.id 
                  ? 'bg-gradient-to-r from-blue-500/20 to-transparent' 
                  : ''
                }`}
              >
                <div className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all ${
                  currentProject === project.id 
                  ? 'bg-[#151515] border border-white/10 shadow-lg shadow-black/50' 
                  : 'hover:bg-white/[0.02]'
                }`}>
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                    currentProject === project.id ? 'bg-blue-600' : 'bg-white/[0.03] text-white/20'
                  }`}>
                    <Database className="w-4 h-4" />
                  </div>
                  <div className="flex flex-col items-start overflow-hidden text-left">
                    <span className={`truncate w-full text-[11px] font-black uppercase tracking-tight ${currentProject === project.id ? 'text-white' : 'text-white/40 group-hover:text-white/80'}`}>
                      {project.name}
                    </span>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[8px] font-mono text-white/10 tracking-widest uppercase">ID: NODE-00{project.id}</span>
                      {currentProject === project.id && <div className="w-1 h-1 bg-emerald-500 rounded-full animate-ping"></div>}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Section 3: Diagnostic Telemetry - Heterogeneous Layout */}
        <div className="bg-[#111] border border-white/5 rounded-3xl p-5 mx-1">
          <div className="flex items-center gap-2 mb-4">
            <Cpu className="w-3.5 h-3.5 text-emerald-500" />
            <span className="text-[10px] font-black text-white/30 uppercase tracking-widest">System Load</span>
          </div>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-[9px] font-mono text-white/20 uppercase">
                <span>Memory</span>
                <span className="text-emerald-500/60">32%</span>
              </div>
              <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                <div className="w-1/3 h-full bg-emerald-500/40"></div>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-[9px] font-mono text-white/20 uppercase">
                <span>Reasoning</span>
                <span className="text-blue-500/60">Optimized</span>
              </div>
              <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                <div className="w-3/4 h-full bg-blue-500/40"></div>
              </div>
            </div>
          </div>
          
          <div className="mt-5 pt-5 border-t border-white/[0.03] flex items-center justify-between">
            <div className="flex -space-x-1.5">
              {[1,2,3].map(i => (
                <div key={i} className="w-5 h-5 rounded-full border-2 border-[#111] bg-white/[0.05] flex items-center justify-center">
                  <div className="w-1.5 h-1.5 bg-white/20 rounded-full"></div>
                </div>
              ))}
            </div>
            <span className="text-[8px] font-black text-white/10 uppercase tracking-tighter">Cluster: 0x82A</span>
          </div>
        </div>

      </div>

      {/* Footer Nav - More Tool-like appearance */}
      <div className="p-4 border-t border-white/5 bg-black/40 grid grid-cols-2 gap-2">
        <button className="flex flex-col items-center justify-center p-2.5 rounded-xl text-white/20 hover:text-white hover:bg-white/[0.03] transition-all border border-transparent hover:border-white/5 group">
          <Terminal className="w-4 h-4 mb-1 group-hover:text-blue-500" />
          <span className="text-[8px] font-black uppercase tracking-widest">Logs</span>
        </button>
        <button className="flex flex-col items-center justify-center p-2.5 rounded-xl text-white/20 hover:text-white hover:bg-white/[0.03] transition-all border border-transparent hover:border-white/5 group">
          <Settings className="w-4 h-4 mb-1 group-hover:text-emerald-500" />
          <span className="text-[8px] font-black uppercase tracking-widest">Configs</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
