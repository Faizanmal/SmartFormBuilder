/**
 * AI Chatbot Assistant for Form Building
 * Provides intelligent help, suggestions, and form creation assistance
 */
'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  MessageCircle,
  Send,
  X,
  Minimize2,
  Maximize2,
  Bot,
  User,
  Sparkles,
  Lightbulb,
  FileQuestion,
  Wand2,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  ChevronDown,
  Mic,
  MicOff,
  Volume2,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Speech Recognition types
interface SpeechRecognitionEvent {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
        confidence: number;
      };
      isFinal: boolean;
    };
    length: number;
  };
}

interface ISpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: (event: SpeechRecognitionEvent) => void;
  onend: () => void;
  onerror: (event: { error: string }) => void;
}

type SpeechRecognitionConstructor = new () => ISpeechRecognition;

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  suggestions?: string[];
  actions?: Array<{
    label: string;
    action: string;
    payload?: Record<string, unknown>;
  }>;
  feedback?: 'positive' | 'negative' | null;
}

interface ChatbotProps {
  formId?: string;
  onSuggestionApply?: (suggestion: Record<string, unknown>) => void;
  onFieldAdd?: (field: Record<string, unknown>) => void;
  className?: string;
}

// Quick suggestions for common tasks
const QUICK_SUGGESTIONS = [
  { icon: <Wand2 className="h-4 w-4" />, text: 'Generate a contact form', category: 'create' },
  { icon: <Lightbulb className="h-4 w-4" />, text: 'Suggest improvements', category: 'optimize' },
  { icon: <FileQuestion className="h-4 w-4" />, text: 'How to add conditional logic?', category: 'help' },
  { icon: <Sparkles className="h-4 w-4" />, text: 'Make form more engaging', category: 'enhance' },
];

