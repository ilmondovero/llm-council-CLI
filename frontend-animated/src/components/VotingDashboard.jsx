import { motion } from 'framer-motion';
import { ProgressBar, BarList } from '@tremor/react';
import { Trophy, TrendingUp, Users } from 'lucide-react';
import { cn } from '../utils/cn';

// Model colors for Tremor
const MODEL_COLORS = {
  gemini: 'blue',
  claude: 'amber',
  codex: 'emerald',
};

const MODEL_NAMES = {
  gemini: 'Gemini',
  claude: 'Claude',
  codex: 'ChatGPT',
};

/**
 * VotingDashboard Component
 * Displays real-time voting results using Tremor components
 */
export function VotingDashboard({ rankings, isVoting, totalVotes }) {
  if (!rankings || rankings.length === 0) {
    return null;
  }

  // Transform rankings for BarList
  const barListData = rankings.map((item, index) => ({
    name: MODEL_NAMES[item.model] || item.model,
    value: item.votes || 0,
    color: MODEL_COLORS[item.model] || 'indigo',
    icon: () => (
      <span className="mr-2">
        {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
      </span>
    ),
  }));

  // Calculate max votes for percentage
  const maxVotes = Math.max(...rankings.map((r) => r.votes || 0), 1);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="bg-ai-card/80 backdrop-blur-sm rounded-xl border border-ai-border p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-ai-accent/20 rounded-lg">
            <Trophy className="w-5 h-5 text-ai-accent" />
          </div>
          <div>
            <h3 className="font-semibold text-white">Council Rankings</h3>
            <p className="text-xs text-gray-400">
              {isVoting ? 'Voting in progress...' : 'Final results'}
            </p>
          </div>
        </div>

        {/* Total votes badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-ai-border/50 rounded-full">
          <Users className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-300">{totalVotes || 0} votes</span>
        </div>
      </div>

      {/* Progress bars for each model */}
      <div className="space-y-4">
        {rankings.map((item, index) => {
          const percentage = maxVotes > 0 ? ((item.votes || 0) / maxVotes) * 100 : 0;
          const isWinner = index === 0 && !isVoting;

          return (
            <motion.div
              key={item.model}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                'p-3 rounded-lg transition-all duration-300',
                isWinner ? 'bg-ai-accent/10 border border-ai-accent/30' : 'bg-ai-border/30',
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-lg">
                    {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
                  </span>
                  <span className={cn(
                    'font-medium',
                    isWinner ? 'text-ai-accent' : 'text-white',
                  )}>
                    {MODEL_NAMES[item.model] || item.model}
                  </span>
                  {isWinner && (
                    <motion.span
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="px-2 py-0.5 text-xs bg-ai-accent text-white rounded-full"
                    >
                      Winner
                    </motion.span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-400">
                    Avg: {item.avgRank?.toFixed(2) || '—'}
                  </span>
                  <span className={cn(
                    'font-mono text-sm',
                    isWinner ? 'text-ai-accent' : 'text-gray-300',
                  )}>
                    {item.votes || 0} pts
                  </span>
                </div>
              </div>

              {/* Tremor ProgressBar */}
              <ProgressBar
                value={percentage}
                color={MODEL_COLORS[item.model] || 'indigo'}
                className="mt-2"
                showAnimation={isVoting}
              />
            </motion.div>
          );
        })}
      </div>

      {/* Voting animation indicator */}
      {isVoting && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 flex items-center justify-center gap-2 text-ai-accent"
        >
          <TrendingUp className="w-4 h-4 animate-bounce" />
          <span className="text-sm">Collecting peer reviews...</span>
        </motion.div>
      )}

      {/* Summary stats */}
      {!isVoting && rankings.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-6 pt-4 border-t border-ai-border/50"
        >
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-white">
                {rankings[0]?.votes || 0}
              </p>
              <p className="text-xs text-gray-400">Top Score</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-white">
                {(rankings.reduce((acc, r) => acc + (r.votes || 0), 0) / rankings.length).toFixed(1)}
              </p>
              <p className="text-xs text-gray-400">Avg Score</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{rankings.length}</p>
              <p className="text-xs text-gray-400">Models</p>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

export default VotingDashboard;
