/**
 * Sources API client (file upload).
 */

import { apiClient } from './client';
import type { SourceMetadata } from '../types';

export const uploadSource = async (
  projectId: string,
  file: File
): Promise<SourceMetadata> => {
  const formData = new FormData();
  formData.append('project_id', projectId);
  formData.append('file', file);

  const response = await apiClient.post('/sources/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getSource = async (sourceId: string): Promise<SourceMetadata> => {
  const response = await apiClient.get(`/sources/${sourceId}`);
  return response.data;
};

export const listProjectSources = async (
  projectId: string
): Promise<SourceMetadata[]> => {
  const response = await apiClient.get(`/sources/project/${projectId}`);
  return response.data;
};

export const deleteSource = async (sourceId: string): Promise<void> => {
  await apiClient.delete(`/sources/${sourceId}`);
};
