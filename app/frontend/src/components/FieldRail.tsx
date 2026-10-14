import { ChevronDown, GitBranch, Layers } from 'lucide-react';
import { Field, FieldGroup, Model, ModelKey } from '../lib/api';

interface Props {
  models: Model[];
  model: ModelKey;
  onModelChange: (m: ModelKey) => void;
  groups: FieldGroup[];
  onPick: (f: Field) => void;
}

export default function FieldRail({ models, model, onModelChange, groups, onPick }: Props) {
  const current = models.find(m => m.key === model);
  const section = (title: string, list: FieldGroup[], measure: boolean) => {
    if (list.length === 0) return null;
    // Blue for dimensions, green for measures
    const tone = measure
      ? { panel: 'bg-emerald-50 border-emerald-500/40', title: 'text-emerald-700', label: 'text-emerald-700/80', field: 'text-emerald-900', hover: 'hover:bg-emerald-100/70', dot: 'bg-emerald-500' }
      : { panel: 'bg-wyndham-blue/5 border-wyndham-blue/40', title: 'text-wyndham-blue', label: 'text-wyndham-blue/80', field: 'text-wyndham-navy', hover: 'hover:bg-wyndham-blue/10', dot: 'bg-wyndham-blue' };
    return (
      <div className={`mb-5 rounded-lg border-l-2 p-3 ${tone.panel}`}>
        <h3 className={`font-semibold text-sm mb-2 ${tone.title}`}>{title}</h3>
        {list.map(g => (
          <div key={g.label} className="mb-3 last:mb-0">
            <p className={`text-[11px] font-medium uppercase tracking-wide mb-1 ${tone.label}`}>{g.label}</p>
            <ul className="space-y-0.5">
              {g.fields.map(f => (
                <li key={f.name}>
                  <button onClick={() => onPick(f)} title={f.description} className={`w-full text-left px-2 py-1.5 rounded-lg ${tone.hover}`}>
                    <span className="flex items-center gap-1.5">
                      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${tone.dot}`} />
                      <span className={`text-sm font-medium ${tone.field}`}>{f.label}</span>
                    </span>
                    <span className="block text-[11px] text-text-tertiary leading-snug pl-3">{f.description}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-soft p-4 sticky top-24 max-h-[calc(100vh-7rem)] overflow-y-auto">
      <label className="text-[11px] font-medium text-text-tertiary uppercase tracking-wide">Genie agent</label>
      <div className="relative mt-1.5 mb-3">
        <select
          value={model}
          onChange={e => onModelChange(e.target.value as ModelKey)}
          className="w-full appearance-none rounded-xl border border-gray-200 bg-white pl-3 pr-8 py-2.5 text-sm font-medium text-text-primary focus:ring-2 focus:ring-wyndham-blue outline-none"
        >
          {models.map(m => (
            <option key={m.key} value={m.key}>
              {m.agent_name}
            </option>
          ))}
        </select>
        <ChevronDown className="w-4 h-4 text-text-secondary absolute right-2.5 top-3 pointer-events-none" />
      </div>

      {current && (
        <div className="rounded-xl bg-wyndham-blue/5 border border-wyndham-blue/10 p-3 mb-4 text-[11px]">
          <div className="flex items-center gap-1.5 font-medium text-wyndham-blue mb-1">
            <GitBranch className="w-3.5 h-3.5" />
            Governed metric view
          </div>
          <p className="text-text-secondary font-mono break-all">{current.metric_view}</p>
          <p className="text-text-tertiary mt-1">Grain: {current.grain}</p>
          <p className="text-text-secondary mt-1.5">{current.description}</p>
        </div>
      )}

      <p className="text-[11px] text-text-tertiary mb-3">Click a field to draft a question. Edit it, then press Enter.</p>
      {section('Dimensions', groups.filter(g => g.kind === 'dimension'), false)}
      {section('Measures', groups.filter(g => g.kind === 'measure'), true)}

      <div className="rounded-xl bg-surface-secondary p-3 text-[11px] text-text-secondary">
        <div className="flex items-center gap-1.5 font-medium text-text-primary mb-1">
          <Layers className="w-3.5 h-3.5 text-wyndham-blue" />
          Semantic layer
        </div>
        Measures are defined once in the Unity Catalog metric view, so every answer uses the same RevPAR.
      </div>
    </div>
  );
}
