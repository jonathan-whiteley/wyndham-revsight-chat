import { useEffect, useRef, useState } from 'react';
import { MessageSquareText, Sparkles } from 'lucide-react';
import { apiClient, Field, FieldGroup, Model, ModelKey } from '../lib/api';
import { GenieThreads } from '../lib/genie';
import FieldRail from '../components/FieldRail';
import AgentTurn from '../components/AgentTurn';
import Composer from '../components/Composer';

export interface AgentChatProps {
  model: ModelKey;
  models: Model[];
  onModelChange: (m: ModelKey) => void;
  genie: GenieThreads;
}

export default function AgentChat({ model, models, onModelChange, genie }: AgentChatProps) {
  const [groups, setGroups] = useState<FieldGroup[]>([]);
  const [drafts, setDrafts] = useState<Record<ModelKey, string>>({ nt: '', str: '' });
  const input = useRef<HTMLTextAreaElement>(null);
  const bottom = useRef<HTMLDivElement>(null);

  const current = models.find(m => m.key === model);
  const agentName = current?.agent_name || 'Genie';
  const turns = genie.threads[model].turns;
  const busy = turns.some(t => t.status === 'pending');
  const draft = drafts[model];
  const setDraft = (v: string) => setDrafts(d => ({ ...d, [model]: v }));

  useEffect(() => {
    setGroups([]);
    apiClient.getFields(model).then(setGroups).catch(() => setGroups([]));
  }, [model]);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [turns.length, turns[turns.length - 1]?.status, model]);

  const send = (q: string) => {
    const text = q.trim();
    if (!text || busy) return;
    setDraft('');
    // Keyed by the agent at ask time, so switching agents mid-question keeps the answer in this thread.
    genie.ask(model, model, text);
  };

  const pick = (f: Field) => {
    const label = f.kind === 'dimension' ? f.label.toLowerCase() : f.label;
    const template = turns.length ? f.followup : current?.starters[f.kind] ?? f.followup;
    setDraft(template.replace('{label}', label));
    input.current?.focus();
  };

  return (
    <div className="grid grid-cols-12 gap-5">
      <aside className="col-span-3">
        <FieldRail models={models} model={model} onModelChange={onModelChange} groups={groups} onPick={pick} />
      </aside>

      <section className="col-span-9 flex flex-col min-h-[calc(100vh-7rem)]">
        <div className="flex items-center gap-2 text-xs text-text-secondary px-1 mb-3">
          <MessageSquareText className="w-3.5 h-3.5 text-wyndham-blue" />
          Thread with <b className="text-text-primary">{agentName}</b>
          <span className="text-text-tertiary">· each agent keeps its own thread; switch back to resume</span>
        </div>

        <div className="flex-1 space-y-6 pb-6">
          {!turns.length && current && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-soft p-8">
              <div className="w-12 h-12 rounded-2xl wyndham-gradient flex items-center justify-center mb-4">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-lg font-semibold">Ask {agentName}</h2>
              <p className="text-sm text-text-secondary mt-1 mb-5">
                {current.description} Genie writes SQL against <span className="font-mono text-xs">{current.metric_view}</span>. Pick a field on the left to draft a question.
              </p>
              <div className="flex flex-col gap-2">
                {current.samples.map(q => (
                  <button key={q} onClick={() => send(q)} className="text-left text-sm px-4 py-3 rounded-xl border border-gray-200 hover:border-wyndham-blue hover:text-wyndham-blue">
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}
          {turns.map(t => (
            <AgentTurn key={t.id} turn={t} agentName={agentName} busy={busy} onFollowUp={send} />
          ))}
          <div ref={bottom} />
        </div>

        <div className="sticky bottom-4">
          <Composer
            ref={input}
            value={draft}
            onChange={setDraft}
            onSend={() => send(draft)}
            onReset={turns.length && !busy ? () => genie.reset(model) : undefined}
            placeholder={turns.length ? `Ask ${agentName} a follow-up…` : `Ask ${agentName} a question…`}
            disabled={busy}
          />
        </div>
      </section>
    </div>
  );
}
