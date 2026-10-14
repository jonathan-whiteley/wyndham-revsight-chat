import { Globe, MessageSquareText, ShieldCheck, Sparkles } from 'lucide-react';

export type TabType = 'agent' | 'one';

interface HeaderProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

export default function Header({ activeTab, onTabChange }: HeaderProps) {
  const tabClass = (tab: TabType) => {
    const base = 'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all';
    return tab === activeTab ? `${base} bg-white text-wyndham-blue shadow-soft` : `${base} text-text-secondary hover:text-text-primary`;
  };

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-[1600px] mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <img src="/wyndham-logo.svg" alt="Wyndham" className="h-8 mix-blend-multiply" />
          <div className="h-8 w-px bg-gray-200"></div>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-wyndham-blue to-wyndham-blue-light flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <p className="font-semibold text-sm">RevSight Chat</p>
              <p className="text-xs text-text-secondary">Ask Wyndham revenue data · Powered by Genie</p>
            </div>
          </div>
        </div>

        <nav className="flex items-center bg-surface-secondary rounded-2xl p-1.5">
          <button onClick={() => onTabChange('agent')} className={tabClass('agent')}>
            <MessageSquareText className="w-4 h-4" />
            Agent Chat
          </button>
          <button onClick={() => onTabChange('one')} className={tabClass('one')}>
            <Globe className="w-4 h-4" />
            Genie One
          </button>
        </nav>

        <span className="inline-flex items-center gap-1.5 rounded-full text-xs px-3 py-1 bg-gray-100 text-gray-700">
          <ShieldCheck className="w-3.5 h-3.5" />
          Unity Catalog governed
        </span>
      </div>
    </header>
  );
}
