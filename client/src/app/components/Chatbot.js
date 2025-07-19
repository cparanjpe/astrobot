"use client";

import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatBot = ({ visible, setVisible, isFullView = false }) => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleAsk = async () => {
    const userInfo = JSON.parse(localStorage.getItem("astro_user_info"));
    if (!userInfo) return alert("Please generate your chart first.");

    if (!question.trim()) return;

    setMessages(prev => [...prev, { role: "user", text: question }]);
    const currentQuestion = question;
    setQuestion('');
    setIsTyping(true);

    // Add a placeholder bot message for streaming
    const botMessageIndex = Date.now(); // Use timestamp as unique identifier
    setMessages(prev => [...prev, { role: "bot", text: "", id: botMessageIndex }]);

    try {
      const response = await fetch('http://localhost:5000/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...userInfo,
          question: currentQuestion,
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              setIsTyping(false);
              return;
            }
            if (data.trim()) {
              accumulatedText += data;
              // Update the bot message with accumulated text
              setMessages(prev => 
                prev.map(msg => 
                  msg.id === botMessageIndex 
                    ? { ...msg, text: accumulatedText }
                    : msg
                )
              );
            }
          }
        }
      }
    } catch (e) {
      console.error('Streaming error:', e);
      // Fallback to regular API call
      try {
        const res = await axios.post('http://localhost:5000/chat', {
          ...userInfo,
          question: currentQuestion,
        });
        setMessages(prev => 
          prev.map(msg => 
            msg.id === botMessageIndex 
              ? { ...msg, text: res.data.response }
              : msg
          )
        );
      } catch (fallbackError) {
        setMessages(prev => 
          prev.map(msg => 
            msg.id === botMessageIndex 
              ? { ...msg, text: "❌ Something went wrong!" }
              : msg
          )
        );
      }
    } finally {
      setIsTyping(false);
    }
  };

  if (!visible) return null;

  // Typing animation component
  const TypingIndicator = () => (
    <div className="flex justify-start">
      <div className={`${isFullView ? 'max-w-[70%]' : 'max-w-[80%]'} px-4 py-3 rounded-xl bg-gray-800 text-white border border-gray-600`}>
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );

  const containerClass = isFullView 
    ? "w-full h-[600px] flex flex-col bg-white/5 rounded-2xl border border-white/20"
    : "fixed bottom-20 right-6 w-[360px] h-[500px] bg-black/90 border border-yellow-500 rounded-2xl shadow-2xl flex flex-col z-50";

  const headerClass = isFullView
    ? "p-6 border-b border-white/20 flex justify-between items-center"
    : "p-4 border-b border-yellow-400 flex justify-between items-center";

  return (
    <div className={containerClass}>
      {!isFullView && (
        <div className={headerClass}>
          <span className="text-yellow-300 font-bold text-lg">🔮 AstroBot</span>
          <button onClick={() => setVisible(false)} className="text-yellow-300 hover:text-red-400 text-xl">&times;</button>
        </div>
      )}

      <div className={`${isFullView ? 'p-6' : 'p-4'} overflow-y-auto flex-1 space-y-4 min-h-0`}>
        {messages.length === 0 && !isTyping && (
          <div className="text-center text-gray-400 py-8">
            <div className="text-4xl mb-4">🔮</div>
            <p>Welcome to AstroBot! Ask me anything about your astrological chart.</p>
            <p className="text-sm mt-2">Try asking: "What does my sun sign mean?" or "Tell me about my career prospects"</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={msg.id || idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`${isFullView ? 'max-w-[70%]' : 'max-w-[80%]'} px-6 py-4 rounded-xl ${msg.role === 'user' ? 'bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 text-black' : 'bg-gray-800 text-white border border-gray-600'}`}>
<ReactMarkdown
  remarkPlugins={[remarkGfm]}
  components={{
    p: ({ node, ...props }) => (
      <p className="mb-3 leading-relaxed" {...props} />
    ),
    ul: ({ node, ...props }) => (
      <ul className="mb-3 ml-4 space-y-1" {...props} />
    ),
    ol: ({ node, ...props }) => (
      <ol className="mb-3 ml-4 space-y-1" {...props} />
    ),
    li: ({ node, ...props }) => (
      <li className="leading-relaxed" {...props} />
    ),
    code: ({ node, ...props }) => (
      <code className="bg-gray-700 px-1 py-0.5 rounded text-sm" {...props} />
    ),
    pre: ({ node, ...props }) => (
      <pre className="bg-gray-700 p-3 rounded-lg overflow-x-auto mb-3" {...props} />
    ),
    table: ({ node, ...props }) => (
      <table className="w-full border-collapse border border-gray-600 mb-3 text-sm" {...props} />
    ),
    thead: ({ node, ...props }) => (
      <thead className="bg-gray-700" {...props} />
    ),
    tbody: ({ node, ...props }) => (
      <tbody {...props} />
    ),
    tr: ({ node, ...props }) => (
      <tr className="border-b border-gray-600" {...props} />
    ),
    th: ({ node, ...props }) => (
      <th className="border border-gray-600 px-3 py-2 text-left font-semibold" {...props} />
    ),
    td: ({ node, ...props }) => (
      <td className="border border-gray-600 px-3 py-2" {...props} />
    ),
  }}
>
  {msg.text}
</ReactMarkdown>
              
            </div>
          </div>
        ))}
        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      <div className={`${isFullView ? 'p-6 border-t border-white/20' : 'p-4 border-t border-yellow-400'} flex-shrink-0`}>
        <div className="flex space-x-2">
          <input
            type="text"
            className={`flex-1 ${isFullView ? 'bg-white/10 text-white p-4' : 'bg-white/10 text-white p-3'} rounded-xl focus:ring-2 focus:ring-yellow-400 border border-white/20 ${isTyping ? 'opacity-50 cursor-not-allowed' : ''}`}
            placeholder={isTyping ? "AstroBot is typing..." : "Ask your question..."}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !isTyping && handleAsk()}
            disabled={isTyping}
          />
          <button
            onClick={handleAsk}
            disabled={isTyping || !question.trim()}
            className={`px-6 py-3 rounded-xl font-semibold transition-all ${
              isTyping || !question.trim() 
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed' 
                : 'bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 text-black hover:scale-105'
            }`}
          >
            {isTyping ? '...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatBot;
