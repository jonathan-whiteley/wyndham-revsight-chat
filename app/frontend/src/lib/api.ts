/** API client for the RevSight Chat backend. */

const API_BASE = '/api';

export type ModelKey = 'nt' | 'str';

export interface Model {
  key: ModelKey;
  label: string;
  agent_name: string;
  metric_view: string;
  grain: string;
  description: string;
  samples: string[];
  starters: { measure: string; dimension: string };
}

export interface AppConfig {
  catalog: string;
  schema: string;
  /** catalog.schema the app reads (set in config.env). */
  schema_fqn: string;
}

export interface Field {
  name: string;
  label: string;
  kind: 'dimension' | 'measure';
  followup: string;
  description: string;
}

export interface FieldGroup {
  label: string;
  kind: string;
  fields: Field[];
}

export interface Column {
  name: string;
  type: string;
}

export interface GenieMessage {
  status: string;
  /** Rows are ready but Genie is still writing its summary. */
  partial?: boolean;
  text: string;
  sql: string;
  description: string;
  columns: Column[];
  rows: Array<Array<string | null>>;
  row_count: number;
  truncated: boolean;
  suggested_questions: string[];
  statement_id: string | null;
  error: string | null;
}

export async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const apiClient = {
  getModels: (): Promise<Model[]> => fetch(`${API_BASE}/models`).then(r => json<Model[]>(r)),

  getConfig: (): Promise<AppConfig> => fetch(`${API_BASE}/config`).then(r => json<AppConfig>(r)),

  getFields: (model: ModelKey): Promise<FieldGroup[]> =>
    fetch(`${API_BASE}/fields?model=${model}`).then(r => json<{ groups: FieldGroup[] }>(r)).then(d => d.groups),

  askGenie: (model: ModelKey, question: string, conversation_id?: string) =>
    fetch(`${API_BASE}/genie/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, question, conversation_id }),
    }).then(r => json<{ model: ModelKey; conversation_id: string; message_id: string }>(r)),

  getGenieMessage: (model: ModelKey, conversation_id: string, message_id: string) =>
    fetch(`${API_BASE}/genie/message/${model}/${conversation_id}/${message_id}`).then(r => json<GenieMessage>(r)),
};
