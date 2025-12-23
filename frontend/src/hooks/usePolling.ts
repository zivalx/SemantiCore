/**
 * React hook for polling async job status.
 *
 * Automatically polls a job until it completes or fails.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { getJobStatus, type JobStatus } from '../api/jobs';

export interface UsePollingOptions {
  interval?: number; // Polling interval in milliseconds (default: 2000)
  enabled?: boolean; // Whether polling is enabled (default: true)
  onComplete?: (job: JobStatus) => void; // Callback when job completes
  onError?: (error: any) => void; // Callback on error
}

export const usePolling = (jobId: string | null, options: UsePollingOptions = {}) => {
  const {
    interval = 2000,
    enabled = true,
    onComplete,
    onError,
  } = options;

  const [job, setJob] = useState<JobStatus | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<any>(null);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const onCompleteRef = useRef(onComplete);
  const onErrorRef = useRef(onError);

  // Update refs when callbacks change
  useEffect(() => {
    onCompleteRef.current = onComplete;
    onErrorRef.current = onError;
  }, [onComplete, onError]);

  const poll = useCallback(async () => {
    if (!jobId) return;

    try {
      const jobStatus = await getJobStatus(jobId);
      setJob(jobStatus);

      // Stop polling if job is completed or failed
      if (jobStatus.status === 'completed' || jobStatus.status === 'failed') {
        setIsPolling(false);

        if (jobStatus.status === 'completed' && onCompleteRef.current) {
          onCompleteRef.current(jobStatus);
        } else if (jobStatus.status === 'failed' && onErrorRef.current) {
          onErrorRef.current(new Error(jobStatus.error || 'Job failed'));
        }
      }
    } catch (err) {
      console.error('Error polling job:', err);
      setError(err);
      setIsPolling(false);

      if (onErrorRef.current) {
        onErrorRef.current(err);
      }
    }
  }, [jobId]);

  // Start polling effect
  useEffect(() => {
    if (jobId && isPolling && enabled) {
      // Poll immediately
      poll();

      // Set up interval
      intervalRef.current = setInterval(poll, interval);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [jobId, isPolling, enabled, interval, poll]);

  const startPolling = useCallback(() => {
    setIsPolling(true);
    setError(null);
  }, []);

  const stopPolling = useCallback(() => {
    setIsPolling(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  }, []);

  return {
    job,
    isPolling,
    error,
    startPolling,
    stopPolling,
  };
};
