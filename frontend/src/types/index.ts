// Core TypeScript interfaces for CiteSight application

export interface AnalysisOptions {
  citationStyle: 'auto' | 'apa' | 'mla' | 'chicago';
  checkUrls: boolean;
  checkDoi: boolean;
  checkWayback: boolean;
  checkPlagiarism: boolean;
  checkInText: boolean;
  processingMode: 'server' | 'local';
}

export interface Pattern {
  text: string;
  severity: 'high' | 'medium' | 'low';
}

export interface Issue {
  type: 'error' | 'warning';
  title: string;
  details: string;
}

export interface WordFrequency {
  word: string;
  count: number;
  size: number;
}

export interface PhraseCount {
  phrase: string;
  count: number;
}

export interface DocumentComparison {
  name: string;
  wordCount: number;
  readability: number;
  references: number;
  issues: number;
}

export interface SuspiciousPatterns {
  selfPlagiarism: Pattern[];
  citationAnomalies: Pattern[];
  styleInconsistencies: Pattern[];
}

export interface ReferenceResults {
  total: number;
  brokenUrls: number;
  unresolvedDois: number;
  missingInText: number;
  orphanedInText: number;
  issues: Issue[];
}

export interface DocumentAnalysis {
  wordCount: number;
  sentenceCount: number;
  avgWordsPerSentence: number;
  paragraphCount: number;
  fleschScore: number;
  fleschKincaidGrade: number;
}

export interface WritingQuality {
  passiveVoicePercentage: number;
  sentenceVariety: number;
  transitionWords: number;
  hedgingLanguage: number;
  academicTone: number;
}

export interface WordAnalysis {
  mostFrequent: WordFrequency[];
  uniqueWords: string[];
  uniquePhrases: PhraseCount[];
}

export interface AnalysisResults {
  references: ReferenceResults;
  suspiciousPatterns: SuspiciousPatterns;
  documentAnalysis: DocumentAnalysis;
  writingQuality: WritingQuality;
  wordAnalysis: WordAnalysis;
  comparison?: DocumentComparison[];
}

export interface FileUpload {
  file: File;
  id: string;
  name: string;
  size: number;
  type: string;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
}

export interface ProcessingProgress {
  stage: 'upload' | 'extraction' | 'analysis' | 'verification' | 'complete';
  progress: number;
  message: string;
  currentFile?: string;
}

export interface AppState {
  // File management
  uploadedFiles: FileUpload[];
  
  // Processing state
  isProcessing: boolean;
  processingProgress: ProcessingProgress;
  
  // Analysis options
  analysisOptions: AnalysisOptions;
  
  // Results
  analysisResults: AnalysisResults | null;
  
  // UI state
  activeTab: string;
  errors: string[];
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  message?: string;
}

export interface AnalysisRequest {
  files: File[];
  options: AnalysisOptions;
}

export interface AnalysisResponse extends AnalysisResults {
  processingTime: number;
  fileCount: number;
}

// Error types
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ValidationError {
  field: string;
  message: string;
}