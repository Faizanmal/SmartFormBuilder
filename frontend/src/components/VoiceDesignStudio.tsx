'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Mic,
  MicOff,
  Volume2,
  Save,
  Undo,
  RefreshCw,
  MessageSquare,
  CheckCircle,
  XCircle,
} from 'lucide-react';

interface VoiceCommand {
  transcript: string;
  action: string;
  timestamp: string;
  success?: boolean;
}

interface VoiceDesignStudioProps {
  formId?: string;
  initialSchema?: Record<string, unknown>;
  onSave?: (schema: Record<string, unknown>) => void;
}

export function VoiceDesignStudio({ formId, initialSchema, onSave }: VoiceDesignStudioProps) {
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [schema, setSchema] = useState<Record<string, unknown>>(initialSchema || { fields: [] });
  const [isRecording, setIsRecording] = useState(false);
  const [commandHistory, setCommandHistory] = useState<VoiceCommand[]>([]);
  const [textCommand, setTextCommand] = useState('');
  const [processing, setProcessing] = useState(false);
  const [lastResponse, setLastResponse] = useState<string | null>(null);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  useEffect(() => {
    startSession();
    return () => {
      if (sessionToken) {
        endSession(false);
      }
    };
  }, []);

  const startSession = async () => {
    try {
      const response = await fetch('/api/v1/automation/voice/start-session/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          form_id: formId,
          initial_schema: initialSchema,
        }),
      });
      const data = await response.json();
      setSessionToken(data.session_token);
      setSchema(data.schema);
    } catch (error) {
      console.error('Failed to start voice session:', error);
    }
  };

  const endSession = async (save: boolean) => {
    if (!sessionToken) return;
    
    try {
      const response = await fetch('/api/v1/automation/voice/end-session/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_token: sessionToken,
          save_to_form: save,
        }),
      });
      const data = await response.json();
      if (save && onSave) {
        onSave(data.schema);
      }
      setSessionToken(null);
    } catch (error) {
      console.error('Failed to end session:', error);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
        await processAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    if (!sessionToken) return;
    
    setProcessing(true);
    try {
      // Convert blob to base64
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        const base64Audio = (reader.result as string).split(',')[1];
        
        const response = await fetch('/api/v1/automation/voice/process-audio/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_token: sessionToken,
            audio: base64Audio,
          }),
        });
        const data = await response.json();
        
        setSchema(data.schema);
        setLastResponse(data.response_text);
        setCommandHistory(prev => [...prev, {
          transcript: data.transcript,
          action: data.action,
          timestamp: new Date().toISOString(),
          success: data.success,
        }]);

        // Play audio response if available
        if (data.audio_response) {
          playAudioResponse(data.audio_response);
        }
        
        setProcessing(false);
      };
    } catch (error) {
      console.error('Failed to process audio:', error);
      setProcessing(false);
    }
  };

  const processTextCommand = async () => {
    if (!sessionToken || !textCommand.trim()) return;
    
    setProcessing(true);
    try {
      const response = await fetch('/api/v1/automation/voice/process-text/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_token: sessionToken,
          command: textCommand,
        }),
      });
      const data = await response.json();
      
      setSchema(data.schema);
      setLastResponse(data.response_text);
      setCommandHistory(prev => [...prev, {
        transcript: textCommand,
        action: data.action,
        timestamp: new Date().toISOString(),
        success: data.success,
      }]);
      setTextCommand('');
    } catch (error) {
      console.error('Failed to process text command:', error);
    } finally {
      setProcessing(false);
    }
  };

  const playAudioResponse = (base64Audio: string) => {
    const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);
    audio.play();
  };

  const handleSave = () => {
    endSession(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Mic className="h-6 w-6 text-primary" />
            Voice Design Studio
          </h2>
          <p className="text-muted-foreground">Create forms using voice commands</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => startSession()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Reset
          </Button>
          <Button onClick={handleSave}>
            <Save className="mr-2 h-4 w-4" />
            Save Form
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Voice Input */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Voice Input</CardTitle>
              <CardDescription>
                Click the microphone and speak your commands
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Recording Button */}
              <div className="flex flex-col items-center">
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={processing || !sessionToken}
                  className={`w-24 h-24 rounded-full flex items-center justify-center transition-all ${
                    isRecording
                      ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                      : 'bg-primary hover:bg-primary/90'
                  } ${processing ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {isRecording ? (
                    <MicOff className="h-10 w-10 text-white" />
                  ) : (
                    <Mic className="h-10 w-10 text-white" />
                  )}
                </button>
                <p className="mt-2 text-sm text-muted-foreground">
                  {isRecording ? 'Recording... Click to stop' : 'Click to start recording'}
                </p>
              </div>

              {/* Processing Indicator */}
              {processing && (
                <div className="flex items-center justify-center gap-2 text-muted-foreground">
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Processing command...
                </div>
              )}

              {/* Last Response */}
              {lastResponse && (
                <div className="p-3 bg-muted rounded-lg flex items-start gap-2">
                  <Volume2 className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                  <p className="text-sm">{lastResponse}</p>
                </div>
              )}

              {/* Text Input Alternative */}
              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground mb-2">Or type a command:</p>
                <div className="flex gap-2">
                  <Input
                    placeholder="e.g., Add an email field"
                    value={textCommand}
                    onChange={(e) => setTextCommand(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && processTextCommand()}
                  />
                  <Button onClick={processTextCommand} disabled={processing || !textCommand.trim()}>
                    <MessageSquare className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Example Commands */}
              <div className="pt-4">
                <p className="text-sm font-medium mb-2">Example commands:</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    'Add a name field',
                    'Add an email field',
                    'Make it required',
                    'Add a phone number',
                    'Delete last field',
                    'Change title to Contact Us',
                  ].map((cmd) => (
                    <button
                      key={cmd}
                      onClick={() => setTextCommand(cmd)}
                      className="text-xs px-2 py-1 bg-muted rounded hover:bg-muted/80"
                    >
                      {cmd}
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Command History */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Command History</CardTitle>
            </CardHeader>
            <CardContent>
              {commandHistory.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No commands yet. Start speaking to build your form!
                </p>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {[...commandHistory].reverse().map((cmd, index) => (
                    <div key={index} className="flex items-start gap-2 p-2 bg-muted rounded">
                      {cmd.success !== false ? (
                        <CheckCircle className="h-4 w-4 text-green-500 shrink-0 mt-0.5" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500 shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{cmd.transcript}</p>
                        <p className="text-xs text-muted-foreground">{cmd.action}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Form Preview */}
        <Card>
          <CardHeader>
            <CardTitle>Form Preview</CardTitle>
            <CardDescription>Live preview of your voice-designed form</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="border rounded-lg p-4 min-h-[400px] bg-white">
              {/* Form Title */}
              <h3 className="text-xl font-semibold mb-2">
                {(schema as any).title || 'Untitled Form'}
              </h3>
              {(schema as any).description && (
                <p className="text-muted-foreground mb-4">{(schema as any).description}</p>
              )}

              {/* Fields */}
              <div className="space-y-4">
                {((schema as any).fields || []).map((field: any, index: number) => (
                  <div key={field.id || index} className="space-y-1">
                    <label className="text-sm font-medium flex items-center gap-1">
                      {field.label}
                      {field.required && <span className="text-red-500">*</span>}
                    </label>
                    {field.type === 'textarea' ? (
                      <textarea
                        className="w-full p-2 border rounded"
                        placeholder={field.placeholder}
                        rows={3}
                        disabled
                      />
                    ) : field.type === 'select' ? (
                      <select className="w-full p-2 border rounded" disabled>
                        <option>{field.placeholder || 'Select an option'}</option>
                        {(field.options || []).map((opt: string, i: number) => (
                          <option key={i}>{opt}</option>
                        ))}
                      </select>
                    ) : field.type === 'checkbox' ? (
                      <div className="flex items-center gap-2">
                        <input type="checkbox" disabled />
                        <span className="text-sm">{field.label}</span>
                      </div>
                    ) : field.type === 'radio' ? (
                      <div className="space-y-1">
                        {(field.options || ['Option 1', 'Option 2']).map((opt: string, i: number) => (
                          <div key={i} className="flex items-center gap-2">
                            <input type="radio" name={field.id} disabled />
                            <span className="text-sm">{opt}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <input
                        type={field.type || 'text'}
                        className="w-full p-2 border rounded"
                        placeholder={field.placeholder}
                        disabled
                      />
                    )}
                    {field.help && (
                      <p className="text-xs text-muted-foreground">{field.help}</p>
                    )}
                  </div>
                ))}
              </div>

              {((schema as any).fields || []).length === 0 && (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <Mic className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">
                    Your form fields will appear here as you add them.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Try saying &quot;Add a name field&quot;
                  </p>
                </div>
              )}
            </div>

            {/* Field Count */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <span className="text-sm text-muted-foreground">
                {((schema as any).fields || []).length} field(s)
              </span>
              <Badge variant="outline">
                {sessionToken ? 'Session Active' : 'No Session'}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default VoiceDesignStudio;
