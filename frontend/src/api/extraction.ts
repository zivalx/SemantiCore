/**
 * Extraction API client (semantic primitive extraction).
 */

import { apiClient } from './client';
import type { SemanticPrimitive } from '../types';
import type { JobStatus } from './jobs';

export const extractPrimitives = async (
  projectId: string
): Promise<JobStatus> => {
  const response = await apiClient.post('/extraction/extract', null, {
    params: { project_id: projectId },
  });
  return response.data;
};

export const getPrimitives = async (
  projectId: string
): Promise<SemanticPrimitive[]> => {
  const response = await apiClient.get(`/extraction/primitives/${projectId}`);
  return response.data;
};
