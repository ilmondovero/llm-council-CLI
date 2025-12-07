import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import CountUp from 'react-countup';
import ReactMarkdown from 'react-markdown';
import { ChevronDown, Clock, Sparkles, Crown } from 'lucide-react';
import { cn } from '../utils/cn';

// Model configuration with colors and icons
const MODEL_CONFIG = {
  gemini: {
    name: 'Gemini',
    color: 'gemini',
    gradient: 'from-blue-500 to-cyan-400',
    icon: '✨',
  },
  claude: {
    name: 'Claude',
    color: 'claude',
    gradient: 'from-amber-500 to-orange-400',
    icon: '🧠',
  },
  codex: {
    name: 'ChatGPT',
    color: 'chatgpt',
    gradient: 'from-emerald-500 to-green-400',
    icon: '🤖',
  },
};

/**
 * LLMCard Component
 * Displays an LLM response with loading timer, expandable content, and winner highlight
 */
export function LLMCard({
  model,
  response,
  isLoading,
  loadingTime,
  isWinner,
  rank,
  votes,
  isExpanded,
  onToggleExpand,
}) {
  const config = MODEL_CONFIG[model] || MODEL_CONFIG.gemini;

  // Generate summary from response (first 150 chars or first sentence)
  const getSummary = (text) => {
    if (!text) return '';
    const firstSentence = text.split(/[.!?]/)[0];
    if (firstSentence.length < 150) return firstSentence + '.';
    return text.substring(0, 150) + '...';
  };

  return (
    <motion.div
      layout
      layoutId={`card-${model}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{
        layout: { type: 'spring', stiffness: 300, damping: 30 },
        opacity: { duration: 0.2 },
      }}
      className={cn(
        'relative rounded-xl border overflow-hidden transition-all duration-300',
        'bg-ai-card/80 backdrop-blur-sm',
        isWinner
          ? 'border-ai-accent winner-glow'
          : 'border-ai-border hover:border-ai-border/80',
      )}
    >
      {/* Winner badge */}
      <AnimatePresence>
        {isWinner && (
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0 }}
            className="absolute -top-1 -right-1 z-10"
          >
            <div className="bg-gradient-to-r from-yellow-400 to-amber-500 rounded-full p-2 shadow-lg">
              <Crown className="w-4 h-4 text-white" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Rank badge */}
      {rank && (
        <div className="absolute top-3 left-3 z-10">
          <div className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold',
            rank === 1 ? 'bg-yellow-500 text-black' :
            rank === 2 ? 'bg-gray-400 text-black' :
            'bg-amber-700 text-white'
          )}>
            #{rank}
          </div>
        </div>
      )}

      {/* Header */}
      <div
        className={cn(
          'p-4 cursor-pointer select-none',
          rank ? 'pl-14' : ''
        )}
        onClick={onToggleExpand}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Model icon with gradient background */}
            <div
              className={cn(
                'w-10 h-10 rounded-lg flex items-center justify-center text-xl',
                `bg-gradient-to-br ${config.gradient}`,
              )}
            >
              {config.icon}
            </div>

            <div>
              <h3 className="font-semibold text-white">{config.name}</h3>
              {votes !== undefined && (
                <p className="text-xs text-gray-400">
                  {votes} votes • Avg: {(votes / 3).toFixed(2)}
                </p>
              )}
            </div>
          </div>

          {/* Timer / Status */}
          <div className="flex items-center gap-3">
            {isLoading ? (
              <div className="flex items-center gap-2 text-ai-accent">
                <Clock className="w-4 h-4 animate-pulse" />
                <span className="font-mono text-sm">
                  <CountUp
                    start={0}
                    end={loadingTime}
                    duration={loadingTime}
                    decimals={1}
                    suffix="s"
                    preserveValue
                  />
                </span>
              </div>
            ) : response ? (
              <Sparkles className="w-4 h-4 text-green-400" />
            ) : null}

            {/* Expand/Collapse chevron */}
            <motion.div
              animate={{ rotate: isExpanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronDown className="w-5 h-5 text-gray-400" />
            </motion.div>
          </div>
        </div>

        {/* Summary (when collapsed) */}
        {!isExpanded && response && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-3 text-sm text-gray-400 line-clamp-2"
          >
            {getSummary(response)}
          </motion.p>
        )}

        {/* Loading shimmer */}
        {isLoading && (
          <div className="mt-3 space-y-2">
            <div className="h-4 bg-ai-border rounded shimmer" />
            <div className="h-4 bg-ai-border rounded w-3/4 shimmer" />
          </div>
        )}
      </div>

      {/* Expanded content */}
      <AnimatePresence>
        {isExpanded && response && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 border-t border-ai-border/50">
              <div className="pt-4 prose prose-sm prose-invert max-w-none">
                <ReactMarkdown>{response}</ReactMarkdown>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom gradient line for winner */}
      {isWinner && (
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          className={cn(
            'absolute bottom-0 left-0 right-0 h-1',
            'bg-gradient-to-r from-ai-accent via-purple-500 to-pink-500',
          )}
        />
      )}
    </motion.div>
  );
}

export default LLMCard;
