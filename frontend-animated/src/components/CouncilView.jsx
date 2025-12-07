import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence, LayoutGroup } from 'framer-motion';
import { Send, Loader2, RotateCcw, Sparkles } from 'lucide-react';
import { LLMCard } from './LLMCard';
import { VotingDashboard } from './VotingDashboard';
import { api } from '../api';
import { cn } from '../utils/cn';

// Flow stages
const STAGES = {
  IDLE: 'idle',
  COLLECTING: 'collecting',
  VOTING: 'voting',
  SYNTHESIZING: 'synthesizing',
  COMPLETE: 'complete',
};

// Initial model state
const createInitialModels = () => [
  { id: 'gemini', model: 'gemini', response: null, isLoading: false, loadingTime: 0, votes: 0, avgRank: 0 },
  { id: 'codex', model: 'codex', response: null, isLoading: false, loadingTime: 0, votes: 0, avgRank: 0 },
  { id: 'claude', model: 'claude', response: null, isLoading: false, loadingTime: 0, votes: 0, avgRank: 0 },
];

/**
 * CouncilView Component
 * Main orchestration component that manages the 3-stage LLM Council flow
 */
export function CouncilView() {
  const [prompt, setPrompt] = useState('');
  const [stage, setStage] = useState(STAGES.IDLE);
  const [models, setModels] = useState(createInitialModels());
  const [expandedCard, setExpandedCard] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [synthesis, setSynthesis] = useState(null);
  const [error, setError] = useState(null);

  // Timer effect for loading states
  useEffect(() => {
    let interval;
    if (stage === STAGES.COLLECTING || stage === STAGES.VOTING) {
      interval = setInterval(() => {
        setModels((prev) =>
          prev.map((m) =>
            m.isLoading ? { ...m, loadingTime: m.loadingTime + 0.1 } : m
          )
        );
      }, 100);
    }
    return () => clearInterval(interval);
  }, [stage]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || stage !== STAGES.IDLE) return;

    setError(null);
    setSynthesis(null);

    try {
      // Create conversation
      const conversation = await api.createConversation();
      setConversationId(conversation.id);

      // Reset and start loading
      setModels(createInitialModels().map((m) => ({ ...m, isLoading: true })));
      setStage(STAGES.COLLECTING);

      // Send message with streaming
      await api.sendMessageStream(conversation.id, prompt, (eventType, event) => {
        switch (eventType) {
          case 'stage1_complete':
            handleStage1Complete(event.data);
            break;
          case 'stage2_start':
            setStage(STAGES.VOTING);
            setModels((prev) => prev.map((m) => ({ ...m, isLoading: true, loadingTime: 0 })));
            break;
          case 'stage2_complete':
            handleStage2Complete(event.data, event.metadata);
            break;
          case 'stage3_start':
            setStage(STAGES.SYNTHESIZING);
            break;
          case 'stage3_complete':
            handleStage3Complete(event.data);
            break;
          case 'complete':
            setStage(STAGES.COMPLETE);
            break;
          case 'error':
            setError(event.message);
            setStage(STAGES.IDLE);
            break;
        }
      });
    } catch (err) {
      setError(err.message);
      setStage(STAGES.IDLE);
    }
  };

  // Handle Stage 1 completion (individual responses)
  const handleStage1Complete = (data) => {
    setModels((prev) =>
      prev.map((m) => {
        const response = data.find((d) => d.model === m.model);
        return {
          ...m,
          response: response?.response || null,
          isLoading: false,
        };
      })
    );
  };

  // Handle Stage 2 completion (voting)
  const handleStage2Complete = (data, metadata) => {
    if (!metadata?.aggregate_rankings) return;

    // Update models with ranking data
    setModels((prev) => {
      const updated = prev.map((m) => {
        const ranking = metadata.aggregate_rankings.find(
          (r) => r.model === m.model
        );
        return {
          ...m,
          isLoading: false,
          votes: ranking ? Math.round((4 - ranking.avg_rank) * 10) : 0, // Convert avg rank to score
          avgRank: ranking?.avg_rank || 0,
        };
      });

      // Sort by votes (winner first)
      return updated.sort((a, b) => b.votes - a.votes);
    });
  };

  // Handle Stage 3 completion (synthesis)
  const handleStage3Complete = (data) => {
    setSynthesis(data);
  };

  // Reset the council
  const handleReset = () => {
    setPrompt('');
    setStage(STAGES.IDLE);
    setModels(createInitialModels());
    setExpandedCard(null);
    setConversationId(null);
    setSynthesis(null);
    setError(null);
  };

  // Toggle card expansion
  const toggleCard = (modelId) => {
    setExpandedCard((prev) => (prev === modelId ? null : modelId));
  };

  // Get winner model
  const winner = stage === STAGES.COMPLETE ? models[0]?.model : null;

  // Calculate rankings for dashboard
  const rankings = models.map((m, index) => ({
    model: m.model,
    votes: m.votes,
    avgRank: m.avgRank,
    rank: index + 1,
  }));

  return (
    <div className="min-h-screen bg-ai-dark">
      {/* Header */}
      <header className="border-b border-ai-border bg-ai-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-ai-accent to-purple-500 rounded-lg">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">LLM Council</h1>
                <p className="text-xs text-gray-400">Multi-AI Deliberation System</p>
              </div>
            </div>

            {stage !== STAGES.IDLE && (
              <button
                onClick={handleReset}
                className="flex items-center gap-2 px-3 py-2 text-sm text-gray-400 hover:text-white transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Input form */}
        <motion.form
          onSubmit={handleSubmit}
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="relative">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ask the council a question..."
              disabled={stage !== STAGES.IDLE}
              rows={3}
              className={cn(
                'w-full px-4 py-3 pr-14 rounded-xl border resize-none',
                'bg-ai-card/80 backdrop-blur-sm text-white placeholder-gray-500',
                'focus:outline-none focus:ring-2 focus:ring-ai-accent focus:border-transparent',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                stage === STAGES.IDLE ? 'border-ai-border' : 'border-ai-accent/30',
              )}
            />
            <button
              type="submit"
              disabled={!prompt.trim() || stage !== STAGES.IDLE}
              className={cn(
                'absolute right-3 bottom-3 p-2 rounded-lg transition-all',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                prompt.trim() && stage === STAGES.IDLE
                  ? 'bg-ai-accent hover:bg-ai-accent/80 text-white'
                  : 'bg-ai-border text-gray-500',
              )}
            >
              {stage === STAGES.IDLE ? (
                <Send className="w-5 h-5" />
              ) : (
                <Loader2 className="w-5 h-5 animate-spin" />
              )}
            </button>
          </div>

          {/* Stage indicator */}
          {stage !== STAGES.IDLE && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-3 flex items-center gap-2 text-sm text-ai-accent"
            >
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>
                {stage === STAGES.COLLECTING && 'Stage 1: Collecting individual responses...'}
                {stage === STAGES.VOTING && 'Stage 2: Peer review in progress...'}
                {stage === STAGES.SYNTHESIZING && 'Stage 3: Chairman synthesizing...'}
                {stage === STAGES.COMPLETE && 'Deliberation complete!'}
              </span>
            </motion.div>
          )}
        </motion.form>

        {/* Error message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* LLM Cards */}
        <LayoutGroup>
          <motion.div layout className="space-y-4 mb-8">
            <AnimatePresence mode="popLayout">
              {models.map((model, index) => (
                <LLMCard
                  key={model.id}
                  model={model.model}
                  response={model.response}
                  isLoading={model.isLoading}
                  loadingTime={model.loadingTime}
                  isWinner={winner === model.model}
                  rank={stage === STAGES.COMPLETE ? index + 1 : null}
                  votes={model.votes}
                  isExpanded={expandedCard === model.id}
                  onToggleExpand={() => toggleCard(model.id)}
                />
              ))}
            </AnimatePresence>
          </motion.div>
        </LayoutGroup>

        {/* Voting Dashboard */}
        <AnimatePresence>
          {(stage === STAGES.VOTING || stage === STAGES.SYNTHESIZING || stage === STAGES.COMPLETE) && (
            <VotingDashboard
              rankings={rankings}
              isVoting={stage === STAGES.VOTING}
              totalVotes={models.reduce((acc, m) => acc + m.votes, 0)}
            />
          )}
        </AnimatePresence>

        {/* Synthesis result */}
        <AnimatePresence>
          {synthesis && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="mt-8 p-6 bg-gradient-to-br from-ai-accent/10 to-purple-500/10 border border-ai-accent/30 rounded-xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-ai-accent/20 rounded-lg">
                  <Sparkles className="w-5 h-5 text-ai-accent" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">Chairman's Synthesis</h3>
                  <p className="text-xs text-gray-400">Final answer from the council</p>
                </div>
              </div>
              <div className="prose prose-sm prose-invert max-w-none">
                <p className="text-gray-300 whitespace-pre-wrap">{synthesis.response}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default CouncilView;
