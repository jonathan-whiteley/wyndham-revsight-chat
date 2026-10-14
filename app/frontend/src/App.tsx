import { useCallback, useEffect, useState } from 'react';
import './index.css';
import { apiClient, Model, ModelKey } from './lib/api';
import { useGenieThreads } from './lib/genie';
import Header, { TabType } from './components/Header';
import AgentChat from './pages/AgentChat';
import GenieOne from './pages/GenieOne';

const AGENT_KEY = 'revsight-chat-agent';

function initialTab(): TabType {
  return new URLSearchParams(window.location.search).get('tab') === 'one' ? 'one' : 'agent';
}

function initialAgent(): ModelKey {
  const p = new URLSearchParams(window.location.search).get('agent');
  if (p === 'nt' || p === 'str') return p;
  return localStorage.getItem(AGENT_KEY) === 'str' ? 'str' : 'nt';
}

function setParam(key: string, value: string) {
  const params = new URLSearchParams(window.location.search);
  params.set(key, value);
  window.history.replaceState({}, '', `?${params.toString()}`);
}

function App() {
  const [tab, setTab] = useState<TabType>(initialTab);
  const [agent, setAgent] = useState<ModelKey>(initialAgent);
  const [models, setModels] = useState<Model[]>([]);
  const genie = useGenieThreads();

  useEffect(() => {
    apiClient.getModels().then(setModels).catch(() => setModels([]));
  }, []);

  const changeTab = (t: TabType) => {
    setTab(t);
    setParam('tab', t);
  };

  const changeAgent = useCallback((m: ModelKey) => {
    setAgent(m);
    localStorage.setItem(AGENT_KEY, m);
    setParam('agent', m);
  }, []);

  return (
    <div className="min-h-screen bg-surface-secondary">
      <Header activeTab={tab} onTabChange={changeTab} />
      <main className="max-w-[1600px] mx-auto px-6 py-6">
        {/* Both tabs stay mounted so threads survive tab switches */}
        <div className={tab === 'agent' ? '' : 'hidden'}>
          <AgentChat model={agent} models={models} onModelChange={changeAgent} genie={genie} />
        </div>
        <div className={tab === 'one' ? '' : 'hidden'}>
          <GenieOne />
        </div>
      </main>
    </div>
  );
}

export default App;
