"use client";

import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const ChatBot = ({ visible, setVisible, isFullView = false }) => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [streamingMessages, setStreamingMessages] = useState(new Set());
  const [predefinedQuestions, setPredefinedQuestions] = useState([
    "What does my sun sign mean?",
    "Tell me about my career prospects",
    "What are my strengths based on my chart?",
    "What challenges might I face?",
    "How can I improve my relationships?"
  ]);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const fetchNextQuestions = async (currentQuestion) => {
    try {
      const response = await axios.post('http://localhost:5000/chat/next-questions', {
        question: currentQuestion
      });
      if (response.data && response.data.questions && Array.isArray(response.data.questions) && response.data.questions.length > 0) {
        setPredefinedQuestions(response.data.questions);
      }
    } catch (error) {
      console.error('Error fetching next questions:', error);
    }
  };

  const handleAsk = async () => {
    const userInfo = JSON.parse(localStorage.getItem("astro_user_info"));
    if (!userInfo) return alert("Please generate your chart first.");

    if (!question.trim()) return;

    setMessages(prev => [...prev, { role: "user", text: question }]);
    const currentQuestion = question;
    setQuestion('');
    setIsTyping(true);

    // Fetch next questions immediately since it doesn't depend on the response
    fetchNextQuestions(currentQuestion);

    // Add a placeholder bot message for streaming
    const botMessageIndex = Date.now(); // Use timestamp as unique identifier
    setMessages(prev => [...prev, { role: "bot", text: "", id: botMessageIndex }]);
    setStreamingMessages(prev => new Set([...prev, botMessageIndex])); // Mark as streaming

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
        if (done) {
          // Final update to ensure we have the complete text
          setMessages(prev =>
            prev.map(msg =>
              msg.id === botMessageIndex
                ? { ...msg, text: accumulatedText }
                : msg
            )
          );
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (data === '[DONE]') {
              setIsTyping(false);
              // Mark streaming as complete and ensure final text is saved
              setMessages(prev =>
                prev.map(msg =>
                  msg.id === botMessageIndex
                    ? { ...msg, text: accumulatedText }
                    : msg
                )
              );
              setStreamingMessages(prev => {
                const newSet = new Set(prev);
                newSet.delete(botMessageIndex);
                return newSet;
              });
              return;
            }
            if (data) {
              accumulatedText += data;
              // Update UI more frequently for better streaming experience
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
        // Mark as not streaming
        setStreamingMessages(prev => {
          const newSet = new Set(prev);
          newSet.delete(botMessageIndex);
          return newSet;
        });
      } catch (fallbackError) {
        setMessages(prev => 
          prev.map(msg => 
            msg.id === botMessageIndex 
              ? { ...msg, text: "❌ Something went wrong!" }
              : msg
          )
        );
        // Mark as not streaming
        setStreamingMessages(prev => {
          const newSet = new Set(prev);
          newSet.delete(botMessageIndex);
          return newSet;
        });
      }
    } finally {
      setIsTyping(false);
    }
  };

  if (!visible) return null;

  // Typing animation component
  const TypingIndicator = () => (
    <div className="flex justify-start">
      <div className={`${isFullView ? 'max-w-[70%]' : 'max-w-[80%]'} px-4 py-3 rounded-lg bg-gray-800 text-white border border-gray-600`}>
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );

  const containerClass = isFullView 
    ? "w-full h-[600px] flex flex-col bg-white/5 rounded-xl border border-white/20"
    : "fixed bottom-20 right-6 w-[360px] h-[500px] bg-black/90 border border-yellow-500 rounded-xl shadow-2xl flex flex-col z-50";

  const headerClass = isFullView
    ? "p-5 border-b border-white/20 flex justify-between items-center"
    : "p-4 border-b border-yellow-400 flex justify-between items-center";

  return (
    <div className={containerClass}>
      {!isFullView && (
        <div className={headerClass}>
          <span className="text-yellow-300 font-semibold text-base">🔮 AstroBot</span>
          <button onClick={() => setVisible(false)} className="text-yellow-300 hover:text-red-400 text-lg transition-colors duration-200">&times;</button>
        </div>
      )}

      <div className={`${isFullView ? 'p-5' : 'p-4'} overflow-y-auto flex-1 space-y-3 min-h-0`}>
        {messages.length === 0 && !isTyping && (
          <div className="text-center text-gray-400 py-6">
            <div className="text-3xl mb-3">🔮</div>
            <p className="text-sm">Welcome to AstroBot! Ask me anything about your astrological chart.</p>
            <p className="text-xs mt-2 opacity-75">Try asking: "What does my sun sign mean?" or "Tell me about my career prospects"</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={msg.id || idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`${isFullView ? 'max-w-[70%]' : 'max-w-[80%]'} px-4 py-3 rounded-lg ${msg.role === 'user' ? 'bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 text-black' : 'bg-gray-800 text-white border border-gray-600'}`}>
              {msg.role === 'user' ? (
                <div className="text-black font-medium text-sm">{msg.text}</div>
              ) : (
                // Clean, elegant plain text styling
                <div className="text-white whitespace-pre-wrap leading-relaxed text-sm">
                  {msg.text}
                  {streamingMessages.has(msg.id) && (
                    <span className="inline-block w-1.5 h-3 bg-yellow-400 ml-1 animate-pulse">|</span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      <div className={`${isFullView ? 'p-5 border-t border-white/20' : 'p-4 border-t border-yellow-400'} flex-shrink-0`}>        
        {predefinedQuestions.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3 justify-center">
            {predefinedQuestions.map((q, idx) => (
              <button
                key={idx}
                className="cursor-pointer bg-transparent text-white px-3 py-1.5 rounded-lg border border-orange-500/60 hover:border-orange-400 hover:bg-orange-500/10 transition-all duration-200 text-xs transform hover:-translate-y-0.5"
                onClick={() => setQuestion(q)}
              >
                {q}
              </button>
            ))}
          </div>
        )}
        <div className="flex space-x-2">
          <input
            type="text"
            className={`flex-1 ${isFullView ? 'bg-white/10 text-white p-3' : 'bg-white/10 text-white p-3'} rounded-lg focus:ring-2 focus:ring-orange-400 border border-white/20 focus:border-orange-400 transition-all duration-200 text-sm ${isTyping ? 'opacity-50 cursor-not-allowed' : 'hover:bg-white/15'}`}
            placeholder={isTyping ? "AstroBot is typing..." : "Ask your question..."}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !isTyping && handleAsk()}
            disabled={isTyping}
          />
          <button
            onClick={handleAsk}
            disabled={isTyping || !question.trim()}
            className={`px-4 py-3 rounded-lg font-medium text-sm transition-all duration-200 ${
              isTyping || !question.trim() 
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed' 
                : 'bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 text-black hover:from-yellow-300 hover:via-pink-300 hover:to-purple-300 transform hover:-translate-y-0.5 shadow-md hover:shadow-lg'
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
