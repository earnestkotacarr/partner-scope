/**
 * StrategyPanel Component
 *
 * Displays the evaluation strategy proposed by the Planner Agent.
 * Allows users to review, modify, and confirm evaluation dimensions and weights.
 *
 * Phase 1 of the evaluation framework.
 */

import React, { useState } from 'react';

const DIMENSION_COLORS = {
  market_compatibility: 'bg-blue-100 text-blue-700',
  financial_health: 'bg-green-100 text-green-700',
  technical_synergy: 'bg-purple-100 text-purple-700',
  operational_capacity: 'bg-orange-100 text-orange-700',
  geographic_coverage: 'bg-cyan-100 text-cyan-700',
  strategic_alignment: 'bg-indigo-100 text-indigo-700',
  cultural_fit: 'bg-pink-100 text-pink-700',
  resource_complementarity: 'bg-yellow-100 text-yellow-700',
  growth_potential: 'bg-emerald-100 text-emerald-700',
  risk_profile: 'bg-red-100 text-red-700',
};

export default function StrategyPanel({
  strategy,
  summary,
  onModify,
  onConfirm,
  isLoading,
  isConfirmed,
}) {
  const [modificationInput, setModificationInput] = useState('');
  const [isModifying, setIsModifying] = useState(false);

  const handleModify = async () => {
    if (!modificationInput.trim()) return;

    setIsModifying(true);
    try {
      await onModify(modificationInput);
      setModificationInput('');
    } finally {
      setIsModifying(false);
    }
  };

  if (!strategy) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  const dimensions = strategy.dimensions || [];

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="p-6 border-b">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">
            Evaluation Strategy
          </h2>
          {isConfirmed && (
            <span className="px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full">
              Confirmed
            </span>
          )}
        </div>
        {summary && (
          <p className="mt-2 text-sm text-gray-600">{summary}</p>
        )}
      </div>

      {/* Dimensions */}
      <div className="p-6">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">
          Evaluation Dimensions
        </h3>

        <div className="space-y-4">
          {dimensions.map((dim, index) => (
            <DimensionBar
              key={dim.dimension}
              dimension={dim}
              index={index}
            />
          ))}
        </div>

        {/* Exclusion Criteria */}
        {strategy.exclusion_criteria && strategy.exclusion_criteria.length > 0 && (
          <div className="mt-6 pt-4 border-t">
            <h4 className="text-sm font-medium text-gray-500 mb-2">
              Exclusion Criteria
            </h4>
            <div className="flex flex-wrap gap-2">
              {strategy.exclusion_criteria.map((criterion, i) => (
                <span
                  key={i}
                  className="px-2 py-1 bg-red-50 text-red-600 text-xs rounded"
                >
                  {criterion}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Modification Input */}
      {!isConfirmed && (
        <div className="p-6 border-t bg-gray-50">
          <h3 className="text-sm font-medium text-gray-700 mb-2">
            Modify Strategy
          </h3>
          <p className="text-xs text-gray-500 mb-3">
            Example: "Lower the weight of Geographic Coverage to 10%" or
            "Focus more on technical synergy"
          </p>
          <div className="flex gap-2">
            <input
              type="text"
              value={modificationInput}
              onChange={(e) => setModificationInput(e.target.value)}
              placeholder="Enter modification request..."
              className="flex-1 px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isLoading || isModifying}
            />
            <button
              onClick={handleModify}
              disabled={isLoading || isModifying || !modificationInput.trim()}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg text-sm font-medium hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isModifying ? 'Modifying...' : 'Modify'}
            </button>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {!isConfirmed && (
        <div className="p-6 border-t flex justify-end">
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Processing...' : 'Confirm Strategy & Start Evaluation'}
          </button>
        </div>
      )}
    </div>
  );
}

function DimensionBar({ dimension, index }) {
  const percentage = Math.round(dimension.weight * 100);
  const colorClass = DIMENSION_COLORS[dimension.dimension] || 'bg-gray-100 text-gray-700';
  const displayName = dimension.dimension.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

  return (
    <div className="group">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">
            {index + 1}. {displayName}
          </span>
          <span className={`px-2 py-0.5 text-xs font-medium rounded ${colorClass}`}>
            {percentage}%
          </span>
        </div>
        <span className="text-xs text-gray-400">
          Priority {dimension.priority}
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClass.split(' ')[0]} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Rationale (shown on hover) */}
      {dimension.rationale && (
        <p className="mt-1 text-xs text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity">
          {dimension.rationale}
        </p>
      )}

      {/* Description */}
      {dimension.description && (
        <p className="mt-1 text-xs text-gray-400">
          {dimension.description}
        </p>
      )}
    </div>
  );
}