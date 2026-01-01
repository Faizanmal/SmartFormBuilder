'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Save,
  Undo,
  Redo,
  RefreshCw,
  MessageSquare,
  CheckCircle,
  XCircle,
  Sparkles,
  Wand2,
  History,
  Settings2,
  Keyboard,
  Zap,
} from 'lucide-react';
import { feedback, speak, stopSpeaking, type SoundType } from '@/lib/audio-feedback';
import { cn } from '@/lib/utils';

interface VoiceCommand {
  transcript: string;
  action: string;
  timestamp: string;
  success?: boolean;
}

interface UndoState {
  schema: Record<string, unknown>;
  timestamp: string;
}

interface VoiceDesignStudioProps {
  formId?: string;
  initialSchema?: Record<string, unknown>;
  onSave?: (schema: Record<string, unknown>) => void;
}

// Animation keyframes as CSS-in-JS
const pulseAnimation = `
  @keyframes pulse-ring {
    0% { transform: scale(0.8); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.5; }
    100% { transform: scale(0.8); opacity: 1; }
  }
  @keyframes field-appear {
    0% { opacity: 0; transform: translateY(-10px); }
    100% { opacity: 1; transform: translateY(0); }
  }
  @keyframes success-flash {
    0%, 100% { background-color: transparent; }
    50% { background-color: rgba(34, 197, 94, 0.2); }
  }
  @keyframes waveform {
    0%, 100% { height: 4px; }
    50% { height: 20px; }
  }
`;

