/**
 * Ontology API client.
 */

import { apiClient } from './client';
import type { Ontology } from '../types';
import type { JobStatus } from './jobs';

export const generateOntology = async (
  projectId: string,
  domainDescription: string
): Promise<JobStatus> => {
  const response = await apiClient.post('/ontology/generate', {
    project_id: projectId,
    domain_description: domainDescription,
  });
  return response.data;
};

export const listOntologyVersions = async (projectId: string): Promise<any[]> => {
  const response = await apiClient.get(`/ontology/${projectId}/versions`);
  return response.data;
};

export const getActiveOntology = async (projectId: string): Promise<any> => {
  const response = await apiClient.get(`/ontology/${projectId}/active`);
  return response.data;
};

export const acceptOntologyVersion = async (versionId: string): Promise<any> => {
  const response = await apiClient.post(`/ontology/${versionId}/accept`);
  return response.data;
};
