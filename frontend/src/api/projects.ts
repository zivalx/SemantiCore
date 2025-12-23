/**
 * Projects API client.
 */

import { apiClient } from './client';
import type { Project } from '../types';

export const createProject = async (data: {
  name: string;
  domain: string;
  description: string;
}): Promise<Project> => {
  const response = await apiClient.post('/projects/', data);
  return response.data;
};

export const listProjects = async (): Promise<Project[]> => {
  const response = await apiClient.get('/projects/');
  return response.data;
};

export const getProject = async (projectId: string): Promise<Project> => {
  const response = await apiClient.get(`/projects/${projectId}`);
  return response.data;
};

export const updateProject = async (
  projectId: string,
  data: Partial<{ name: string; domain: string; description: string }>
): Promise<Project> => {
  const response = await apiClient.put(`/projects/${projectId}`, data);
  return response.data;
};

export const deleteProject = async (projectId: string): Promise<void> => {
  await apiClient.delete(`/projects/${projectId}`);
};
