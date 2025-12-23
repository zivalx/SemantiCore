/**
 * Application constants for SemantiCore.
 */

// File upload configuration
export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
export const SUPPORTED_FILE_TYPES = [
  'text/csv',
  'application/json',
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain'
];

export const FILE_TYPE_EXTENSIONS = {
  'csv': 'text/csv',
  'json': 'application/json',
  'pdf': 'application/pdf',
  'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'txt': 'text/plain'
};
