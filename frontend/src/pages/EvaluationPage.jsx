/**
 * EvaluationPage Component
 *
 * Full-screen chat-based evaluation interface.
 * All evaluation data (Strategy, Rankings, Scores) displayed inline in chat.
 * Phase transitions via explicit buttons instead of string matching.
 *
 * Design: OpenAI-style clean white background with avatar-based layout
 */

import { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useScenario } from '../context/ScenarioContext';
import CostBadge from '../components/CostBadge';

// Chat-embedded evaluation components
import ChatStrategyDisplay from '../components/evaluation/ChatStrategyDisplay';
import ChatRankingDisplay from '../components/evaluation/ChatRankingDisplay';
import CandidateDetailModal from '../components/evaluation/CandidateDetailModal';
import PhaseTransitionButtons from '../components/evaluation/PhaseTransitionButtons';
import ExternalResearchComparison from '../components/evaluation/ExternalResearchComparison';

export default function EvaluationPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { scenario, results, addCost, getCostSummary, applyEvaluationToResults, setEvaluationState } = useScenario();
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Chat state - messages now include embedded data
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');

  // Evaluation state
  const [sessionId, setSessionId] = useState(null);
  const [phase, setPhase] = useState('init'); // init, planning, evaluating, complete
  const [strategy, setStrategy] = useState(null);
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [startupProfile, setStartupProfile] = useState(null);

  // Modal state
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  // Cost tracking
  const [evaluationCost, setEvaluationCost] = useState({
    input_tokens: 0,
    output_tokens: 0,
    total_cost: 0,
  });

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Initialize from navigation state or context
  useEffect(() => {
    const stateCandidates = location.state?.candidates || results?.matches || [];
    const stateProfile = location.state?.startupProfile || {
      name: scenario?.startup_name || 'My Startup',
      industry: scenario?.industry || '',
      stage: scenario?.investment_stage || 'Seed',
      partner_needs: scenario?.partner_needs || '',
      description: scenario?.description || '',
    };

    setCandidates(stateCandidates);
    setStartupProfile(stateProfile);

    if (stateCandidates.length === 0) {
      setMessages([{
        role: 'assistant',
        content: "It looks like there are no candidates to evaluate. Please go back to the search results and try again.",
      }]);
      return;
    }

    // Start with welcome message
    setMessages([{
      role: 'assistant',
      content: `Welcome to the AI Partner Evaluation! I found **${stateCandidates.length} candidates** from your search.

I'll help you evaluate these partners using multi-dimensional analysis. Here's how it works:

1. **Strategy Planning** - I'll propose evaluation dimensions and weights based on your needs
2. **Multi-Agent Evaluation** - Specialized AI agents will assess each candidate
3. **Ranking & Insights** - I'll provide ranked results with detailed insights

Click **"Propose Strategy"** below to begin, or ask me any questions first.`,
    }]);
  }, [location.state, results, scenario]);

  // Handle phase transition button clicks
  const handlePhaseAction = async (actionKey) => {
    switch (actionKey) {
      case 'propose_strategy':
        await sendApiRequest('__ACTION__:propose_strategy', 'start');
        break;
      case 'confirm_and_run':
        await sendApiRequest('__ACTION__:confirm_and_run', 'confirm');
        break;
      case 'modify_strategy':
        // Add a message asking user what to modify
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: "What would you like to modify? You can:\n- Adjust dimension weights\n- Add or remove dimensions\n- Focus on specific aspects (e.g., \"focus more on technical synergy\")\n\nPlease describe your changes.",
        }]);
        break;
      case 'refine_results':
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: "What refinements would you like? You can:\n- Exclude specific candidates\n- Adjust dimension weights and re-rank\n- Focus on particular aspects\n\nTell me what you'd like to change.",
        }]);
        break;
      case 'new_evaluation':
        // Reset and start over
        setPhase('init');
        setStrategy(null);
        setEvaluationResult(null);
        setMessages([{
          role: 'assistant',
          content: `Starting a new evaluation for **${candidates.length} candidates**. Click **"Propose Strategy"** to begin.`,
        }]);
        break;
      case 'view_results':
        // Navigate back to results page with enriched data
        navigate('/results');
        break;
      default:
        break;
    }
  };

  // Core API request function
  const sendApiRequest = async (userMessage, actionHint = null) => {
    // Don't show __ACTION__ messages to user
    const displayMessage = userMessage.startsWith('__ACTION__') ? null : userMessage;

    if (displayMessage) {
      setMessages(prev => [...prev, { role: 'user', content: displayMessage }]);
    }

    setLoading(true);

    try {
      const response = await fetch('/api/evaluation/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: messages,
          current_message: actionHint || userMessage,
          session_id: sessionId,
          phase,
          candidates,
          startup_profile: startupProfile,
          strategy,
          evaluation_result: evaluationResult,
          action_hint: actionHint, // Explicit action hint for backend
        }),
      });

      if (!response.ok) {
        throw new Error('Evaluation request failed');
      }

      const data = await response.json();

      // Update state based on response
      if (data.session_id) {
        setSessionId(data.session_id);
      }

      const newPhase = data.phase || phase;
      setPhase(newPhase);

      const newStrategy = data.strategy || strategy;
      if (data.strategy) {
        setStrategy(newStrategy);
      }

      const newResult = data.evaluation_result || evaluationResult;
      if (data.evaluation_result) {
        setEvaluationResult(newResult);

        // Apply evaluation results to main results in context (enrichment)
        if (data.phase === 'complete') {
          applyEvaluationToResults(data.evaluation_result, newStrategy);

          // Save to global context for comparison panel persistence
          setEvaluationState({
            strategy: newStrategy,
            phase: 'complete',
            evaluatedAt: new Date().toISOString(),
            result: newResult,
          });
        }
      }

      // Track cost
      if (data.cost) {
        setEvaluationCost(prev => ({
          input_tokens: prev.input_tokens + (data.cost.input_tokens || 0),
          output_tokens: prev.output_tokens + (data.cost.output_tokens || 0),
          total_cost: prev.total_cost + (data.cost.total_cost || 0),
        }));
        addCost(data.cost, 'evaluation');
      }

      // Add assistant response with embedded data
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        // Attach data for inline rendering
        embeddedData: {
          strategy: newPhase === 'planning' ? newStrategy : null,
          evaluationResult: newPhase === 'complete' ? newResult : null,
          showStrategy: data.phase === 'planning' && data.strategy,
          showResults: data.phase === 'complete' && data.evaluation_result,
        },
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      console.error('Evaluation error:', err);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I encountered an error processing your request. Please try again.",
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Handle sending chat messages
  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!inputValue.trim() || loading) return;

    const content = inputValue.trim();
    setInputValue('');
    await sendApiRequest(content);
  };

  // Handle clicking on a candidate in the ranking
  const handleCandidateClick = (candidate) => {
    setSelectedCandidate(candidate);
  };

  // Handle textarea keydown
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Get placeholder text based on phase
  const getPlaceholder = () => {
    switch (phase) {
      case 'init':
        return "Ask questions or click 'Propose Strategy' to begin...";
      case 'planning':
        return "Describe any changes to the strategy, or confirm to run...";
      case 'complete':
        return "Ask about results, request refinements, or compare candidates...";
      default:
        return "Type your message...";
    }
  };

  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">
      {/* Header - Minimal with subtle border */}
      <div className="bg-white border-b border-gray-100 px-4 py-4 flex-shrink-0">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-semibold text-gray-900">Partner Evaluation</h1>
            <PhaseIndicator phase={phase} />
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">
              {candidates.length} candidates
            </span>
            <button
              onClick={() => navigate('/results')}
              className="text-gray-600 hover:text-gray-900 font-medium text-sm"
            >
              Back to Results
            </button>
          </div>
        </div>
      </div>

      {/* Main Chat Area - Flex container */}
      <div className="flex-1 container mx-auto px-4 flex flex-col max-w-3xl min-h-0">
        {/* Messages - Scrollable area */}
        <div className="flex-1 overflow-y-auto py-6">
          <div className="space-y-6">
            {messages.map((msg, index) => (
              <ChatMessage
                key={index}
                message={msg}
                onCandidateClick={handleCandidateClick}
                startupProfile={startupProfile}
                strategy={strategy}
              />
            ))}

            {/* Typing Indicator */}
            {loading && (
              <div className="flex gap-4">
                <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div className="flex items-center gap-1 text-gray-400 pt-2">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Bottom Fixed Area - Buttons and Input */}
        <div className="flex-shrink-0 pb-6">
          {/* Phase Transition Buttons */}
          {!loading && phase !== 'evaluating' && (
            <div className="mb-4">
              <PhaseTransitionButtons
                phase={phase}
                onAction={handlePhaseAction}
                disabled={loading}
              />
            </div>
          )}

          {/* Evaluating Progress */}
          {phase === 'evaluating' && loading && (
            <div className="mb-4 bg-gray-50 rounded-2xl p-4 border border-gray-200">
              <div className="flex items-center gap-3">
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-300 border-t-gray-900"></div>
                <span className="text-gray-700 font-medium">Running multi-dimensional evaluation...</span>
              </div>
            </div>
          )}

          {/* Chat Input - Inline textarea */}
          <form onSubmit={handleSendMessage} className="relative">
            <div className="bg-gray-50 rounded-2xl border border-gray-200 focus-within:border-gray-400 focus-within:bg-white transition-colors">
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                placeholder={getPlaceholder()}
                rows={1}
                className="w-full bg-transparent px-4 py-3 pr-12 resize-none focus:outline-none text-gray-900 placeholder-gray-500"
                style={{ minHeight: '48px', maxHeight: '200px' }}
              />
              <button
                type="submit"
                disabled={loading || !inputValue.trim()}
                className="absolute right-2 bottom-2 p-2 rounded-xl bg-black text-white disabled:bg-gray-300 disabled:text-gray-500 hover:bg-gray-800 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Floating Cost Badge */}
      <CostBadge
        cost={{
          ...getCostSummary(),
          ...evaluationCost,
          total_cost: (getCostSummary()?.total_cost || 0) + evaluationCost.total_cost,
        }}
        isSearching={loading}
      />

      {/* External Research Comparison - Floating panel, top-right */}
      {evaluationResult && (
        <div className="fixed top-20 right-6 z-40 w-96 max-h-[calc(100vh-120px)] overflow-auto shadow-2xl rounded-xl border border-gray-200 bg-white">
          <ExternalResearchComparison
            partnerScopeResults={evaluationResult}
            startupProfile={startupProfile}
            strategy={strategy}
            onCandidateClick={(c) => setSelectedCandidate(c)}
          />
        </div>
      )}

      {/* Candidate Detail Modal */}
      {selectedCandidate && (
        <CandidateDetailModal
          candidate={selectedCandidate}
          onClose={() => setSelectedCandidate(null)}
        />
      )}
    </div>
  );
}

