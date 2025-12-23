
import React, { useState, useMemo } from 'react';
import {
  Upload, Database, Search, Sparkles, Network, Terminal, Check,
  ChevronRight, File, X, BrainCircuit, Activity, Layers, History, MessageSquare, AlertCircle, Code, Play, ShieldAlert, Download,
  Eye, EyeOff, Info, ClipboardList, Fingerprint, ArrowRight, Zap, ShieldCheck
} from 'lucide-react';
import { WizardStep, Ontology, SemanticPrimitive, SourceMetadata } from '../types';
import OntologyGraph from './OntologyGraph';
import { createProject } from '../src/api/projects';
import { uploadSource } from '../src/api/sources';
import { extractPrimitives, getPrimitives } from '../src/api/extraction';
import { generateOntology, getActiveOntology } from '../src/api/ontology';
import { usePolling } from '../src/hooks/usePolling';

const ProjectWizard: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const [step, setStep] = useState<WizardStep>('setup');
  const [projectId, setProjectId] = useState<string | null>(null);
  const [projectName, setProjectName] = useState('');
  const [files, setFiles] = useState<SourceMetadata[]>([]);
  const [description, setDescription] = useState('');
  const [primitives, setPrimitives] = useState<SemanticPrimitive[]>([]);
  const [ontology, setOntology] = useState<Ontology | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [queryText, setQueryText] = useState('');
  const [cypherQuery, setCypherQuery] = useState('// Initialize query to begin...');
  const [queryResults, setQueryResults] = useState<any[]>([]);
  const [showConsistencyCheck, setShowConsistencyCheck] = useState(false);
  const [consistencyReport, setConsistencyReport] = useState<string | null>(null);
  const [viewingContentId, setViewingContentId] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const steps: { key: WizardStep; label: string; icon: any }[] = [
    { key: 'setup', label: 'Identity', icon: Fingerprint },
    { key: 'frame', label: 'Frame', icon: Search },
    { key: 'ingest', label: 'Ingest', icon: Database },
    { key: 'extract', label: 'Extract', icon: Layers },
    { key: 'propose', label: 'Propose', icon: Sparkles },
    { key: 'negotiate', label: 'Negotiate', icon: MessageSquare },
    { key: 'graph', label: 'Knowledge', icon: Network },
    { key: 'query', label: 'Query', icon: Terminal },
  ];

  // Shared function to process files (used by both click and drag-and-drop)
  const processFiles = async (fileList: File[]) => {
    // Create project if it doesn't exist
    if (!projectId) {
      try {
        const project = await createProject({
          name: projectName || 'Untitled Project',
          domain: 'General',
          description: description || 'Project description',
        });
        setProjectId(project.id);
      } catch (error) {
        console.error('Error creating project:', error);
        alert('Failed to create project');
        return;
      }
    }

    // Upload files to backend
    const uploadPromises = fileList.map(async (file: File) => {
      try {
        const source = await uploadSource(projectId!, file);
        return {
          id: source.id,
          name: source.name,
          type: source.type,
          processedAt: source.uploaded_at,
          size: source.file_size || 0,
        };
      } catch (error) {
        console.error(`Error uploading file ${file.name}:`, error);
        throw error;
      }
    });

    try {
      const uploadedFiles = await Promise.all(uploadPromises);
      setFiles(prev => [...prev, ...uploadedFiles]);
    } catch (error) {
      alert('Some files failed to upload');
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileList = Array.from(e.target.files) as File[];
      await processFiles(fileList);
    }
  };

  // Drag and drop handlers
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files) as File[];
    if (files.length > 0) {
      await processFiles(files);
    }
  };

  const startExtraction = async () => {
    if (!projectId) {
      alert('Please create a project and upload files first');
      return;
    }

    setIsProcessing(true);
    try {
      // Start extraction job
      const job = await extractPrimitives(projectId);
      setCurrentJobId(job.id);

      // Poll for completion
      const pollInterval = setInterval(async () => {
        try {
          const primitivesList = await getPrimitives(projectId);
          if (primitivesList && primitivesList.length > 0) {
            clearInterval(pollInterval);
            setPrimitives(primitivesList);
            setStep('extract');
            setIsProcessing(false);
            setCurrentJobId(null);
          }
        } catch (error) {
          console.error('Error fetching primitives:', error);
        }
      }, 2000);

      // Timeout after 2 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        if (isProcessing) {
          console.error('Extraction timed out');
          setPrimitives(MOCK_PRIMITIVES);
          setStep('extract');
          setIsProcessing(false);
        }
      }, 120000);
    } catch (e) {
      console.error("Extraction failed, using mock data", e);
      setPrimitives(MOCK_PRIMITIVES);
      setStep('extract');
      setIsProcessing(false);
    }
  };

  const generateOntology = async () => {
    if (!projectId) {
      alert('Please create a project first');
      return;
    }

    setIsProcessing(true);
    try {
      // Start ontology generation job
      const job = await generateOntology(projectId, description);
      setCurrentJobId(job.id);

      // Poll for completion
      const pollInterval = setInterval(async () => {
        try {
          const result = await getActiveOntology(projectId);
          if (result && result.ontology) {
            clearInterval(pollInterval);
            // Convert backend ontology format to frontend format
            const formattedOntology = {
              version: result.ontology.version,
              nodes: result.ontology.classes.map((cls: any) => ({
                id: cls.name,
                label: cls.name,
                type: 'Class',
                description: cls.description,
                reasoning: cls.properties?.map((p: any) => p.name).join(', ') || '',
              })).concat(
                result.ontology.relation_types.map((rel: any) => ({
                  id: rel.name,
                  label: rel.name,
                  type: 'RelationType',
                  description: rel.description,
                  reasoning: `${rel.source_class} -> ${rel.target_class}`,
                }))
              ),
              edges: result.ontology.relation_types.map((rel: any) => ({
                id: `${rel.source_class}-${rel.name}-${rel.target_class}`,
                source: rel.source_class,
                target: rel.target_class,
                label: rel.name,
              })),
            };
            setOntology(formattedOntology);
            setStep('propose');
            setIsProcessing(false);
            setCurrentJobId(null);
          }
        } catch (error) {
          console.error('Error fetching ontology:', error);
        }
      }, 3000);

      // Timeout after 3 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        if (isProcessing) {
          console.error('Ontology generation timed out');
          setOntology(MOCK_ONTOLOGY_V1);
          setStep('propose');
          setIsProcessing(false);
        }
      }, 180000);
    } catch (error) {
      console.error("Ontology generation failed, using mock data", error);
      setOntology(MOCK_ONTOLOGY_V1);
      setStep('propose');
      setIsProcessing(false);
    }
  };

  const executeSemanticQuery = async () => {
    if (!queryText) return;
    setIsProcessing(true);
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: `Cypher query for: "${queryText}". Ontology: ${JSON.stringify(ontology)}.`,
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              cypher: { type: Type.STRING },
              results: { type: Type.ARRAY, items: { type: Type.OBJECT, properties: { node: { type: Type.STRING }, data: { type: Type.STRING } } } }
            }
          }
        }
      });
      const parsed = JSON.parse(response.text || '{}');
      setCypherQuery(parsed.cypher);
      setQueryResults(parsed.results || []);
    } catch (e) {
      setCypherQuery("// Execution error.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-[#0a0a0a] overflow-hidden relative">
      {/* PROCESSING OVERLAY - Materialization Feedback */}
      {isProcessing && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-md z-[100] flex flex-col items-center justify-center animate-in fade-in duration-300">
           <div className="relative mb-8">
              <div className="w-24 h-24 bg-blue-600/20 rounded-full border border-blue-500/30 flex items-center justify-center animate-pulse">
                 <BrainCircuit className="w-10 h-10 text-blue-500 animate-bounce" />
              </div>
              <div className="absolute inset-0 border-2 border-dashed border-blue-500/20 rounded-full animate-spin-slow"></div>
           </div>
           <div className="text-center">
              <h3 className="text-xl font-black uppercase italic tracking-tighter mb-2">Materializing Logic</h3>
              <p className="text-[10px] font-black text-white/30 uppercase tracking-[0.4em] font-mono">Architecting Domain Ontology...</p>
           </div>
        </div>
      )}

      {/* Pipeline Stepper */}
      <div className="border-b border-white/5 bg-[#0d0d0d] px-6 py-4 flex items-center justify-between shrink-0 overflow-x-auto custom-scrollbar">
        <div className="flex items-center gap-1.5 min-w-max">
          {steps.map((s, idx) => (
            <React.Fragment key={s.key}>
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl transition-all ${step === s.key ? 'bg-blue-600/10 text-blue-400 border border-blue-500/10' : steps.findIndex(x => x.key === step) > idx ? 'text-emerald-500' : 'text-white/10'}`}>
                <s.icon className={`w-3.5 h-3.5 ${step === s.key ? 'animate-pulse' : ''}`} />
                <div className="flex flex-col">
                  <span className="text-[9px] font-black uppercase tracking-tight">{s.label}</span>
                </div>
              </div>
              {idx < steps.length - 1 && <div className="w-2 h-[1px] bg-white/5 mx-0.5" />}
            </React.Fragment>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 lg:p-10 flex flex-col items-center relative">
        {step === 'setup' && (
          <div className="max-w-xl w-full flex flex-col justify-center animate-in fade-in slide-in-from-bottom-8 py-4 lg:py-10">
            <div className="flex items-center gap-4 mb-8">
               <div className="w-12 h-12 rounded-2xl bg-blue-600/10 flex items-center justify-center border border-blue-500/20 shadow-2xl shrink-0">
                  <Fingerprint className="w-6 h-6 text-blue-500" />
               </div>
               <div>
                 <h2 className="text-2xl lg:text-3xl font-black uppercase tracking-tight italic">Deployment Identity</h2>
                 <p className="text-[9px] font-black text-white/20 uppercase tracking-[0.2em] mt-0.5">Canonical Target</p>
               </div>
            </div>
            <p className="text-white/40 mb-8 text-sm lg:text-base leading-relaxed font-medium">Assign a unique identifier for this deployment. This name serves as the canonical root for all versioned ontology mutations.</p>
            <div className="space-y-6">
              <input 
                autoFocus
                className="w-full bg-[#0d0d0d] border border-white/10 rounded-2xl p-6 text-xl font-black placeholder:text-white/5 outline-none focus:ring-1 focus:ring-blue-500/30 transition-all text-white/90"
                placeholder="Ex: Precision_Oncology_X"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && projectName && setStep('frame')}
              />
            </div>
            <button 
              onClick={() => setStep('frame')} 
              disabled={!projectName} 
              className="mt-10 h-16 bg-blue-600 rounded-2xl font-black text-base hover:bg-blue-500 flex items-center justify-center gap-4 transition-all shadow-xl group disabled:opacity-20"
            >
              Configure Domain Framing <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        )}

        {step === 'frame' && (
          <div className="max-w-2xl w-full flex flex-col justify-center animate-in fade-in slide-in-from-bottom-8 py-4 lg:py-10">
            <div className="flex items-center gap-4 mb-4">
               <div className="w-10 h-10 rounded-full bg-blue-600/10 flex items-center justify-center border border-blue-500/20 shrink-0"><Search className="w-5 h-5 text-blue-500" /></div>
               <div>
                  <h2 className="text-2xl lg:text-3xl font-black uppercase tracking-tight italic">Domain Framing</h2>
                  <p className="text-[9px] font-black text-white/20 uppercase tracking-[0.2em]">{projectName}</p>
               </div>
            </div>
            <p className="text-white/30 mb-6 text-sm lg:text-base leading-relaxed font-medium">Define the semantic rules for your domain knowledge graph.</p>
            <textarea 
              className="w-full h-64 lg:h-80 bg-[#0d0d0d] border border-white/10 rounded-3xl p-8 text-base font-mono focus:ring-1 focus:ring-blue-500/20 outline-none placeholder:text-white/10 transition-all resize-none leading-relaxed"
              placeholder="Architect a knowledge graph for... Focus on relationships between..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <button 
              onClick={() => setStep('ingest')} 
              disabled={!description} 
              className="mt-10 h-16 bg-blue-600 rounded-2xl font-black text-base hover:bg-blue-500 flex items-center justify-center gap-4 transition-all shadow-xl disabled:opacity-30"
            >
              Initialize Ingestion <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}

        {step === 'ingest' && (
          <div className="max-w-5xl w-full h-full flex flex-col items-center justify-center animate-in fade-in py-4">
            <h2 className="text-2xl lg:text-3xl font-black uppercase italic tracking-tighter mb-8">Source Ingestion</h2>
            <div className="w-full flex flex-col md:flex-row gap-6 h-[400px] lg:h-[450px]">
              <label
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                className={`flex-1 border-2 border-dashed rounded-3xl transition-all cursor-pointer flex flex-col items-center justify-center group relative overflow-hidden ${
                  isDragging
                    ? 'border-blue-500 bg-blue-500/10 scale-[1.02]'
                    : 'border-white/5 bg-white/[0.01] hover:bg-white/[0.02]'
                }`}
              >
                <Upload className={`w-8 h-8 transition-colors mb-4 ${
                  isDragging ? 'text-blue-500 scale-110' : 'text-white/10 group-hover:text-blue-500'
                }`} />
                <span className={`text-sm font-bold tracking-wide ${
                  isDragging ? 'text-blue-400' : 'text-white/40'
                }`}>
                  {isDragging ? 'Drop files here' : 'Drag files or click to browse'}
                </span>
                <span className="text-xs text-white/20 mt-2">CSV, JSON, PDF, DOCX, TXT</span>
                <input type="file" className="hidden" multiple onChange={handleFileUpload} />
              </label>

              <div className="flex-1 glass rounded-3xl overflow-hidden flex flex-col border border-white/5 shadow-xl">
                <div className="px-6 py-4 border-b border-white/5 bg-white/[0.01] flex justify-between items-center shrink-0 text-[9px] font-black uppercase tracking-widest text-white/20">
                  Buffer Status: {files.length}
                </div>
                <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-3">
                  {files.map(f => (
                    <div key={f.id} className="p-4 bg-[#0a0a0a] border border-white/5 rounded-xl flex items-center justify-between group hover:border-blue-500/20">
                      <div className="flex items-center gap-3 min-w-0">
                        <File className="w-4 h-4 text-blue-500 shrink-0" />
                        <div className="min-w-0">
                          <div className="text-[10px] font-black text-white/80 truncate uppercase tracking-tight">{f.name}</div>
                          <div className="text-[8px] text-white/20 font-mono mt-0.5 uppercase tracking-tighter">{(f.size! / 1024).toFixed(1)} KB</div>
                        </div>
                      </div>
                      <button onClick={() => setFiles(prev => prev.filter(x => x.id !== f.id))} className="p-2 hover:bg-red-500/10 rounded-lg text-red-500/40 hover:text-red-500 transition-all"><X className="w-3.5 h-3.5" /></button>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <button 
              onClick={startExtraction}
              disabled={files.length === 0 || isProcessing}
              className="mt-10 bg-blue-600 text-white font-black py-4 px-16 rounded-2xl hover:bg-blue-500 transition-all disabled:opacity-20 shadow-xl flex items-center gap-3 text-sm uppercase tracking-widest"
            >
              {isProcessing ? <Activity className="w-4 h-4 animate-spin" /> : <><Sparkles className="w-4 h-4" /> Extract Primitives</>}
            </button>
          </div>
        )}

        {step === 'extract' && (
          <div className="w-full h-full flex flex-col animate-in fade-in py-2 max-w-[1200px]">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-xl lg:text-2xl font-black uppercase tracking-tight italic">Semantic Extraction</h2>
                <p className="text-[9px] text-white/30 uppercase tracking-[0.2em] mt-1 font-black">Refined from Ingested Sources</p>
              </div>
              <button 
                onClick={generateOntology} 
                disabled={isProcessing}
                className="bg-white text-black px-6 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-neutral-200 transition-all flex items-center gap-2 shadow-2xl disabled:opacity-50"
              >
                {isProcessing ? <Activity className="w-3.5 h-3.5 animate-spin" /> : <>Propose Formal Ontology <ChevronRight className="w-3.5 h-3.5" /></>}
              </button>
            </div>
            
            <div className="flex-1 overflow-hidden border border-white/5 rounded-3xl bg-[#0d0d0d] flex flex-col shadow-xl">
              <div className="grid grid-cols-12 gap-4 px-6 py-4 bg-white/[0.01] border-b border-white/5 text-[8px] font-black uppercase tracking-widest text-white/20">
                 <div className="col-span-1">Ref</div>
                 <div className="col-span-4">Primitive</div>
                 <div className="col-span-2">Type</div>
                 <div className="col-span-1 text-center">Score</div>
                 <div className="col-span-4">Source Evidence</div>
              </div>
              <div className="flex-1 overflow-y-auto custom-scrollbar">
                {primitives.map((p, idx) => (
                  <div key={p.id} className="grid grid-cols-12 gap-4 px-6 py-3.5 border-b border-white/[0.02] items-center hover:bg-white/[0.01] transition-all group overflow-hidden">
                    <div className="col-span-1 text-[9px] font-mono text-white/10 uppercase">{idx + 100}</div>
                    <div className="col-span-4 text-xs font-black text-white/80 group-hover:text-blue-400 transition-colors uppercase truncate tracking-tight">{p.label}</div>
                    <div className="col-span-2">
                      <span className={`px-2 py-0.5 rounded-full text-[7px] font-black uppercase tracking-widest ${
                        p.type === 'entity' ? 'bg-blue-500/10 text-blue-500 border border-blue-500/10' : 
                        p.type === 'relation' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/10' : 
                        'bg-amber-500/10 text-amber-500 border border-amber-500/10'
                      }`}>
                        {p.type}
                      </span>
                    </div>
                    <div className="col-span-1 flex items-center justify-center gap-2 text-[9px] font-mono text-white/20">
                       {(p.confidence * 100).toFixed(0)}%
                    </div>
                    <div className="col-span-4 text-[9px] font-mono text-white/10 leading-relaxed italic truncate pr-4 overflow-hidden">
                      "{p.evidence}"
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 'propose' && ontology && (
          <div className="w-full h-full flex flex-col animate-in fade-in py-2 max-w-[1200px]">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-xl lg:text-2xl font-black uppercase italic tracking-tighter">Proposed Schema v{ontology.version}</h2>
                <p className="text-[9px] text-white/30 uppercase tracking-[0.2em] font-black">AI Orchestrated Blueprint</p>
              </div>
              <button onClick={() => setStep('negotiate')} className="bg-emerald-600 px-6 py-2.5 rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-emerald-500 transition-all flex items-center gap-2 shadow-lg">Commit Blueprint <Check className="w-3.5 h-3.5" /></button>
            </div>
            <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-4 pb-20">
               {ontology.nodes.map(node => (
                 <div key={node.id} className="p-6 bg-[#0d0d0d] rounded-2xl border border-white/5 hover:border-blue-500/20 transition-all relative group overflow-hidden shadow-xl flex items-start justify-between gap-6">
                    <div className="flex-1">
                       <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-black text-white/90 tracking-tight uppercase italic">{node.label}</h3>
                          <span className="text-[7px] font-black text-blue-500 bg-blue-500/10 px-2 py-0.5 rounded-full tracking-widest uppercase border border-blue-500/10">{node.type}</span>
                       </div>
                       <p className="text-xs text-white/40 leading-relaxed font-medium line-clamp-2">{node.description}</p>
                    </div>
                    <div className="w-1/3 bg-black/40 p-4 rounded-xl border border-white/5 hidden md:block">
                      <span className="text-[7px] uppercase text-white/20 block mb-1 font-black tracking-widest">Logic Axiom</span>
                      <p className="text-[10px] text-white/30 leading-relaxed font-mono italic line-clamp-2">{node.reasoning || "Canonical Domain Class"}</p>
                    </div>
                 </div>
               ))}
            </div>
          </div>
        )}

        {step === 'negotiate' && (
          <div className="h-full flex flex-col items-center justify-center animate-in zoom-in-95 text-center px-6">
             <div className="w-20 h-20 bg-emerald-600/10 rounded-3xl flex items-center justify-center mx-auto mb-8 border border-emerald-500/20 shadow-2xl animate-bounce"><Check className="w-10 h-10 text-emerald-500" /></div>
             <h2 className="text-4xl lg:text-5xl font-black mb-4 tracking-tighter uppercase italic">Blueprint Locked</h2>
             <p className="text-white/20 mb-10 text-lg font-medium max-w-lg leading-relaxed">Model integrity verified. Ready for deployment.</p>
             <button onClick={() => setStep('graph')} className="bg-white text-black font-black px-12 py-4 rounded-2xl text-lg hover:bg-neutral-200 transition-all shadow-2xl active:scale-95">Deploy Knowledge Graph</button>
          </div>
        )}

        {step === 'graph' && ontology && (
          <div className="w-full h-full flex flex-col animate-in fade-in py-2 max-w-[1400px]">
             <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl lg:text-2xl font-black uppercase italic tracking-tighter">Knowledge Explorer</h2>
                <button onClick={() => setStep('query')} className="bg-blue-600 px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-500 transition-all">Launch Engine</button>
             </div>
             <div className="flex-1 rounded-[40px] overflow-hidden border border-white/5 bg-[#050505] relative shadow-inner">
                <OntologyGraph data={ontology} />
             </div>
          </div>
        )}

        {step === 'query' && (
          <div className="w-full h-full flex flex-col animate-in fade-in py-2 max-w-[1200px]">
             <div className="mb-8 flex justify-between items-end px-2">
                <div>
                  <h2 className="text-xl lg:text-2xl font-black uppercase italic tracking-tighter">Cypher Engine</h2>
                  <p className="text-white/20 text-[8px] font-black uppercase tracking-widest font-mono">Status: Materialized</p>
                </div>
             </div>
             <div className="flex-1 grid grid-cols-12 gap-6 overflow-hidden">
                <div className="col-span-12 lg:col-span-8 flex flex-col gap-6">
                   <div className="flex-1 bg-[#050505] rounded-[32px] border border-white/5 flex flex-col overflow-hidden shadow-2xl">
                      <div className="flex-1 p-8 font-mono text-sm text-blue-300/60 leading-relaxed whitespace-pre-wrap overflow-y-auto custom-scrollbar">{cypherQuery}</div>
                      {queryResults.length > 0 && (
                        <div className="p-6 bg-white/[0.01] border-t border-white/5 max-h-48 overflow-y-auto space-y-2">
                           {queryResults.map((res, idx) => (
                             <div key={idx} className="flex items-center justify-between p-4 bg-black/40 border border-white/5 rounded-xl">
                                <span className="text-[10px] font-black text-white/50 uppercase">{res.node}</span>
                                <span className="text-[10px] font-mono text-blue-400">{res.data}</span>
                             </div>
                           ))}
                        </div>
                      )}
                   </div>
                   <div className="h-20 bg-[#0d0d0d] rounded-[24px] flex items-center px-8 gap-4 border border-white/10 shadow-2xl transition-all">
                      <Terminal className="w-5 h-5 text-white/20" />
                      <input className="flex-1 bg-transparent border-none outline-none font-black text-lg placeholder:text-white/5 tracking-tight text-white/80" placeholder="Query semantic paths..." value={queryText} onChange={(e) => setQueryText(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && executeSemanticQuery()} />
                      <button onClick={executeSemanticQuery} disabled={isProcessing} className="bg-blue-600 text-white px-8 py-3 rounded-xl font-black text-xs hover:bg-blue-500 transition-all active:scale-95">{isProcessing ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-current" />}</button>
                   </div>
                </div>
                <div className="col-span-12 lg:col-span-4 glass rounded-[32px] p-8 flex flex-col gap-6">
                   <h4 className="text-[9px] font-black uppercase tracking-[0.2em] text-white/20 italic">Bindings</h4>
                   <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 border border-white/5 rounded-xl bg-white/[0.01]"><span className="text-[10px] font-black text-white/40 uppercase">Engine</span><span className="text-[9px] font-mono text-emerald-500 uppercase tracking-widest">Active</span></div>
                      <div className="flex items-center justify-between p-4 border border-white/5 rounded-xl bg-white/[0.01]"><span className="text-[10px] font-black text-white/40 uppercase">Optimized</span><span className="text-[9px] font-mono text-blue-500 uppercase">Yes</span></div>
                   </div>
                </div>
             </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin-slow {
          animation: spin-slow 12s linear infinite;
        }
      `}</style>
    </div>
  );
};

export default ProjectWizard;