export function FormAssistantChatbot({
  formId,
  onSuggestionApply,
  onFieldAdd,
  className,
}: ChatbotProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm your AI form assistant. 👋 I can help you create forms, suggest improvements, answer questions, and more. What would you like to do today?",
      timestamp: new Date(),
      suggestions: [
        'Create a new form',
        'Improve my current form',
        'Learn about features',
        'Get field suggestions',
      ],
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<ISpeechRecognition | null>(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Update unread count when minimized
  useEffect(() => {
    if (!isOpen || isMinimized) {
      const newMessages = messages.filter(
        m => m.role === 'assistant' && new Date(m.timestamp) > new Date(Date.now() - 60000)
      );
      if (newMessages.length > 0) {
        setUnreadCount(newMessages.length);
      }
    } else {
      setUnreadCount(0);
    }
  }, [messages, isOpen, isMinimized]);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition() as ISpeechRecognition;
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      
      recognitionRef.current.onresult = (event: SpeechRecognitionEvent) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(transcript);
        setIsListening(false);
      };
      
      recognitionRef.current.onerror = () => {
        setIsListening(false);
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  // Generate unique ID
  const generateId = () => Math.random().toString(36).substring(7);

  // Handle sending message
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Simulate API call to AI service
      const response = await fetch('/api/v1/ai/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content,
          form_id: formId,
          conversation_history: messages.slice(-10).map(m => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        const assistantMessage: Message = {
          id: generateId(),
          role: 'assistant',
          content: data.response || getLocalResponse(content),
          timestamp: new Date(),
          suggestions: data.suggestions,
          actions: data.actions,
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Fallback to local responses
        const assistantMessage: Message = {
          id: generateId(),
          role: 'assistant',
          content: getLocalResponse(content),
          timestamp: new Date(),
          suggestions: getLocalSuggestions(content),
        };

        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      // Fallback to local responses
      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: getLocalResponse(content),
        timestamp: new Date(),
        suggestions: getLocalSuggestions(content),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [formId, messages]);

  // Local response generation (fallback)
  const getLocalResponse = (input: string): string => {
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('create') && lowerInput.includes('form')) {
      return "I'd be happy to help you create a form! Here are some popular form types I can generate:\n\n• **Contact Form** - Name, email, message\n• **Registration Form** - Full user signup\n• **Survey Form** - Multiple choice questions\n• **Feedback Form** - Ratings and comments\n\nJust tell me which type you'd like, or describe the form you need!";
    }
    
    if (lowerInput.includes('contact')) {
      return "Great choice! A contact form typically includes:\n\n✅ Name field (required)\n✅ Email field (required, validated)\n✅ Phone field (optional)\n✅ Subject dropdown\n✅ Message textarea\n\nWould you like me to create this form for you?";
    }
    
    if (lowerInput.includes('improve') || lowerInput.includes('optimize')) {
      return "Here are some ways to improve your form's performance:\n\n🎯 **Reduce Fields** - Only ask for essential information\n🎨 **Visual Hierarchy** - Use headings and spacing\n📱 **Mobile Friendly** - Ensure touch-friendly inputs\n✨ **Progressive Disclosure** - Use multi-step for long forms\n🔄 **Smart Defaults** - Pre-fill when possible\n\nWould you like me to analyze your current form?";
    }
    
    if (lowerInput.includes('conditional') || lowerInput.includes('logic')) {
      return "Conditional logic allows fields to show/hide based on user responses! Here's how to use it:\n\n1. Select a field you want to conditionally display\n2. Click 'Add Condition' in field settings\n3. Choose the trigger field and condition\n4. Save your changes\n\n**Example:** Show 'Company Name' only when 'Are you a business?' is 'Yes'\n\nNeed help setting up a specific condition?";
    }
    
    if (lowerInput.includes('help') || lowerInput.includes('how')) {
      return "I'm here to help! Here are things I can assist with:\n\n📝 **Form Creation** - Generate forms from descriptions\n🔧 **Field Configuration** - Set up validations, options\n💡 **Best Practices** - Improve conversion rates\n🎨 **Design Tips** - Make forms more engaging\n🔄 **Integrations** - Connect with other tools\n\nWhat would you like to know more about?";
    }
    
    if (lowerInput.includes('field') && (lowerInput.includes('add') || lowerInput.includes('suggest'))) {
      return "Based on common form patterns, here are field suggestions:\n\n**For Contact Forms:**\n• Email (required)\n• Phone (with country code)\n• Preferred contact method (radio)\n\n**For Registration:**\n• Password (with confirmation)\n• Date of birth (date picker)\n• Terms agreement (checkbox)\n\nTell me more about your form and I'll give specific suggestions!";
    }
    
    return "I understand you're looking for help with your form. Could you be more specific about what you'd like to do? I can help with:\n\n• Creating new forms\n• Adding or configuring fields\n• Setting up conditional logic\n• Improving form performance\n• Answering questions about features\n\nJust ask!";
  };

  // Local suggestions based on input
  const getLocalSuggestions = (input: string): string[] => {
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('form')) {
      return ['Create a contact form', 'Create a survey', 'Create a registration form'];
    }
    
    if (lowerInput.includes('field')) {
      return ['Add email field', 'Add phone field', 'Add dropdown'];
    }
    
    return ['Show me examples', 'How does this work?', 'What else can you do?'];
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  // Handle action click
  const handleActionClick = (action: { action: string; payload?: Record<string, unknown> }) => {
    switch (action.action) {
      case 'add_field':
        onFieldAdd?.(action.payload || {});
        break;
      case 'apply_suggestion':
        onSuggestionApply?.(action.payload || {});
        break;
      default:
        sendMessage(action.action);
    }
  };

  // Handle feedback
  const handleFeedback = (messageId: string, feedback: 'positive' | 'negative') => {
    setMessages(prev => prev.map(m => 
      m.id === messageId ? { ...m, feedback } : m
    ));
    
    // Could send feedback to API here
  };

  // Toggle voice input
  const toggleVoiceInput = () => {
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      recognitionRef.current?.start();
      setIsListening(true);
    }
  };

  // Copy message content
  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  // Regenerate last response
  const regenerateResponse = () => {
    const lastUserMessage = [...messages].reverse().find(m => m.role === 'user');
    if (lastUserMessage) {
      // Remove last assistant message
      setMessages(prev => prev.slice(0, -1));
      sendMessage(lastUserMessage.content);
    }
  };

  if (!isOpen) {
    return (
      <Button
        onClick={() => setIsOpen(true)}
        className={cn(
          'fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg z-50',
          'bg-gradient-to-br from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90',
          className
        )}
      >
        <MessageCircle className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </Button>
    );
  }

  return (
    <Card className={cn(
      'fixed bottom-6 right-6 z-50 shadow-2xl transition-all duration-300',
      isMinimized ? 'w-80 h-14' : 'w-96 h-[600px]',
      className
    )}>
      {/* Header */}
      <CardHeader className="p-3 border-b flex flex-row items-center justify-between space-y-0">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div>
            <CardTitle className="text-sm">Form Assistant</CardTitle>
            {!isMinimized && (
              <p className="text-xs text-muted-foreground flex items-center gap-1">
                <span className="h-2 w-2 rounded-full bg-green-500"></span>
                Online
              </p>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => setIsMinimized(!isMinimized)}
          >
            {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => setIsOpen(false)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>

      {!isMinimized && (
        <>
          {/* Messages */}
          <ScrollArea className="flex-1 h-[calc(600px-130px)] p-4" ref={scrollAreaRef}>
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex gap-2',
                    message.role === 'user' && 'flex-row-reverse'
                  )}
                >
                  <Avatar className="h-8 w-8 shrink-0">
                    <AvatarFallback className={cn(
                      message.role === 'assistant' 
                        ? 'bg-gradient-to-br from-primary to-purple-600 text-white' 
                        : 'bg-muted'
                    )}>
                      {message.role === 'assistant' ? (
                        <Bot className="h-4 w-4" />
                      ) : (
                        <User className="h-4 w-4" />
                      )}
                    </AvatarFallback>
                  </Avatar>

                  <div className={cn(
                    'max-w-[80%] space-y-2',
                    message.role === 'user' && 'text-right'
                  )}>
                    <div className={cn(
                      'rounded-lg px-3 py-2 text-sm',
                      message.role === 'assistant' 
                        ? 'bg-muted' 
                        : 'bg-primary text-primary-foreground'
                    )}>
                      <div className="whitespace-pre-wrap">{message.content}</div>
                    </div>

                    {/* Suggestions */}
                    {message.suggestions && message.suggestions.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {message.suggestions.map((suggestion, index) => (
                          <Button
                            key={index}
                            variant="outline"
                            size="sm"
                            className="text-xs h-7"
                            onClick={() => handleSuggestionClick(suggestion)}
                          >
                            {suggestion}
                          </Button>
                        ))}
                      </div>
                    )}

                    {/* Actions */}
                    {message.actions && message.actions.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {message.actions.map((action, index) => (
                          <Button
                            key={index}
                            size="sm"
                            className="text-xs h-7"
                            onClick={() => handleActionClick(action)}
                          >
                            <Sparkles className="h-3 w-3 mr-1" />
                            {action.label}
                          </Button>
                        ))}
                      </div>
                    )}

                    {/* Message Actions */}
                    {message.role === 'assistant' && (
                      <div className="flex items-center gap-1 opacity-0 hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={() => copyMessage(message.content)}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className={cn('h-6 w-6', message.feedback === 'positive' && 'text-green-500')}
                          onClick={() => handleFeedback(message.id, 'positive')}
                        >
                          <ThumbsUp className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className={cn('h-6 w-6', message.feedback === 'negative' && 'text-red-500')}
                          onClick={() => handleFeedback(message.id, 'negative')}
                        >
                          <ThumbsDown className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Typing Indicator */}
              {isTyping && (
                <div className="flex gap-2">
                  <Avatar className="h-8 w-8 shrink-0">
                    <AvatarFallback className="bg-gradient-to-br from-primary to-purple-600 text-white">
                      <Bot className="h-4 w-4" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="bg-muted rounded-lg px-4 py-3">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Quick Suggestions */}
          {messages.length === 1 && (
            <div className="px-4 py-2 border-t">
              <p className="text-xs text-muted-foreground mb-2">Quick actions:</p>
              <div className="flex flex-wrap gap-1">
                {QUICK_SUGGESTIONS.map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="text-xs h-7 gap-1"
                    onClick={() => sendMessage(suggestion.text)}
                  >
                    {suggestion.icon}
                    {suggestion.text}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <CardContent className="p-3 border-t">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage(inputValue);
              }}
              className="flex gap-2"
            >
              <div className="flex-1 relative">
                <Input
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Ask me anything..."
                  className="pr-10"
                  disabled={isTyping}
                />
                {recognitionRef.current && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className={cn(
                      'absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7',
                      isListening && 'text-red-500'
                    )}
                    onClick={toggleVoiceInput}
                  >
                    {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  </Button>
                )}
              </div>
              <Button type="submit" size="icon" disabled={!inputValue.trim() || isTyping}>
                <Send className="h-4 w-4" />
              </Button>
            </form>
            
            {/* Regenerate button */}
            {messages.length > 1 && (
              <div className="flex justify-center mt-2">
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-xs gap-1"
                  onClick={regenerateResponse}
                  disabled={isTyping}
                >
                  <RefreshCw className="h-3 w-3" />
                  Regenerate response
                </Button>
              </div>
            )}
          </CardContent>
        </>
      )}
    </Card>
  );
}

export default FormAssistantChatbot;