export function VoiceDesignStudio({ formId, initialSchema, onSave }: VoiceDesignStudioProps) {
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [schema, setSchema] = useState<Record<string, unknown>>(initialSchema || { fields: [] });
  const [isRecording, setIsRecording] = useState(false);
  const [commandHistory, setCommandHistory] = useState<VoiceCommand[]>([]);
  const [textCommand, setTextCommand] = useState('');
  const [processing, setProcessing] = useState(false);
  const [lastResponse, setLastResponse] = useState<string | null>(null);
  
  // Enhanced features state
  const [audioLevel, setAudioLevel] = useState(0);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [speechEnabled, setSpeechEnabled] = useState(true);
  const [undoStack, setUndoStack] = useState<UndoState[]>([]);
  const [redoStack, setRedoStack] = useState<UndoState[]>([]);
  const [showSettings, setShowSettings] = useState(false);
  const [lastAddedFieldId, setLastAddedFieldId] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showKeyboardShortcuts, setShowKeyboardShortcuts] = useState(false);
  
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Play feedback with settings check
  const playFeedback = useCallback((type: SoundType) => {
    if (soundEnabled) {
      feedback(type, true);
    }
  }, [soundEnabled]);

  // Text-to-speech with settings check
  const speakText = useCallback((text: string) => {
    if (speechEnabled) {
      speak(text, { rate: 1.1 });
    }
  }, [speechEnabled]);

  // Push to undo stack
  const pushUndo = useCallback(() => {
    setUndoStack(prev => [...prev.slice(-19), { schema, timestamp: new Date().toISOString() }]);
    setRedoStack([]);
  }, [schema]);

  // Undo action
  const handleUndo = useCallback(() => {
    if (undoStack.length === 0) return;
    
    const lastState = undoStack[undoStack.length - 1];
    setRedoStack(prev => [...prev, { schema, timestamp: new Date().toISOString() }]);
    setUndoStack(prev => prev.slice(0, -1));
    setSchema(lastState.schema);
    playFeedback('click');
  }, [undoStack, schema, playFeedback]);

  // Redo action
  const handleRedo = useCallback(() => {
    if (redoStack.length === 0) return;
    
    const nextState = redoStack[redoStack.length - 1];
    setUndoStack(prev => [...prev, { schema, timestamp: new Date().toISOString() }]);
    setRedoStack(prev => prev.slice(0, -1));
    setSchema(nextState.schema);
    playFeedback('click');
  }, [redoStack, schema, playFeedback]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + Z for undo
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        handleUndo();
      }
      // Ctrl/Cmd + Shift + Z or Ctrl/Cmd + Y for redo
      if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
        e.preventDefault();
        handleRedo();
      }
      // Space to toggle recording (when not typing)
      if (e.code === 'Space' && document.activeElement?.tagName !== 'INPUT') {
        e.preventDefault();
        if (isRecording) {
          stopRecording();
        } else {
          startRecording();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleUndo, handleRedo, isRecording]);

  // Start session useEffect moved below to avoid using functions before declaration

  const startSession = useCallback(async () => {
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
  }, [formId, initialSchema]);

  const endSession = useCallback(async (save: boolean) => {
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
  }, [sessionToken, onSave]);

  // Initialize session when component mounts (placed after function declarations)
  useEffect(() => {
    startSession();
    return () => {
      if (sessionToken) {
        endSession(false);
      }
    };
  }, [startSession, endSession, sessionToken]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Setup audio analyser for visual feedback
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;
      
      // Animate audio level
      const updateLevel = () => {
        if (!analyserRef.current) return;
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        setAudioLevel(average / 255 * 100);
        animationFrameRef.current = requestAnimationFrame(updateLevel);
      };
      updateLevel();
      
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = async () => {
        // Clean up audio analyser
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }
        analyserRef.current = null;
        setAudioLevel(0);
        
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
        await processAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
        audioContext.close();
      };

      mediaRecorder.current.start();
      setIsRecording(true);
      playFeedback('start');
    } catch (error) {
      console.error('Failed to start recording:', error);
      playFeedback('error');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
      playFeedback('stop');
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    if (!sessionToken) return;
    
    pushUndo(); // Save state before processing
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
        
        // Track new field for animation
        const oldFields = (schema as { fields?: { id: string }[] }).fields || [];
        const newFields = (data.schema as { fields?: { id: string }[] }).fields || [];
        if (newFields.length > oldFields.length) {
          setLastAddedFieldId(newFields[newFields.length - 1]?.id || null);
          setTimeout(() => setLastAddedFieldId(null), 1000);
        }
        
        setSchema(data.schema);
        setLastResponse(data.response_text);
        setCommandHistory(prev => [...prev, {
          transcript: data.transcript,
          action: data.action,
          timestamp: new Date().toISOString(),
          success: data.success,
        }]);
        
        // Play feedback based on success
        if (data.success !== false) {
          playFeedback('success');
          setShowSuccess(true);
          setTimeout(() => setShowSuccess(false), 1000);
          speakText(data.response_text);
        } else {
          playFeedback('error');
        }

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
    
    pushUndo(); // Save state before processing
    setProcessing(true);
    playFeedback('click');
    
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
      
      // Track new field for animation
      const oldFields = (schema as { fields?: { id: string }[] }).fields || [];
      const newFields = (data.schema as { fields?: { id: string }[] }).fields || [];
      if (newFields.length > oldFields.length) {
        setLastAddedFieldId(newFields[newFields.length - 1]?.id || null);
        setTimeout(() => setLastAddedFieldId(null), 1000);
      }
      
      setSchema(data.schema);
      setLastResponse(data.response_text);
      setCommandHistory(prev => [...prev, {
        transcript: textCommand,
        action: data.action,
        timestamp: new Date().toISOString(),
        success: data.success,
      }]);
      setTextCommand('');
      
      // Play feedback based on success
      if (data.success !== false) {
        playFeedback('success');
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 1000);
      } else {
        playFeedback('error');
      }
    } catch (error) {
      console.error('Failed to process text command:', error);
      playFeedback('error');
    } finally {
      setProcessing(false);
    }
  };

  const playAudioResponse = (base64Audio: string) => {
    const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);
    audio.play();
  };

  const handleSave = () => {
    playFeedback('success');
    endSession(true);
  };

  return (
    <div className="space-y-6">
      {/* Inject animation styles */}
      <style dangerouslySetInnerHTML={{ __html: pulseAnimation }} />
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary animate-pulse" />
            Voice Design Studio
            <Badge variant="secondary" className="ml-2">AI Powered</Badge>
          </h2>
          <p className="text-muted-foreground">Create forms using voice commands</p>
        </div>
        <div className="flex gap-2">
          {/* Undo/Redo */}
          <Button
            variant="outline"
            size="icon"
            onClick={handleUndo}
            disabled={undoStack.length === 0}
            title="Undo (Ctrl+Z)"
          >
            <Undo className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={handleRedo}
            disabled={redoStack.length === 0}
            title="Redo (Ctrl+Y)"
          >
            <Redo className="h-4 w-4" />
          </Button>
          
          {/* Settings */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings2 className="h-4 w-4" />
          </Button>
          
          {/* Keyboard Shortcuts */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setShowKeyboardShortcuts(!showKeyboardShortcuts)}
          >
            <Keyboard className="h-4 w-4" />
          </Button>
          
          <Button variant="outline" onClick={() => startSession()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Reset
          </Button>
          <Button onClick={handleSave} className="gap-2">
            <Save className="h-4 w-4" />
            Save Form
          </Button>
        </div>
      </div>
      
      {/* Settings Panel */}
      {showSettings && (
        <Card className="animate-in slide-in-from-top-2">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Voice Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="sound-effects" className="flex items-center gap-2">
                <Volume2 className="h-4 w-4" />
                Sound Effects
              </Label>
              <Switch
                id="sound-effects"
                checked={soundEnabled}
                onCheckedChange={setSoundEnabled}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="speech-feedback" className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Voice Responses
              </Label>
              <Switch
                id="speech-feedback"
                checked={speechEnabled}
                onCheckedChange={(checked) => {
                  setSpeechEnabled(checked);
                  if (!checked) stopSpeaking();
                }}
              />
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Keyboard Shortcuts Panel */}
      {showKeyboardShortcuts && (
        <Card className="animate-in slide-in-from-top-2">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Keyboard Shortcuts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="flex items-center gap-2">
                <kbd className="px-2 py-1 bg-muted rounded text-xs">Space</kbd>
                <span>Toggle Recording</span>
              </div>
              <div className="flex items-center gap-2">
                <kbd className="px-2 py-1 bg-muted rounded text-xs">Ctrl+Z</kbd>
                <span>Undo</span>
              </div>
              <div className="flex items-center gap-2">
                <kbd className="px-2 py-1 bg-muted rounded text-xs">Ctrl+Y</kbd>
                <span>Redo</span>
              </div>
              <div className="flex items-center gap-2">
                <kbd className="px-2 py-1 bg-muted rounded text-xs">Enter</kbd>
                <span>Send Text Command</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Voice Input */}
        <div className="space-y-4">
          <Card className={cn(showSuccess && 'ring-2 ring-green-500 transition-all')}>
            <CardHeader>
              <CardTitle>Voice Input</CardTitle>
              <CardDescription>
                Click the microphone and speak your commands
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Recording Button with Visual Feedback */}
              <div className="flex flex-col items-center">
                <div className="relative">
                  {/* Pulse rings when recording */}
                  {isRecording && (
                    <>
                      <div 
                        className="absolute inset-0 rounded-full bg-red-500 opacity-20"
                        style={{
                          animation: 'pulse-ring 1.5s ease-in-out infinite',
                          transform: `scale(${1 + audioLevel / 100})`,
                        }}
                      />
                      <div 
                        className="absolute inset-0 rounded-full bg-red-500 opacity-10"
                        style={{
                          animation: 'pulse-ring 1.5s ease-in-out infinite 0.3s',
                          transform: `scale(${1.2 + audioLevel / 100})`,
                        }}
                      />
                    </>
                  )}
                  
                  <button
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={processing || !sessionToken}
                    className={cn(
                      'relative w-24 h-24 rounded-full flex items-center justify-center transition-all transform hover:scale-105',
                      isRecording
                        ? 'bg-red-500 hover:bg-red-600'
                        : 'bg-primary hover:bg-primary/90',
                      processing && 'opacity-50 cursor-not-allowed'
                    )}
                  >
                    {isRecording ? (
                      <MicOff className="h-10 w-10 text-white" />
                    ) : (
                      <Mic className="h-10 w-10 text-white" />
                    )}
                  </button>
                </div>
                
                {/* Audio Level Indicator */}
                {isRecording && (
                  <div className="mt-4 flex items-center gap-1">
                    {[...Array(7)].map((_, i) => (
                      <div
                        key={i}
                        className="w-1 bg-red-500 rounded-full transition-all"
                        style={{
                          height: `${Math.max(4, (audioLevel / 100) * 24 * Math.sin((i + 1) * 0.5))}px`,
                          animation: `waveform ${0.5 + i * 0.1}s ease-in-out infinite`,
                        }}
                      />
                    ))}
                  </div>
                )}
                
                <p className="mt-2 text-sm text-muted-foreground flex items-center gap-2">
                  {isRecording ? (
                    <>
                      <span className="flex h-2 w-2 relative">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                      </span>
                      Recording... Click to stop
                    </>
                  ) : (
                    'Press Space or click to start recording'
                  )}
                </p>
              </div>

              {/* Processing Indicator with Animation */}
              {processing && (
                <div className="flex flex-col items-center justify-center gap-2 p-4 bg-muted/50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Wand2 className="h-5 w-5 text-primary animate-bounce" />
                    <Zap className="h-4 w-4 text-yellow-500 animate-pulse" />
                  </div>
                  <p className="text-sm text-muted-foreground">Processing your command...</p>
                  <Progress value={66} className="w-32 h-1" />
                </div>
              )}

              {/* Last Response with Animation */}
              {lastResponse && (
                <div className={cn(
                  'p-3 rounded-lg flex items-start gap-2 transition-all animate-in slide-in-from-bottom-2',
                  showSuccess ? 'bg-green-50 border border-green-200' : 'bg-muted'
                )}>
                  {speechEnabled ? (
                    <Volume2 className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                  ) : (
                    <VolumeX className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
                  )}
                  <p className="text-sm">{lastResponse}</p>
                  {showSuccess && <CheckCircle className="h-4 w-4 text-green-500 shrink-0 ml-auto" />}
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
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2">
                <History className="h-4 w-4" />
                Command History
              </CardTitle>
              {commandHistory.length > 0 && (
                <Badge variant="secondary">{commandHistory.length} commands</Badge>
              )}
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
              {(() => {
                type VoiceField = { id?: string; label?: string; required?: boolean; type?: string; placeholder?: string; options?: string[]; help?: string };
                type VoiceSchema = { title?: string; description?: string; fields?: VoiceField[] };
                const s = schema as VoiceSchema;
                return (
                  <>
                    <h3 className="text-xl font-semibold mb-2">{s.title || 'Untitled Form'}</h3>
                    {s.description && (
                      <p className="text-muted-foreground mb-4">{s.description}</p>
                    )}

                    {/* Fields */}
                    <div className="space-y-4">
                      {(s.fields || []).map((field: VoiceField, index: number) => (
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

                      {(s.fields || []).length === 0 && (
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

                    {/* Field Count */}
                    <div className="flex items-center justify-between mt-4 pt-4 border-t">
                      <span className="text-sm text-muted-foreground">{(s.fields || []).length} field(s)</span>
                      <Badge variant="outline">{sessionToken ? 'Session Active' : 'No Session'}</Badge>
                    </div>
                  </>
                );
              })()}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default VoiceDesignStudio;
