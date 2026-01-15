/**
 * PhaseTransitionButtons Component
 *
 * Displays action buttons for transitioning between evaluation phases.
 * Replaces string-matching based phase detection.
 *
 * Design: Black primary buttons, white secondary with rounded-full pills
 */

export default function PhaseTransitionButtons({ phase, onAction, disabled }) {
  // Define available actions based on current phase
  const getPhaseActions = () => {
    switch (phase) {
      case 'init':
        return [
          {
            key: 'propose_strategy',
            label: 'Propose Strategy',
            primary: true,
            icon: (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            ),
          },
        ];

      case 'planning':
        return [
          {
            key: 'confirm_and_run',
            label: 'Confirm & Run Evaluation',
            primary: true,
            icon: (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ),
          },
          {
            key: 'modify_strategy',
            label: 'Modify Strategy',
            primary: false,
            icon: (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            ),
          },
        ];

      case 'evaluating':
        return []; // No actions during evaluation - show loading

      case 'complete':
        return [
          {
            key: 'view_results',
            label: 'View Enriched Results',
            primary: true,
            icon: (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            ),
          },
          {
            key: 'refine_results',
            label: 'Refine Results',
            primary: false,
            icon: (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
            ),
          },
          {
            key: 'new_evaluation',
            label: 'New Evaluation',
            primary: false,
            icon: (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            ),
          },
        ];

      default:
        return [];
    }
  };

  const actions = getPhaseActions();

  if (actions.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-2 justify-center">
      {actions.map((action) => (
        <button
          key={action.key}
          onClick={() => onAction?.(action.key)}
          disabled={disabled}
          className={`
            flex items-center gap-2 px-4 py-2.5 rounded-full font-medium transition-all
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md active:scale-95'}
            ${
              action.primary
                ? 'bg-black text-white hover:bg-gray-800'
                : 'bg-white text-gray-700 border border-gray-300 hover:border-gray-400'
            }
          `}
        >
          {action.icon}
          <span>{action.label}</span>
        </button>
      ))}
    </div>
  );
}
