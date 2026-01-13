/**
 * useEvaluation Hook
 *
 * Custom hook for interacting with the Partner Evaluation Framework API.
 * Manages evaluation sessions, strategy, and results.
 */

import { useState, useCallback } from 'react';

const API_BASE = '/api/evaluation';

export function useEvaluation() {
  const [sessionId, setSessionId] = useState(null);
  const [strategy, setStrategy] = useState(null);
  const [strategySummary, setStrategySummary] = useState('');
  const [isStrategyConfirmed, setIsStrategyConfirmed] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [phase, setPhase] = useState('init'); // init, planning, evaluating, complete

  /**
   * Create a new evaluation session
   */
  const createSession = useCallback(async (startupProfile, candidates) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          startup_profile: startupProfile,
          candidates,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create session: ${response.statusText}`);
      }

      const data = await response.json();
      setSessionId(data.session_id);
      setPhase('planning');
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Propose an evaluation strategy
   */
  const proposeStrategy = useCallback(async (partnerRequirements = {}) => {
    if (!sessionId) {
      throw new Error('No session. Call createSession first.');
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/strategy/propose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          partner_requirements: partnerRequirements,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to propose strategy: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setStrategy(data.strategy);
        setStrategySummary(data.summary || '');
      }
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  /**
   * Modify the current strategy
   */
  const modifyStrategy = useCallback(async (modification) => {
    if (!sessionId) {
      throw new Error('No session.');
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/strategy/modify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          modification,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to modify strategy: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setStrategy(data.strategy);
        setStrategySummary(data.summary || strategySummary);
      }
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, strategySummary]);

  /**
   * Confirm the strategy and prepare for evaluation
   */
  const confirmStrategy = useCallback(async () => {
    if (!sessionId) {
      throw new Error('No session.');
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/strategy/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error(`Failed to confirm strategy: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setIsStrategyConfirmed(true);
        setPhase('evaluating');
      }
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  /**
   * Run the full evaluation
   */
  const runEvaluation = useCallback(async (context = {}) => {
    if (!sessionId) {
      throw new Error('No session.');
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          context,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to run evaluation: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setEvaluationResult(data.result);
        setPhase('complete');
      }
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  /**
   * Refine results with a custom request
   */
  const refineResults = useCallback(async (action, parameters, reason = '') => {
    if (!sessionId) {
      throw new Error('No session.');
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/refine`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          action,
          parameters,
          reason,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to refine results: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success && data.result) {
        setEvaluationResult(data.result);
      }
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  /**
   * Exclude a specific candidate
   */
  const excludeCandidate = useCallback(async (candidateId, reason = '') => {
    if (!sessionId) {
      throw new Error('No session.');
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/exclude`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          candidate_id: candidateId,
          reason,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to exclude candidate: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success && data.result) {
        setEvaluationResult(data.result);
      }
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  /**
   * Adjust dimension weight
   */
  const adjustWeight = useCallback(async (dimension, newWeight, reason = '') => {
    if (!sessionId) {
      throw new Error('No session.');
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/adjust-weight`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          dimension,
          new_weight: newWeight,
          reason,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to adjust weight: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success && data.result) {
        setEvaluationResult(data.result);
      }
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  /**
   * Get session status
   */
  const getSessionStatus = useCallback(async () => {
    if (!sessionId) {
      return null;
    }

    try {
      const response = await fetch(`${API_BASE}/session/${sessionId}`);
      if (!response.ok) {
        throw new Error(`Failed to get session status: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [sessionId]);

  /**
   * Reset the evaluation state
   */
  const reset = useCallback(() => {
    setSessionId(null);
    setStrategy(null);
    setStrategySummary('');
    setIsStrategyConfirmed(false);
    setEvaluationResult(null);
    setIsLoading(false);
    setError(null);
    setPhase('init');
  }, []);

  return {
    // State
    sessionId,
    strategy,
    strategySummary,
    isStrategyConfirmed,
    evaluationResult,
    isLoading,
    error,
    phase,

    // Actions
    createSession,
    proposeStrategy,
    modifyStrategy,
    confirmStrategy,
    runEvaluation,
    refineResults,
    excludeCandidate,
    adjustWeight,
    getSessionStatus,
    reset,
  };
}

export default useEvaluation;