
import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ProjectWizard from './components/ProjectWizard';
import { Project } from './types';
import { listProjects } from './src/api/projects';
import {
  LayoutGrid, Database, Share2, MoreVertical, Search, Bell, Network,
  FolderKanban, ShieldCheck, Box, Activity, Plus, Clock, ChevronRight,
  HardDrive, Layers, Cpu, Compass, Globe, Zap
} from 'lucide-react';

const App: React.FC = () => {
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch projects on mount
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await listProjects();
        setProjects(data);
      } catch (error) {
        console.error('Failed to fetch projects:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProjects();
  }, []);

  const activeProject = projects.find(p => p.id === currentProjectId);

  const handleNewProject = () => {
    setCurrentProjectId(null);
    setIsCreating(true);
  };

  const handleProjectSelect = (id: string | null) => {
    setIsCreating(false);
    setCurrentProjectId(id);
  };

  const navigateHome = () => {
    setIsCreating(false);
    setCurrentProjectId(null);
  };

  return (
    <div className="flex h-screen w-full bg-[#0a0a0a] overflow-hidden text-white font-inter">
      <Sidebar
        currentProject={currentProjectId}
        onProjectSelect={handleProjectSelect}
        onNewProject={handleNewProject}
        projects={projects}
        isWizardOpen={isCreating}
      />
      
      <main className="flex-1 flex flex-col relative overflow-hidden bg-[#080808]">
        {/* Technical Header */}
        <header className="h-14 border-b border-white/5 flex items-center justify-between px-6 bg-[#0d0d0d] z-20 shrink-0">
          <div className="flex items-center gap-3">
            <button 
              onClick={navigateHome}
              className={`flex items-center gap-2 text-[9px] font-black uppercase tracking-[0.2em] transition-all px-3 py-1.5 rounded-lg ${!activeProject && !isCreating ? 'bg-blue-600/10 text-blue-400' : 'text-white/20 hover:text-white hover:bg-white/5'}`}
            >
              <Compass className="w-3.5 h-3.5" />
              Overview
            </button>
            <div className="w-[1px] h-4 bg-white/5 mx-1"></div>
            {activeProject ? (
              <div className="flex items-center gap-3 animate-in fade-in">
                <span className="text-[9px] font-black text-white/20 uppercase tracking-[0.2em]">Active:</span>
                <h1 className="text-sm font-bold tracking-tight text-blue-400 truncate max-w-[200px]">{activeProject.name}</h1>
                <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full hidden sm:flex">
                   <div className="w-1 h-1 rounded-full bg-emerald-500 animate-pulse"></div>
                   <span className="text-[7px] font-bold text-emerald-500 uppercase tracking-wider">VERIFIED</span>
                </div>
              </div>
            ) : isCreating ? (
              <div className="flex items-center gap-2 animate-pulse">
                <Zap className="w-3 h-3 text-amber-500" />
                <h1 className="text-[9px] font-black uppercase tracking-[0.2em] text-white/40">Initializing Core</h1>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Globe className="w-3 h-3 text-white/10" />
                <h1 className="text-[9px] font-black uppercase tracking-[0.2em] text-white/10">Global Orchestration</h1>
              </div>
            )}
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden lg:flex items-center gap-3 px-3 py-1 bg-white/[0.02] border border-white/5 rounded-full text-[8px] font-mono text-white/30 uppercase tracking-widest">
               <div className="flex items-center gap-1.5">
                 <div className="w-1 h-1 bg-blue-500 rounded-full"></div>
                 <span>Engine: v3.1</span>
               </div>
               <div className="w-[1px] h-3 bg-white/10"></div>
               <div className="flex items-center gap-1.5">
                 <ShieldCheck className="w-3 h-3 text-emerald-500" />
                 <span>Secure</span>
               </div>
            </div>
            <div className="w-8 h-8 rounded-xl bg-white/[0.05] border border-white/10 flex items-center justify-center text-white/40 hover:text-white transition-all cursor-pointer">
              <Bell className="w-3.5 h-3.5" />
            </div>
          </div>
        </header>

        {/* Workspace Area */}
        <div className="flex-1 overflow-hidden relative">
          {isCreating ? (
            <ProjectWizard onComplete={navigateHome} />
          ) : activeProject ? (
            <div className="p-6 lg:p-8 h-full flex flex-col gap-6 animate-in fade-in slide-in-from-left-4 overflow-y-auto custom-scrollbar max-w-[1600px] mx-auto w-full">
               <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="p-4 bg-[#0d0d0d] border border-white/5 rounded-2xl shadow-xl">
                     <div className="text-[8px] font-black uppercase text-white/20 tracking-widest mb-2">Ingested Records</div>
                     <div className="text-xl lg:text-2xl font-black tabular-nums italic text-blue-400">{(activeProject.dataSources.length * 1150).toLocaleString()}</div>
                  </div>
                  <div className="p-4 bg-[#0d0d0d] border border-white/5 rounded-2xl shadow-xl">
                     <div className="text-[8px] font-black uppercase text-white/20 tracking-widest mb-2">Ontological Nodes</div>
                     <div className="text-xl lg:text-2xl font-black tabular-nums italic">{activeProject.nodeCount || 24}</div>
                  </div>
                  <div className="p-4 bg-[#0d0d0d] border border-white/5 rounded-2xl shadow-xl">
                     <div className="text-[8px] font-black uppercase text-white/20 tracking-widest mb-2">Relations</div>
                     <div className="text-xl lg:text-2xl font-black tabular-nums italic">{activeProject.relationCount || '2.4k'}</div>
                  </div>
                  <div className="p-4 bg-[#0d0d0d] border border-white/5 rounded-2xl shadow-xl">
                     <div className="text-[8px] font-black uppercase text-white/20 tracking-widest mb-2">Stability</div>
                     <div className="text-xl lg:text-2xl font-black tabular-nums italic text-emerald-500">98.2%</div>
                  </div>
               </div>

               <div className="flex-1 grid grid-cols-12 gap-6 min-h-[400px]">
                  <div className="col-span-12 lg:col-span-8 glass rounded-3xl p-6 lg:p-8 flex flex-col gap-6 overflow-hidden shadow-2xl">
                     <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                           <Activity className="w-4 h-4 text-blue-500" />
                           <h2 className="text-lg font-black uppercase tracking-tight italic">Materialization Log</h2>
                        </div>
                        <button className="text-[9px] font-black uppercase text-blue-500 hover:text-blue-400 tracking-widest bg-blue-500/10 px-3 py-1.5 rounded-full transition-all">Live Trace</button>
                     </div>
                     <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-3">
                        {[1,2,3,4,5,6,7,8].map(i => (
                          <div key={i} className="p-4 bg-white/[0.02] border border-white/5 rounded-xl flex items-center justify-between hover:bg-white/[0.04] transition-all group">
                             <div className="flex items-center gap-4">
                                <div className="w-8 h-8 rounded-lg bg-blue-500/5 flex items-center justify-center border border-blue-500/10 group-hover:bg-blue-600 transition-all">
                                   <Layers className="w-3.5 h-3.5 text-blue-500 group-hover:text-white" />
                                </div>
                                <div>
                                   <div className="text-[10px] font-black text-white/80 uppercase tracking-tight truncate max-w-[150px] sm:max-w-none">Resolved: {activeProject.name.split(' ')[0]}_EID_{i * 102}</div>
                                   <div className="text-[8px] text-white/20 font-mono mt-0.5 uppercase tracking-widest">Trace: {activeProject.dataSources[0]?.name}</div>
                                </div>
                             </div>
                             <div className="flex items-center gap-2">
                               <div className="w-1 h-1 rounded-full bg-emerald-500"></div>
                               <span className="text-[8px] font-black text-white/20 uppercase">Synched</span>
                             </div>
                          </div>
                        ))}
                     </div>
                  </div>
                  <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
                     <div className="p-8 lg:p-10 bg-gradient-to-br from-[#121212] to-[#0a0a0a] border border-white/5 rounded-[32px] flex-1 flex flex-col items-center justify-center text-center shadow-2xl group cursor-pointer hover:border-blue-500/20 transition-all">
                        <div className="w-16 h-16 bg-blue-600/10 rounded-2xl flex items-center justify-center mb-6 border border-blue-500/20 group-hover:scale-110 transition-transform">
                          <Network className="w-8 h-8 text-blue-500" />
                        </div>
                        <h3 className="text-xl font-black uppercase italic tracking-tight mb-3">Knowledge Explorer</h3>
                        <p className="text-xs text-white/30 leading-relaxed max-w-[200px] font-medium">Interact with the graph for the <span className="text-blue-400">{activeProject.name}</span> deployment.</p>
                        <button className="mt-8 bg-white text-black text-[9px] font-black uppercase px-8 py-3 rounded-xl hover:bg-neutral-200 transition-all tracking-[0.2em] shadow-xl shadow-white/5">Launch Interface</button>
                     </div>
                  </div>
               </div>
            </div>
          ) : (
            /* OVERVIEW (DEFAULT VIEW) */
            <div className="p-6 lg:p-10 h-full flex flex-col animate-in fade-in slide-in-from-bottom-8 overflow-y-auto custom-scrollbar max-w-[1800px] mx-auto w-full">
              <div className="mb-10 lg:mb-14 flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                  <h2 className="text-3xl lg:text-4xl font-black tracking-tight mb-2">SemantiCore</h2>
                  <p className="text-white/30 font-medium text-lg max-w-2xl leading-relaxed">Semantic knowledge graph platform for domain-specific ontologies</p>
                </div>
                <div className="flex gap-4">
                  <div className="p-4 bg-[#0d0d0d] border border-white/5 rounded-2xl flex items-center gap-4 shadow-xl">
                    <div className="w-10 h-10 bg-emerald-500/10 rounded-xl flex items-center justify-center border border-emerald-500/20">
                      <Cpu className="w-5 h-5 text-emerald-500" />
                    </div>
                    <div>
                      <div className="text-[8px] font-black text-white/20 uppercase tracking-widest mb-0.5">Engine Load</div>
                      <div className="text-xl font-black tabular-nums italic">14%</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-20">
                {/* Existing Project Cards */}
                {isLoading ? (
                  <div className="col-span-full flex items-center justify-center py-20">
                    <div className="text-white/40 text-sm">Loading projects...</div>
                  </div>
                ) : projects.length === 0 ? (
                  <div className="col-span-full flex flex-col items-center justify-center py-20 text-center">
                    <Database className="w-16 h-16 text-white/10 mb-4" />
                    <h3 className="text-lg font-bold text-white/40 mb-2">No Projects Yet</h3>
                    <p className="text-sm text-white/20">Create your first semantic knowledge graph</p>
                  </div>
                ) : null}

                {projects.map(project => (
                  <div 
                    key={project.id}
                    onClick={() => handleProjectSelect(project.id)}
                    className="group p-6 min-h-[16rem] lg:min-h-[18rem] bg-[#0d0d0d] border border-white/5 rounded-3xl hover:border-white/20 hover:bg-[#111] transition-all cursor-pointer flex flex-col relative overflow-hidden shadow-2xl"
                  >
                    <div className="flex justify-between items-start mb-6">
                      <div className="w-12 h-12 bg-blue-600/10 rounded-2xl flex items-center justify-center border border-blue-500/20 group-hover:bg-blue-600 transition-all shadow-lg group-hover:shadow-blue-500/20">
                        <Database className="w-6 h-6 text-blue-500 group-hover:text-white" />
                      </div>
                      <div className="flex flex-col items-end">
                        <span className="text-[8px] font-black text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full uppercase tracking-widest mb-1.5 border border-emerald-500/10">v{project.version}.0.4</span>
                        <div className="text-[8px] text-white/20 font-mono uppercase tracking-tighter italic">{project.lastModified}</div>
                      </div>
                    </div>
                    
                    <div className="flex-1">
                      <h3 className="text-xl font-black uppercase italic tracking-tighter mb-2 group-hover:text-blue-400 transition-colors truncate">{project.name}</h3>
                      <p className="text-xs text-white/30 font-medium leading-relaxed line-clamp-3 mb-4">{project.description}</p>
                    </div>
                    
                    <div className="flex items-center justify-between mt-4 pt-6 border-t border-white/5">
                      <div className="flex items-center gap-4">
                        <div className="flex flex-col">
                          <span className="text-[8px] font-black text-white/10 uppercase tracking-widest mb-1">Nodes</span>
                          <span className="text-base font-black italic">{project.nodeCount || 18}</span>
                        </div>
                        <div className="w-[1px] h-8 bg-white/5"></div>
                        <div className="flex flex-col">
                          <span className="text-[8px] font-black text-white/10 uppercase tracking-widest mb-1">Sources</span>
                          <span className="text-base font-black italic text-blue-400/80">{project.dataSources.length}</span>
                        </div>
                      </div>
                      <div className="w-10 h-10 rounded-xl bg-white/[0.03] flex items-center justify-center group-hover:bg-blue-600 group-hover:scale-110 transition-all">
                        <ChevronRight className="w-5 h-5 text-white/20 group-hover:text-white" />
                      </div>
                    </div>
                  </div>
                ))}

                {/* PRIMARY CTA: START NEW DEPLOYMENT */}
                <button 
                  onClick={handleNewProject}
                  className="group relative p-6 min-h-[16rem] lg:min-h-[18rem] border-2 border-dashed border-white/5 rounded-3xl hover:border-blue-500/40 hover:bg-blue-600/[0.03] transition-all flex flex-col items-center justify-center text-center overflow-hidden shadow-2xl"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-600/0 to-blue-600/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
                  <div className="w-16 h-16 bg-white/[0.02] border border-white/5 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform group-hover:shadow-[0_0_40px_rgba(37,99,235,0.15)] group-hover:border-blue-500/30">
                    <Plus className="w-8 h-8 text-white/10 group-hover:text-blue-500 transition-colors" />
                  </div>
                  <span className="text-xl font-bold tracking-tight text-white/20 group-hover:text-white transition-colors">New Project</span>
                  <p className="text-[8px] text-white/10 uppercase tracking-[0.3em] mt-6 group-hover:text-blue-500/60 transition-colors font-black">SEMANTICORE v1.0</p>
                </button>

                {/* Simulated Data Node */}
                <div className="p-6 min-h-[16rem] lg:min-h-[18rem] bg-gradient-to-b from-[#0d0d0d] to-transparent border border-white/5 border-dashed rounded-3xl flex flex-col justify-center items-center text-center grayscale opacity-10 hover:grayscale-0 hover:opacity-40 transition-all group">
                   <HardDrive className="w-12 h-12 text-white/10 mb-6 group-hover:text-emerald-500/40 transition-colors" />
                   <h3 className="text-lg font-black uppercase italic tracking-tight text-white/10">Secure Archive</h3>
                   <p className="text-[8px] text-white/5 uppercase tracking-[0.2em] mt-3 font-bold">Node: 0xFD2A</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
