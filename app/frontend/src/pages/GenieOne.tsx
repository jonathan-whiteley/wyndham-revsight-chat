import { useEffect, useRef, useState } from 'react';
import { Globe, ShieldCheck } from 'lucide-react';
import { useGenieOne } from '../lib/genieOne';
import GenieOneTurn from '../components/GenieOneTurn';
import Composer from '../components/Composer';
import { apiClient } from '../lib/api';

// Starters name the configured catalog.schema so Genie One searches the right data.
const samples = (fq: string) => [
  `What was total room revenue by brand in September 2026 in ${fq}?`,
  `Which tables in ${fq} describe hotel reservations, and how big are they?`,
  `Compare September 2026 occupancy in hurricane markets vs other markets using ${fq} data`,
];

export default function GenieOne() {
  const one = useGenieOne();
  const [draft, setDraft] = useState('');
  const [schemaFqn, setSchemaFqn] = useState<string | null>(null);
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    apiClient.getConfig().then(c => setSchemaFqn(c.schema_fqn)).catch(() => setSchemaFqn(null));
  }, []);

  const lastTurn = one.turns[one.turns.length - 1];
  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [one.turns.length, lastTurn?.status, lastTurn?.activity.length, lastTurn?.answer]);

  const send = (q: string) => {
    const text = q.trim();
    if (!text || one.busy) return;
    setDraft('');
    one.ask(text);
  };

  return (
    <div className="max-w-4xl mx-auto flex flex-col min-h-[calc(100vh-7rem)]">
      <div className="flex-1 space-y-6 pb-6">
        {!one.turns.length && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-soft p-8">
            <div className="w-12 h-12 rounded-2xl wyndham-gradient flex items-center justify-center mb-4">
              <Globe className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-lg font-semibold">Ask Genie One</h2>
            <p className="text-sm text-text-secondary mt-1">Genie One searches everything you can access in Unity Catalog. No agent to pick.</p>
            <p className="text-xs text-text-tertiary mt-2 mb-5 inline-flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              Runs as you: answers respect your Unity Catalog permissions.
            </p>
            <div className="flex flex-col gap-2">
              {schemaFqn && samples(schemaFqn).map(q => (
                <button key={q} onClick={() => send(q)} className="text-left text-sm px-4 py-3 rounded-xl border border-gray-200 hover:border-wyndham-blue hover:text-wyndham-blue">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        {one.turns.map(t => (
          <GenieOneTurn key={t.id} turn={t} busy={one.busy} onRetry={() => one.retry(t.id)} />
        ))}
        <div ref={bottom} />
      </div>
      <div className="sticky bottom-4">
        <Composer
          value={draft}
          onChange={setDraft}
          onSend={() => send(draft)}
          onReset={one.turns.length && !one.busy ? one.reset : undefined}
          placeholder={one.turns.length ? 'Ask Genie One a follow-up…' : 'Ask Genie One anything about your data…'}
          disabled={one.busy}
        />
      </div>
    </div>
  );
}
