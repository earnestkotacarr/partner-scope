/**
 * DebugPanel Component
 *
 * Floating panel that appears in debug mode, allowing quick navigation
 * to any page with pre-populated fake data.
 */

import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { isDebugMode, disableDebugMode, debugPages, debugSettings, setDebugSetting } from '../debug/config';
import { generateFakeData } from '../debug/fakeData';

export default function DebugPanel() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isExpanded, setIsExpanded] = useState(false);
  const [candidatesCount, setCandidatesCount] = useState(debugSettings.fakeCandidatesCount);

  // Don't render if not in debug mode
  if (!isDebugMode()) {
    return null;
  }

  const handleNavigate = (path) => {
    // Generate fresh fake data
    const fakeData = generateFakeData(candidatesCount, debugSettings.seed);

    // For evaluation page, pass state with candidates
    if (path === '/evaluate') {
      navigate(path, {
        state: {
          candidates: fakeData.candidates,
          startupProfile: fakeData.startupProfile,
        },
      });
    } else {
      navigate(path);
    }
  };

  const handleCandidatesChange = (e) => {
    const count = parseInt(e.target.value, 10);
    setCandidatesCount(count);
    setDebugSetting('fakeCandidatesCount', count);
  };

  const handleDisableDebug = () => {
    if (window.confirm('Disable debug mode? The page will reload.')) {
      disableDebugMode();
    }
  };

  return (
    <div className="fixed bottom-4 left-4 z-50">
      {/* Collapsed State - Just the debug badge */}
      {!isExpanded && (
        <button
          onClick={() => setIsExpanded(true)}
          className="bg-orange-500 hover:bg-orange-600 text-white px-3 py-2 rounded-lg shadow-lg flex items-center gap-2 text-sm font-medium transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          DEBUG
        </button>
      )}

      {/* Expanded State - Full panel */}
      {isExpanded && (
        <div className="bg-white rounded-xl shadow-2xl border border-orange-200 w-72 overflow-hidden">
          {/* Header */}
          <div className="bg-orange-500 text-white px-4 py-3 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span className="font-semibold">Debug Panel</span>
            </div>
            <button
              onClick={() => setIsExpanded(false)}
              className="hover:bg-orange-600 rounded p-1 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="p-4 space-y-4">
            {/* Current Page Indicator */}
            <div className="text-xs text-slate-500">
              Current: <span className="font-medium text-slate-700">{location.pathname}</span>
            </div>

            {/* Quick Navigation */}
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase mb-2">Quick Navigation</h3>
              <div className="space-y-1">
                {debugPages.map((page) => (
                  <button
                    key={page.path}
                    onClick={() => handleNavigate(page.path)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                      location.pathname === page.path
                        ? 'bg-orange-100 text-orange-700 font-medium'
                        : 'hover:bg-slate-100 text-slate-700'
                    }`}
                  >
                    <div className="font-medium">{page.name}</div>
                    <div className="text-xs text-slate-500">{page.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Settings */}
            <div className="border-t border-slate-200 pt-4">
              <h3 className="text-xs font-semibold text-slate-500 uppercase mb-2">Settings</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm text-slate-600">Candidates:</label>
                  <select
                    value={candidatesCount}
                    onChange={handleCandidatesChange}
                    className="text-sm border border-slate-300 rounded px-2 py-1"
                  >
                    <option value="5">5</option>
                    <option value="10">10</option>
                    <option value="15">15</option>
                    <option value="20">20</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="border-t border-slate-200 pt-4">
              <button
                onClick={handleDisableDebug}
                className="w-full px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition-colors"
              >
                Disable Debug Mode
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
