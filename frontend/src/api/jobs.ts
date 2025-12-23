/**
 * Jobs API client (async job polling).
 */

import { apiClient } from './client';

export interface JobStatus {
  id: string;
  project_id: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  result?: any;
  error?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export const getJobStatus = async (jobId: string): Promise<JobStatus> => {
  const response = await apiClient.get(`/jobs/${jobId}`);
  return response.data;
};

export const listProjectJobs = async (
  projectId: string,
  params?: {
    job_type?: string;
    job_status?: string;
    limit?: number;
    offset?: number;
  }
): Promise<JobStatus[]> => {
  const response = await apiClient.get(`/jobs/project/${projectId}`, { params });
  return response.data;
};
