import { AlertTriangle, Loader2, Sparkles } from 'lucide-react';
import { Turn } from '../lib/genie';
import Markdown from './Markdown';
import QueryResult from './QueryResult';

const PHASES: Record<string, string> = {
  FILTERING_CONTEXT: 'Reading the metric view',
  ASKING_AI: 'Writing SQL',
  PENDING_WAREHOUSE: 'Waking the warehouse',
  EXECUTING_QUERY: 'Running the query',
};

interface Props {
  turn: Turn;
  agentName: string;
  busy: boolean;
  onFollowUp: (q: string) => void;
}

export default function AgentTurn({ turn, agentName, busy, onFollowUp }: Props) {
  const r = turn.result;
  return (
    <div className="space-y-3">
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-br-md bg-wyndham-blue text-white px-4 py-2.5 text-sm">{turn.question}</div>
      </div>
      <div className="bg-white rounded-2xl border border-gray-100 shadow-soft p-5 space-y-4">
        <div className="flex items-center gap-2 text-xs font-medium text-wyndham-blue">
          <Sparkles className="w-3.5 h-3.5" />
          {agentName}
          {turn.elapsedMs ? <span className="text-text-tertiary font-normal">· {(turn.elapsedMs / 1000).toFixed(1)}s</span> : null}
        </div>

        {turn.status === 'pending' && (
          <div className="flex items-center gap-3 text-sm text-wyndham-blue">
            <Loader2 className="w-4 h-4 animate-spin" />
            {PHASES[turn.phase || ''] || 'Thinking'}…
          </div>
        )}

        {turn.status === 'error' && (
          <div className="flex items-start gap-3 rounded-xl bg-red-50 border border-red-100 p-4 text-sm text-red-700">
            <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
            <div>
              <p className="font-medium">Genie could not answer this</p>
              <p className="mt-1">{turn.error}</p>
            </div>
          </div>
        )}

        {r && turn.status === 'done' && (
          <>
            {r.text && <Markdown text={r.text} />}
            {r.columns.length > 0 && (
              <QueryResult columns={r.columns} rows={r.rows} rowCount={r.row_count} truncated={r.truncated} sql={r.sql} sqlLabel="Generated SQL (governed metric view)" />
            )}
            {r.suggested_questions.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {r.suggested_questions.slice(0, 3).map(q => (
                  <button
                    key={q}
                    disabled={busy}
                    onClick={() => onFollowUp(q)}
                    className="text-xs px-3 py-1.5 rounded-full border border-gray-200 text-text-secondary hover:border-wyndham-blue hover:text-wyndham-blue text-left disabled:opacity-50"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
