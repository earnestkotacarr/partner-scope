/**
 * Evaluation Components Module
 *
 * Exports all evaluation-related components for the Partner Evaluation Framework.
 */

// Original panel components
export { default as StrategyPanel } from './StrategyPanel';
export { default as EvaluationResults } from './EvaluationResults';

// Card components for chat-based interface
export { default as StrategyCard } from './StrategyCard';
export { default as DimensionScoresCard } from './DimensionScoresCard';
export { default as CandidateRankingCard } from './CandidateRankingCard';
export { default as EvaluationInsightsCard } from './EvaluationInsightsCard';

// Chat-embedded components (inline display in chat)
export { default as ChatStrategyDisplay } from './ChatStrategyDisplay';
export { default as ChatRankingDisplay } from './ChatRankingDisplay';
export { default as ChatDimensionScores } from './ChatDimensionScores';

// Modal and UI components
export { default as CandidateDetailModal } from './CandidateDetailModal';
export { default as PhaseTransitionButtons } from './PhaseTransitionButtons';
