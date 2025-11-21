'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Mic, MicOff, Send, Volume2, VolumeX } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  type: 'bot' | 'user';
  content: string;
  timestamp: Date;
}

interface ConversationalFormProps {
  formId: string;
  onComplete?: (data: any) => void;
  enableVoice?: boolean;
  className?: string;
}

export function ConversationalForm({
  formId,
  onComplete,
  enableVoice = false,
  className,
}: ConversationalFormProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    startConversation();
  }, [formId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startConversation = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/advanced/conversational/start_conversation/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_id: formId }),
      });

      const data = await response.json();
      setSessionToken(data.session_token);

      // Add bot's first question
      addMessage('bot', data.question.question);
      
      // Speak if voice enabled
      if (enableVoice) {
        speakText(data.question.question);
      }
    } catch (error) {
      console.error('Failed to start conversation:', error);
      addMessage('bot', 'Sorry, there was an error starting the form. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const addMessage = (type: 'bot' | 'user', content: string) => {
    setMessages((prev) => [...prev, { type, content, timestamp: new Date() }]);
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!currentInput.trim() || !sessionToken || isLoading) return;

    const userMessage = currentInput;
    addMessage('user', userMessage);
    setCurrentInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/advanced/conversational/respond/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_token: sessionToken,
          response: userMessage,
        }),
      });

      const data = await response.json();

      if (data.complete) {
        // Form complete
        addMessage('bot', data.summary);
        setIsComplete(true);
        setProgress(100);
        
        if (enableVoice) {
          speakText(data.summary);
        }
        
        onComplete?.(data.collected_data);
      } else if (data.error) {
        // Validation error
        addMessage('bot', data.error);
        
        if (enableVoice) {
          speakText(data.error);
        }
      } else {
        // Next question
        addMessage('bot', data.question.question);
        setProgress(data.progress * 100);
        
        if (enableVoice) {
          speakText(data.question.question);
        }
      }
    } catch (error) {
      console.error('Failed to submit response:', error);
      addMessage('bot', 'Sorry, there was an error processing your response. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('Voice input is not supported in your browser');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await processVoiceInput(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Failed to access microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processVoiceInput = async (audioBlob: Blob) => {
    setIsLoading(true);
    try {
      // Convert blob to base64
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      
      reader.onloadend = async () => {
        const base64Audio = reader.result as string;
        
        const response = await fetch('/api/advanced/conversational/voice_input/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_token: sessionToken,
            audio_data: base64Audio,
            audio_format: 'webm',
          }),
        });

        const data = await response.json();

        if (data.transcription) {
          // Show what was heard
          addMessage('user', `🎤 ${data.transcription}`);
        }

        // Process like regular text input
        if (data.complete) {
          addMessage('bot', data.summary);
          setIsComplete(true);
          setProgress(100);
          onComplete?.(data.collected_data);
        } else if (data.error) {
          addMessage('bot', data.error);
        } else if (data.question) {
          addMessage('bot', data.question.question);
          setProgress(data.progress * 100);
          
          if (enableVoice) {
            speakText(data.question.question);
          }
        }
      };
    } catch (error) {
      console.error('Failed to process voice input:', error);
      addMessage('bot', 'Sorry, I couldn\'t understand that. Please try typing or speaking again.');
    } finally {
      setIsLoading(false);
    }
  };

  const speakText = async (text: string) => {
    if (!enableVoice || isSpeaking) return;

    setIsSpeaking(true);
    try {
      const response = await fetch('/api/advanced/conversational/text_to_speech/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, voice: 'nova' }),
      });

      const data = await response.json();
      
      if (data.audio_data) {
        const audio = new Audio(data.audio_data);
        audio.onended = () => setIsSpeaking(false);
        await audio.play();
      } else {
        setIsSpeaking(false);
      }
    } catch (error) {
      console.error('Text-to-speech failed:', error);
      setIsSpeaking(false);
    }
  };

  const toggleSpeech = () => {
    setIsSpeaking((prev) => !prev);
  };

  return (
    <Card className={cn('w-full max-w-2xl mx-auto', className)}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Chat Form</span>
          <div className="flex items-center gap-2">
            {enableVoice && (
              <Button
                size="sm"
                variant="ghost"
                onClick={toggleSpeech}
              >
                {isSpeaking ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
              </Button>
            )}
            <div className="text-sm text-muted-foreground">
              {Math.round(progress)}% complete
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progress Bar */}
        <div className="w-full bg-secondary rounded-full h-2">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Messages */}
        <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
          {messages.map((message, index) => (
            <div
              key={index}
              className={cn(
                'flex gap-3',
                message.type === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              {message.type === 'bot' && (
                <Avatar className="h-8 w-8">
                  <AvatarFallback>🤖</AvatarFallback>
                </Avatar>
              )}
              <div
                className={cn(
                  'rounded-lg px-4 py-2 max-w-[80%]',
                  message.type === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                )}
              >
                <p className="text-sm">{message.content}</p>
                <span className="text-xs opacity-70 mt-1 block">
                  {message.timestamp.toLocaleTimeString()}
                </span>
              </div>
              {message.type === 'user' && (
                <Avatar className="h-8 w-8">
                  <AvatarFallback>👤</AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-3">
              <Avatar className="h-8 w-8">
                <AvatarFallback>🤖</AvatarFallback>
              </Avatar>
              <div className="bg-muted rounded-lg px-4 py-2">
                <div className="flex gap-1">
                  <span className="animate-bounce">●</span>
                  <span className="animate-bounce delay-100">●</span>
                  <span className="animate-bounce delay-200">●</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        {!isComplete && (
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              placeholder="Type your answer..."
              disabled={isLoading || isRecording}
              className="flex-1"
            />
            {enableVoice && (
              <Button
                type="button"
                variant={isRecording ? 'destructive' : 'outline'}
                size="icon"
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isLoading}
              >
                {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              </Button>
            )}
            <Button type="submit" size="icon" disabled={isLoading || isRecording || !currentInput.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        )}

        {isComplete && (
          <div className="text-center py-4">
            <p className="text-lg font-semibold text-green-600">✅ Form Complete!</p>
            <p className="text-sm text-muted-foreground mt-2">
              Thank you for your responses.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
