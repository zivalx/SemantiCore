
export interface SourceMetadata {
  id: string;
  name: string;
  type: 'json' | 'csv' | 'text' | 'pdf' | 'docx';
  processedAt: string;
  content?: string; // Real content for LLM processing
  size?: number;
}

export interface SemanticPrimitive {
  id: string;
  label: string;
  type: 'entity' | 'attribute' | 'relation';
  evidence: string;
  confidence: number;
  sourceId: string;
}

export interface Project {
  id: string;
  name: string;
  domain: string;
  description: string;
  status: 'draft' | 'building' | 'complete';
  lastModified: string;
  dataSources: SourceMetadata[];
  version: number;
  nodeCount?: number;
  relationCount?: number;
}

export interface OntologyNode {
  id: string;
  label: string;
  type: 'Class' | 'RelationType' | 'Property';
  description?: string;
  reasoning?: string;
  alternatives?: string[];
  confidence?: number;
}

export interface OntologyEdge {
  id: string;
  source: string;
  target: string;
  label: string;
}

export interface Ontology {
  version: string;
  nodes: OntologyNode[];
  edges: OntologyEdge[];
  openQuestions?: string[];
}

export type WizardStep = 'setup' | 'frame' | 'ingest' | 'extract' | 'propose' | 'negotiate' | 'graph' | 'query';
