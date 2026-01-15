/**
 * EvaluationPage Component
 *
 * Full-screen chat-based evaluation interface.
 * All evaluation data (Strategy, Rankings, Scores) displayed inline in chat.
 * Phase transitions via explicit buttons instead of string matching.
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


export default function EvaluationPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { scenario, results, addCost, getCostSummary, applyEvaluationToResults } = useScenario();
  const messagesEndRef = useRef(null);

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
  const handleSendMessage = async (content) => {
    await sendApiRequest(content);
  };

  // Handle clicking on a candidate in the ranking
  const handleCandidateClick = (candidate) => {
    setSelectedCandidate(candidate);
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-100">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={() => navigate('/results')}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          <div className="flex items-center gap-3">
            <h1 className="text-base font-medium text-gray-900">Partner Evaluation</h1>
            <PhaseIndicator phase={phase} />
          </div>
          <span className="text-sm text-gray-400">{candidates.length} candidates</span>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-8">
          {messages.map((msg, index) => (
            <ChatMessage
              key={index}
              message={msg}
              onCandidateClick={handleCandidateClick}
            />
          ))}

          {/* Typing Indicator */}
          {loading && (
            <div className="mb-8">
              <div className="flex gap-4">
                <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div className="flex-1 pt-2">
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 bg-gray-300 rounded-full animate-pulse" />
                    <div className="w-2 h-2 bg-gray-300 rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-300 rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Evaluating Progress */}
          {phase === 'evaluating' && loading && (
            <div className="mb-8 flex gap-4">
              <div className="w-8 flex-shrink-0" />
              <div className="flex-1">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-50 text-gray-600 text-sm rounded-full border border-gray-200">
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-gray-600"></div>
                  Running multi-dimensional evaluation...
                </div>
              </div>
            </div>
          )}

          {/* Phase Transition Buttons */}
          {!loading && phase !== 'evaluating' && (
            <div className="mb-8 flex gap-4">
              <div className="w-8 flex-shrink-0" />
              <div className="flex-1">
                <PhaseTransitionButtons
                  phase={phase}
                  onAction={handlePhaseAction}
                  disabled={loading}
                />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-100 bg-white">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <div className="relative">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (inputValue.trim() && !loading) {
                    handleSendMessage(inputValue.trim());
                    setInputValue('');
                  }
                }
              }}
              placeholder={
                phase === 'init' ? "Ask questions or click 'Propose Strategy' to begin..." :
                phase === 'planning' ? "Describe any changes to the strategy, or confirm to run..." :
                phase === 'complete' ? "Ask about results, request refinements, or compare candidates..." :
                "Type your message..."
              }
              disabled={loading}
              rows={1}
              className="w-full px-4 py-3 pr-12 border border-gray-200 rounded-2xl resize-none focus:outline-none focus:border-gray-300 focus:ring-0 disabled:bg-gray-50 disabled:text-gray-400 text-gray-800 placeholder-gray-400"
              style={{ minHeight: '48px', maxHeight: '200px' }}
              onInput={(e) => {
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
              }}
            />
            <button
              type="button"
              onClick={() => {
                if (inputValue.trim() && !loading) {
                  handleSendMessage(inputValue.trim());
                  setInputValue('');
                }
              }}
              disabled={loading || !inputValue.trim()}
              className="absolute right-2 bottom-2 p-2 text-gray-400 hover:text-gray-600 disabled:text-gray-300 disabled:hover:text-gray-300 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
          <p className="text-xs text-gray-400 text-center mt-3">
            Press Enter to send, Shift+Enter for new line
          </p>
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

// Chat Message Component with embedded data support - OpenAI style
function ChatMessage({ message, onCandidateClick }) {
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
        j % 2 === 1 ? <strong key={j} className="font-semibold">{part}</strong> : part
      );
    };

    return lines.map((line, i) => {
      // Handle headers (## and ###)
      if (line.startsWith('### ')) {
        return (
          <h4 key={i} className="font-semibold text-sm mt-3 mb-1">
            {renderInline(line.slice(4))}
          </h4>
        );
      }
      if (line.startsWith('## ')) {
        return (
          <h3 key={i} className="font-bold text-base mt-4 mb-2">
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
            <span className="text-gray-500 font-medium min-w-[1.25rem]">{numberedMatch[1]}.</span>
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
        return <div key={i} className="h-3" />;
      }

      // Regular text
      return (
        <p key={i} className={i > 0 ? 'mt-3' : ''}>
          {renderInline(line)}
        </p>
      );
    });
  };

  return (
    <div className="mb-8">
      <div className="flex gap-4">
        {isUser ? (
          <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
            <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
        ) : (
          <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center flex-shrink-0">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        )}
        <div className="flex-1 pt-1">
          <div className="text-gray-800 leading-relaxed">
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
                <div className="mt-4 bg-gray-50 rounded-xl p-4 border border-gray-100">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">Key Insights</h4>
                  <ul className="space-y-2">
                    {embeddedData.evaluationResult.insights.slice(0, 3).map((insight, i) => (
                      <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-gray-400 mt-0.5">•</span>
                        {insight}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// Phase indicator component - OpenAI style
function PhaseIndicator({ phase }) {
  const phaseLabels = {
    init: 'Ready',
    planning: 'Planning',
    evaluating: 'Evaluating',
    complete: 'Complete',
  };

  return (
    <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded-full">
      {phaseLabels[phase] || phase}
    </span>
  );
}
