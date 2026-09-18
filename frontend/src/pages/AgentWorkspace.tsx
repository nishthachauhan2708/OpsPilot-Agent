import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Header } from '../components/Header';
import { ToolTracePanel } from '../components/ToolTracePanel';
import { PendingActionCard } from '../components/PendingActionCard';
import { apiService } from '../services/api';
import { ToolEvent, ActionRequest } from '../types';
import { Send, Bot, User, Sparkles, RefreshCw } from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  timestamp: string;
  toolEvents?: ToolEvent[];
  pendingAction?: ActionRequest | null;
}

interface AgentWorkspaceProps {
  onActionCreated?: () => void;
}

export const AgentWorkspace: React.FC<AgentWorkspaceProps> = ({ onActionCreated }) => {
  const [inputQuery, setInputQuery] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'agent',
      text: "Hi! I'm OpsPilot. I can help with orders, inventory, returns and daily operations.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [isThinking, setIsThinking] = useState(false);
  const [activeToolEvents, setActiveToolEvents] = useState<ToolEvent[]>([]);

  const exampleChips = [
    "Show today's delayed orders",
    "Which products are currently low on stock?",
    "Check order 1042",
    "Why is order 1042 delayed?",
    "Check order 1042 and tell me if it is eligible for a return.",
    "Create a return for order 1028 because the product arrived damaged.",
    "Give me today's operations summary"
  ];

  const handleSendMessage = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || isThinking) return;

    const userMsgId = Date.now().toString();
    const newMsg: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, newMsg]);
    setInputQuery('');
    setIsThinking(true);
    setActiveToolEvents([]);

    try {
      const response = await apiService.sendAgentMessage(textToSend);
      
      const agentMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: response.message,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        toolEvents: response.tool_events,
        pendingAction: response.pending_action,
      };

      setMessages((prev) => [...prev, agentMsg]);
      setActiveToolEvents(response.tool_events || []);
      if (response.pending_action && onActionCreated) {
        onActionCreated();
      }
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: "I couldn't load the order data right now. Please try again.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-[#0b0f19] text-[#f3f4f6]">
      <Header title="Agent Workspace" subtitle="Business operations assistant — Ask about orders, inventory, returns or daily operations" />

      <div className="flex-1 flex overflow-hidden">
        {/* CENTER: Chat Interface */}
        <div className="flex-1 flex flex-col h-full overflow-hidden border-r border-[#263244]">
          {/* Messages Stream */}
          <div className="flex-1 overflow-y-auto p-6 space-y-5">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'agent' && (
                  <div className="w-8 h-8 rounded-lg bg-[#38bdf8]/10 border border-[#38bdf8]/20 text-[#38bdf8] flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div className={`max-w-2xl space-y-2.5 ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                  <div
                    className={`p-3.5 rounded-xl text-xs sm:text-sm leading-relaxed ${
                      msg.sender === 'user'
                        ? 'bg-[#0284c7] text-white font-medium rounded-tr-none shadow-sm'
                        : 'bg-[#111827] border border-[#263244] text-[#f3f4f6] rounded-tl-none'
                    }`}
                  >
                    {msg.sender === 'agent' ? (
                      <div className="markdown-content">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{ img: () => null }}
                        >
                          {msg.text}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      msg.text
                    )}
                  </div>

                  {/* Render Pending Action Card inside agent response if present */}
                  {msg.pendingAction && (
                    <PendingActionCard
                      action={msg.pendingAction}
                      onActionComplete={() => {
                        if (onActionCreated) onActionCreated();
                      }}
                    />
                  )}

                  <div className="text-[10px] text-[#94a3b8] px-1">{msg.timestamp}</div>
                </div>

                {msg.sender === 'user' && (
                  <div className="w-8 h-8 rounded-lg bg-[#151d2d] border border-[#263244] text-slate-300 flex items-center justify-center shrink-0 mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}

            {isThinking && (
              <div className="flex gap-3 items-center">
                <div className="w-8 h-8 rounded-lg bg-[#38bdf8]/10 border border-[#38bdf8]/20 text-[#38bdf8] flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 animate-spin" />
                </div>
                <div className="p-2.5 bg-[#111827] border border-[#263244] rounded-xl text-xs text-[#38bdf8] flex items-center gap-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Checking order data...</span>
                </div>
              </div>
            )}
          </div>

          {/* Example Query Chips & Input Footer */}
          <div className="p-4 bg-[#111827] border-t border-[#263244] space-y-3">
            <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none text-xs">
              <span className="text-[#94a3b8] font-medium text-[11px] shrink-0 flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-[#38bdf8]" /> Quick queries:
              </span>
              {exampleChips.map((chip, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(chip)}
                  disabled={isThinking}
                  className="bg-[#0b0f19] hover:bg-[#151d2d] text-slate-300 hover:text-white border border-[#263244] px-2.5 py-1 rounded-full whitespace-nowrap text-[11px] transition-colors disabled:opacity-50"
                >
                  {chip}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <input
                type="text"
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask OpsPilot about orders, inventory, returns or operations..."
                disabled={isThinking}
                className="flex-1 bg-[#0b0f19] border border-[#263244] rounded-lg px-4 py-2.5 text-xs sm:text-sm text-[#f3f4f6] placeholder-[#94a3b8] focus:outline-none focus:border-[#38bdf8] transition-colors disabled:opacity-50"
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={isThinking || !inputQuery.trim()}
                className="bg-[#0284c7] hover:bg-[#0369a1] text-white font-medium px-4 py-2.5 rounded-lg flex items-center gap-2 text-xs transition-colors disabled:opacity-50 shadow-sm"
              >
                <span>Send</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT: Agent Activity & Tool Trace Panel */}
        <div className="w-80 bg-[#111827]/40 p-4 hidden lg:block overflow-y-auto">
          <ToolTracePanel toolEvents={activeToolEvents} isThinking={isThinking} />
        </div>
      </div>
    </div>
  );
};