// Chat Message Component with avatar-based layout
function ChatMessage({ message, onCandidateClick, startupProfile, strategy }) {
  const isUser = message.role === 'user';
  const embeddedData = message.embeddedData || {};

  // Enhanced markdown rendering
  const renderContent = (content) => {
    if (!content) return null;

    const lines = content.split('\n');

    // Helper to render inline formatting (bold, etc.)
    const renderInline = (text) => {
      if (!text) return null;
      const boldParts = text.split(/\*\*([^*]+)\*\*/g);
      return boldParts.map((part, j) =>
        j % 2 === 1 ? <strong key={j}>{part}</strong> : part
      );
    };

    return lines.map((line, i) => {
      // Handle headers (## and ###)
      if (line.startsWith('### ')) {
        return (
          <h4 key={i} className="font-semibold text-sm mt-3 mb-1 text-gray-900">
            {renderInline(line.slice(4))}
          </h4>
        );
      }
      if (line.startsWith('## ')) {
        return (
          <h3 key={i} className="font-bold text-base mt-4 mb-2 text-gray-900">
            {renderInline(line.slice(3))}
          </h3>
        );
      }

      // Handle unordered list items (- or *)
      if (/^[-*]\s/.test(line)) {
        return (
          <div key={i} className="flex items-start gap-2 ml-2">
            <span className="text-gray-400 mt-0.5">•</span>
            <span>{renderInline(line.slice(2))}</span>
          </div>
        );
      }

      // Handle numbered list items (1. 2. etc.)
      const numberedMatch = line.match(/^(\d+)\.\s(.+)/);
      if (numberedMatch) {
        return (
          <div key={i} className="flex items-start gap-2 ml-2">
            <span className="text-gray-600 font-medium min-w-[1.25rem]">{numberedMatch[1]}.</span>
            <span>{renderInline(numberedMatch[2])}</span>
          </div>
        );
      }

      // Handle + list items (sub-items)
      if (/^\+\s/.test(line)) {
        return (
          <div key={i} className="flex items-start gap-2 ml-6 text-gray-600">
            <span className="text-gray-400 mt-0.5">+</span>
            <span>{renderInline(line.slice(2))}</span>
          </div>
        );
      }

      // Empty line
      if (line.trim() === '') {
        return <div key={i} className="h-2" />;
      }

      // Regular text
      return (
        <span key={i}>
          {renderInline(line)}
          {i < lines.length - 1 && <br />}
        </span>
      );
    });
  };

  return (
    <div className="flex gap-4">
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
        isUser ? 'bg-gray-200' : 'bg-black'
      }`}>
        {isUser ? (
          <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        ) : (
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        )}
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        <div className="text-sm leading-relaxed text-gray-800">
          {renderContent(message.content)}
        </div>

        {/* Embedded Strategy Display */}
        {embeddedData.showStrategy && embeddedData.strategy && (
          <ChatStrategyDisplay strategy={embeddedData.strategy} />
        )}

        {/* Embedded Results Display */}
        {embeddedData.showResults && embeddedData.evaluationResult && (
          <>
            <ChatRankingDisplay
              candidates={embeddedData.evaluationResult.top_candidates}
              onCandidateClick={onCandidateClick}
            />
            {embeddedData.evaluationResult.insights && embeddedData.evaluationResult.insights.length > 0 && (
              <div className="mt-3 bg-gray-50 rounded-lg p-3 border border-gray-100">
                <h4 className="text-xs font-semibold text-gray-600 mb-2">Key Insights</h4>
                <ul className="space-y-1">
                  {embeddedData.evaluationResult.insights.slice(0, 3).map((insight, i) => (
                    <li key={i} className="text-xs text-gray-600 flex items-start gap-2">
                      <span className="text-gray-400 mt-0.5">•</span>
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {/* External Research Comparison */}
            <ExternalResearchComparison
              partnerScopeResults={embeddedData.evaluationResult}
              startupProfile={startupProfile}
              strategy={strategy}
              onCandidateClick={onCandidateClick}
            />
          </>
        )}
      </div>
    </div>
  );
}

// Phase indicator component - grayscale
function PhaseIndicator({ phase }) {
  const phases = [
    { id: 'init', label: 'Init' },
    { id: 'planning', label: 'Strategy' },
    { id: 'evaluating', label: 'Evaluating' },
    { id: 'complete', label: 'Complete' },
  ];

  const currentIndex = phases.findIndex(p => p.id === phase);

  return (
    <div className="flex items-center gap-1">
      {phases.map((p, index) => {
        const isActive = p.id === phase;
        const isComplete = index < currentIndex;

        return (
          <div key={p.id} className="flex items-center">
            {index > 0 && (
              <div className={`w-4 h-0.5 ${isComplete ? 'bg-gray-800' : 'bg-gray-200'}`} />
            )}
            <div
              className={`px-2 py-0.5 text-xs rounded-full font-medium ${
                isActive
                  ? 'bg-gray-900 text-white'
                  : isComplete
                  ? 'bg-gray-200 text-gray-700'
                  : 'bg-gray-100 text-gray-400'
              }`}
            >
              {isComplete ? '✓' : ''} {p.label}
            </div>
          </div>
        );
      })}
    </div>
  );
}
