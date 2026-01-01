/**
 * Voice-Activated Form Filling
 * Allows end users to fill forms using voice input
 */
'use client';

import React, { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from '@/components/ui/tooltip';
import { 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX,
  ChevronRight,
  ChevronLeft,
  Check,
  X,
  RefreshCw,
  HelpCircle,
  Settings,
  SkipForward,
  MessageSquare,
  AlertCircle,
  CheckCircle2,
  Loader2,
  Languages,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Types
interface FormField {
  id: string;
  type: 'text' | 'email' | 'phone' | 'number' | 'date' | 'select' | 'radio' | 'checkbox' | 'textarea';
  label: string;
  placeholder?: string;
  required?: boolean;
  options?: { value: string; label: string }[];
  validation?: {
    pattern?: string;
    min?: number;
    max?: number;
    minLength?: number;
    maxLength?: number;
  };
}

interface VoiceFormFillingProps {
  fields: FormField[];
  onSubmit: (data: Record<string, string>) => void;
  onFieldChange?: (fieldId: string, value: string) => void;
  language?: string;
  enableConfirmation?: boolean;
  enableReadBack?: boolean;
}

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
  onspeechend: () => void;
}

type SpeechRecognitionConstructor = new () => ISpeechRecognition;

export function VoiceFormFilling({
  fields,
  onSubmit,
  onFieldChange,
  language = 'en-US',
  enableConfirmation = true,
  enableReadBack = true,
}: VoiceFormFillingProps) {
  // State
  const [currentFieldIndex, setCurrentFieldIndex] = useState(0);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [status, setStatus] = useState<'idle' | 'listening' | 'processing' | 'confirming' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [pendingValue, setPendingValue] = useState<string | null>(null);
  const [isAutoAdvance, setIsAutoAdvance] = useState(true);
  const [speechEnabled, setSpeechEnabled] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [voiceMode, setVoiceMode] = useState<'conversational' | 'direct'>('conversational');

  // Refs
  const recognitionRef = useRef<ISpeechRecognition | null>(null);
  const synthRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Current field
  const currentField = useMemo(() => fields[currentFieldIndex], [fields, currentFieldIndex]);
  const progress = useMemo(() => ((currentFieldIndex) / fields.length) * 100, [currentFieldIndex, fields.length]);
  const isComplete = currentFieldIndex >= fields.length;

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition() as ISpeechRecognition;
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = language;
        recognitionRef.current = recognition;
      }
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, [language]);

  // Speak function
  const speak = useCallback((text: string): Promise<void> => {
    return new Promise((resolve) => {
      if (!speechEnabled || !window.speechSynthesis) {
        resolve();
        return;
      }

      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language;
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => {
        setIsSpeaking(false);
        resolve();
      };
      utterance.onerror = () => {
        setIsSpeaking(false);
        resolve();
      };

      synthRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    });
  }, [language, speechEnabled]);

  // Stop speaking
  const stopSpeaking = useCallback(() => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, []);

  // Ask current field question
  const askFieldQuestion = useCallback(async () => {
    if (!currentField) return;

    const fieldType = currentField.type;
    let question = '';

    if (voiceMode === 'conversational') {
      question = `Please tell me your ${currentField.label.toLowerCase()}`;
      
      if (fieldType === 'select' || fieldType === 'radio') {
        const options = currentField.options?.map(o => o.label).join(', ');
        question += `. Your options are: ${options}`;
      } else if (fieldType === 'checkbox') {
        question += `. Say yes or no`;
      } else if (fieldType === 'date') {
        question += `. Please say the date in a natural format`;
      } else if (fieldType === 'email') {
        question += `. Please spell it out if needed`;
      }

      if (!currentField.required) {
        question += `. You can also say skip to continue`;
      }
    } else {
      question = currentField.label;
    }

    await speak(question);
  }, [currentField, speak, voiceMode]);

  // Parse voice input based on field type
  const parseVoiceInput = useCallback((transcript: string, field: FormField): string => {
    const normalizedInput = transcript.toLowerCase().trim();

    switch (field.type) {
      case 'email':
        // Handle common email phrases
        return normalizedInput
          .replace(/\s+at\s+/gi, '@')
          .replace(/\s+dot\s+/gi, '.')
          .replace(/\s+underscore\s+/gi, '_')
          .replace(/\s+dash\s+/gi, '-')
          .replace(/\s/g, '');
      
      case 'phone':
        // Extract numbers only
        return normalizedInput.replace(/\D/g, '');
      
      case 'number':
        // Parse number words
        const numberWords: Record<string, string> = {
          'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
          'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
          'ten': '10', 'eleven': '11', 'twelve': '12', 'twenty': '20',
          'thirty': '30', 'forty': '40', 'fifty': '50', 'hundred': '100',
        };
        let result = normalizedInput;
        Object.entries(numberWords).forEach(([word, num]) => {
          result = result.replace(new RegExp(word, 'gi'), num);
        });
        return result.replace(/\D/g, '');
      
      case 'date':
        // Try to parse natural date
        try {
          const date = new Date(transcript);
          if (!isNaN(date.getTime())) {
            return date.toISOString().split('T')[0];
          }
        } catch {
          // Fall through
        }
        return transcript;
      
      case 'checkbox':
        // Boolean detection
        if (/yes|yeah|yep|correct|affirmative|true|sure|ok|check/i.test(normalizedInput)) {
          return 'true';
        }
        if (/no|nope|false|negative|uncheck|nah/i.test(normalizedInput)) {
          return 'false';
        }
        return transcript;
      
      case 'select':
      case 'radio':
        // Match to closest option
        if (field.options) {
          const match = field.options.find(opt =>
            opt.label.toLowerCase().includes(normalizedInput) ||
            opt.value.toLowerCase().includes(normalizedInput)
          );
          if (match) return match.value;
        }
        return transcript;
      
      default:
        return transcript;
    }
  }, []);

  // Validate field value
  const validateValue = useCallback((value: string, field: FormField): { valid: boolean; error?: string } => {
    if (field.required && !value) {
      return { valid: false, error: 'This field is required' };
    }

    if (!value) return { valid: true };

    switch (field.type) {
      case 'email':
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          return { valid: false, error: 'Please provide a valid email address' };
        }
        break;
      
      case 'phone':
        if (value.length < 10) {
          return { valid: false, error: 'Phone number seems too short' };
        }
        break;
      
      case 'number':
        if (isNaN(Number(value))) {
          return { valid: false, error: 'Please provide a valid number' };
        }
        if (field.validation?.min && Number(value) < field.validation.min) {
          return { valid: false, error: `Value must be at least ${field.validation.min}` };
        }
        if (field.validation?.max && Number(value) > field.validation.max) {
          return { valid: false, error: `Value must be at most ${field.validation.max}` };
        }
        break;
    }

    if (field.validation?.minLength && value.length < field.validation.minLength) {
      return { valid: false, error: `Please provide at least ${field.validation.minLength} characters` };
    }

    return { valid: true };
  }, []);

  // Handle voice input result
  const handleVoiceResult = useCallback(async (transcript: string, isFinal: boolean) => {
    if (!currentField) return;

    setInterimTranscript(transcript);

    if (!isFinal) return;

    // Check for navigation commands
    const normalizedTranscript = transcript.toLowerCase().trim();
    
    if (/^(skip|next|pass)$/i.test(normalizedTranscript)) {
      if (!currentField.required) {
        setInterimTranscript('');
        if (isAutoAdvance) {
          setCurrentFieldIndex(prev => Math.min(prev + 1, fields.length));
        }
        return;
      } else {
        setErrorMessage('This field is required');
        await speak('This field is required. Please provide a value.');
        return;
      }
    }

    if (/^(back|previous|go back)$/i.test(normalizedTranscript)) {
      setInterimTranscript('');
      setCurrentFieldIndex(prev => Math.max(prev - 1, 0));
      return;
    }

    if (/^(repeat|say again|what)$/i.test(normalizedTranscript)) {
      await askFieldQuestion();
      return;
    }

    if (/^(clear|delete|erase)$/i.test(normalizedTranscript)) {
      setInterimTranscript('');
      setFormData(prev => ({ ...prev, [currentField.id]: '' }));
      await speak('Cleared. Please provide a new value.');
      return;
    }

    // Parse and validate the input
    const parsedValue = parseVoiceInput(transcript, currentField);
    const validation = validateValue(parsedValue, currentField);

    if (!validation.valid) {
      setErrorMessage(validation.error || 'Invalid input');
      setStatus('error');
      await speak(validation.error || 'That doesn\'t seem right. Please try again.');
      setStatus('idle');
      return;
    }

    if (enableConfirmation && parsedValue) {
      // Ask for confirmation
      setPendingValue(parsedValue);
      setStatus('confirming');
      
      if (enableReadBack) {
        await speak(`I heard "${parsedValue}". Is that correct? Say yes or no.`);
      } else {
        await speak('Is that correct? Say yes or no.');
      }
    } else {
      // Direct save
      saveValue(parsedValue);
    }
  }, [currentField, fields.length, isAutoAdvance, parseVoiceInput, validateValue, enableConfirmation, enableReadBack, speak, askFieldQuestion]);

  // Save value and advance
  const saveValue = useCallback(async (value: string) => {
    if (!currentField) return;

    setFormData(prev => ({ ...prev, [currentField.id]: value }));
    onFieldChange?.(currentField.id, value);
    setInterimTranscript('');
    setPendingValue(null);
    setStatus('idle');
    setErrorMessage('');

    if (isAutoAdvance) {
      const nextIndex = currentFieldIndex + 1;
      if (nextIndex >= fields.length) {
        await speak('Great! All fields are complete. Ready to submit?');
      } else {
        await speak('Got it!');
        setCurrentFieldIndex(nextIndex);
      }
    }
  }, [currentField, currentFieldIndex, fields.length, isAutoAdvance, onFieldChange, speak]);

  // Handle confirmation response
  const handleConfirmation = useCallback(async (confirmed: boolean) => {
    if (confirmed && pendingValue !== null) {
      await saveValue(pendingValue);
    } else {
      setPendingValue(null);
      setStatus('idle');
      await speak('Let\'s try again. ' + currentField?.label);
    }
  }, [pendingValue, saveValue, speak, currentField]);

  // Start listening
  const startListening = useCallback(() => {
    if (!recognitionRef.current) {
      setErrorMessage('Speech recognition not supported');
      return;
    }

    stopSpeaking();
    setIsListening(true);
    setStatus('listening');
    setErrorMessage('');
    setInterimTranscript('');

    recognitionRef.current.onresult = (event: SpeechRecognitionEvent) => {
      let finalTranscript = '';
      let interim = '';
      let maxConfidence = 0;

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
          maxConfidence = Math.max(maxConfidence, result[0].confidence);
        } else {
          interim += result[0].transcript;
        }
      }

      setConfidence(Math.round(maxConfidence * 100));
      
      if (finalTranscript) {
        handleVoiceResult(finalTranscript, true);
      } else {
        handleVoiceResult(interim, false);
      }
    };

    recognitionRef.current.onend = () => {
      setIsListening(false);
      if (status === 'listening') {
        setStatus('idle');
      }
    };

    recognitionRef.current.onerror = (event) => {
      setIsListening(false);
      setStatus('error');
      setErrorMessage(`Recognition error: ${event.error}`);
    };

    recognitionRef.current.start();
  }, [handleVoiceResult, status, stopSpeaking]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
    setStatus('idle');
  }, []);

  // Toggle listening
  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  // Navigate fields
  const goToField = useCallback((index: number) => {
    if (index >= 0 && index < fields.length) {
      setCurrentFieldIndex(index);
      setInterimTranscript('');
      setErrorMessage('');
      setPendingValue(null);
      setStatus('idle');
    }
  }, [fields.length]);

  // Handle form submission
  const handleSubmit = useCallback(() => {
    // Check all required fields
    const missingRequired = fields.filter(f => f.required && !formData[f.id]);
    if (missingRequired.length > 0) {
      speak(`Please fill in ${missingRequired.map(f => f.label).join(', ')} before submitting`);
      setCurrentFieldIndex(fields.findIndex(f => f.id === missingRequired[0].id));
      return;
    }
    onSubmit(formData);
  }, [fields, formData, onSubmit, speak]);

  // Auto-start asking when field changes
  useEffect(() => {
    if (voiceMode === 'conversational' && currentField && !isComplete) {
      const timer = setTimeout(() => {
        askFieldQuestion();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [currentFieldIndex, askFieldQuestion, voiceMode, currentField, isComplete]);

  // Check support
  const isSupported = typeof window !== 'undefined' && 
    ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);

  if (!isSupported) {
    return (
      <Card className="max-w-lg mx-auto">
        <CardContent className="pt-6 text-center">
          <AlertCircle className="h-12 w-12 mx-auto mb-4 text-yellow-500" />
          <h3 className="font-medium mb-2">Voice Input Not Supported</h3>
          <p className="text-sm text-muted-foreground">
            Your browser doesn't support voice input. Please use Chrome, Edge, or Safari.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <TooltipProvider>
      <div className="max-w-2xl mx-auto space-y-4">
        {/* Progress Header */}
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">
                {isComplete ? 'Complete!' : `Question ${currentFieldIndex + 1} of ${fields.length}`}
              </span>
              <div className="flex items-center gap-2">
                <Badge variant={isListening ? 'default' : 'secondary'}>
                  {isListening ? 'Listening...' : 'Ready'}
                </Badge>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowSettings(!showSettings)}
                >
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <Progress value={isComplete ? 100 : progress} className="h-2" />
          </CardContent>
        </Card>

        {/* Settings Panel */}
        {showSettings && (
          <Card>
            <CardContent className="pt-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Volume2 className="h-4 w-4" />
                  <Label>Voice Feedback</Label>
                </div>
                <Switch
                  checked={speechEnabled}
                  onCheckedChange={setSpeechEnabled}
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <SkipForward className="h-4 w-4" />
                  <Label>Auto Advance</Label>
                </div>
                <Switch
                  checked={isAutoAdvance}
                  onCheckedChange={setIsAutoAdvance}
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4" />
                  <Label>Confirm Answers</Label>
                </div>
                <Switch
                  checked={enableConfirmation}
                  disabled
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4" />
                  <Label>Voice Mode</Label>
                </div>
                <div className="flex gap-1">
                  <Button
                    size="sm"
                    variant={voiceMode === 'conversational' ? 'default' : 'outline'}
                    onClick={() => setVoiceMode('conversational')}
                  >
                    Conversational
                  </Button>
                  <Button
                    size="sm"
                    variant={voiceMode === 'direct' ? 'default' : 'outline'}
                    onClick={() => setVoiceMode('direct')}
                  >
                    Direct
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Main Voice Interface */}
        {!isComplete ? (
          <Card className="overflow-hidden">
            <CardHeader className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white">
              <CardTitle className="flex items-center gap-2">
                {currentField?.required && <span className="text-red-200">*</span>}
                {currentField?.label}
              </CardTitle>
              {currentField?.placeholder && (
                <CardDescription className="text-white/80">
                  {currentField.placeholder}
                </CardDescription>
              )}
            </CardHeader>
            <CardContent className="pt-6 space-y-6">
              {/* Field Type Hint */}
              <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                <HelpCircle className="h-4 w-4" />
                <span>
                  {currentField?.type === 'select' || currentField?.type === 'radio'
                    ? `Options: ${currentField.options?.map(o => o.label).join(', ')}`
                    : currentField?.type === 'email'
                    ? 'Say "at" for @ and "dot" for .'
                    : currentField?.type === 'checkbox'
                    ? 'Say "yes" or "no"'
                    : `Type: ${currentField?.type}`
                  }
                </span>
              </div>

              {/* Current Value Display */}
              <div className="p-4 rounded-lg border-2 min-h-[80px] flex items-center justify-center">
                {status === 'confirming' ? (
                  <div className="text-center space-y-2">
                    <p className="text-lg font-medium">{pendingValue}</p>
                    <p className="text-sm text-muted-foreground">Is this correct?</p>
                    <div className="flex justify-center gap-2 mt-4">
                      <Button
                        variant="outline"
                        onClick={() => handleConfirmation(false)}
                      >
                        <X className="h-4 w-4 mr-2" />
                        No
                      </Button>
                      <Button onClick={() => handleConfirmation(true)}>
                        <Check className="h-4 w-4 mr-2" />
                        Yes
                      </Button>
                    </div>
                  </div>
                ) : interimTranscript ? (
                  <p className={cn(
                    'text-lg',
                    status === 'listening' && 'text-muted-foreground italic'
                  )}>
                    {interimTranscript}
                  </p>
                ) : formData[currentField?.id] ? (
                  <p className="text-lg font-medium text-green-600">
                    ✓ {formData[currentField.id]}
                  </p>
                ) : (
                  <p className="text-muted-foreground">
                    Tap the microphone and speak your answer
                  </p>
                )}
              </div>

              {/* Error Message */}
              {errorMessage && (
                <div className="flex items-center gap-2 text-red-600 justify-center">
                  <AlertCircle className="h-4 w-4" />
                  <span className="text-sm">{errorMessage}</span>
                </div>
              )}

              {/* Voice Controls */}
              <div className="flex items-center justify-center gap-4">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => goToField(currentFieldIndex - 1)}
                      disabled={currentFieldIndex === 0}
                    >
                      <ChevronLeft className="h-5 w-5" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Previous field</TooltipContent>
                </Tooltip>

                <Button
                  size="lg"
                  className={cn(
                    'w-20 h-20 rounded-full transition-all',
                    isListening && 'bg-red-500 hover:bg-red-600 animate-pulse'
                  )}
                  onClick={toggleListening}
                >
                  {isListening ? (
                    <MicOff className="h-8 w-8" />
                  ) : (
                    <Mic className="h-8 w-8" />
                  )}
                </Button>

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => goToField(currentFieldIndex + 1)}
                      disabled={currentFieldIndex >= fields.length - 1}
                    >
                      <ChevronRight className="h-5 w-5" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Next field</TooltipContent>
                </Tooltip>
              </div>

              {/* Audio Level Indicator */}
              {isListening && (
                <div className="flex items-center justify-center gap-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div
                      key={i}
                      className={cn(
                        'w-2 rounded-full bg-indigo-500 transition-all',
                        'animate-pulse'
                      )}
                      style={{
                        height: `${12 + Math.random() * 20}px`,
                        animationDelay: `${i * 0.1}s`
                      }}
                    />
                  ))}
                </div>
              )}

              {/* Confidence Indicator */}
              {confidence > 0 && !isListening && (
                <div className="flex items-center justify-center gap-2 text-sm">
                  <span className="text-muted-foreground">Confidence:</span>
                  <Progress value={confidence} className="w-24 h-2" />
                  <span className="font-medium">{confidence}%</span>
                </div>
              )}

              {/* Helper Actions */}
              <div className="flex justify-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={askFieldQuestion}
                  disabled={isSpeaking}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Repeat Question
                </Button>
                {speechEnabled && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={isSpeaking ? stopSpeaking : undefined}
                  >
                    {isSpeaking ? (
                      <>
                        <VolumeX className="h-4 w-4 mr-2" />
                        Stop Speaking
                      </>
                    ) : (
                      <>
                        <Volume2 className="h-4 w-4 mr-2" />
                        Voice On
                      </>
                    )}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (
          // Completion Card
          <Card>
            <CardContent className="pt-6 text-center space-y-6">
              <div className="w-20 h-20 rounded-full bg-green-100 mx-auto flex items-center justify-center">
                <CheckCircle2 className="h-10 w-10 text-green-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold">All Done!</h3>
                <p className="text-muted-foreground">
                  You've answered all {fields.length} questions
                </p>
              </div>
              <Button size="lg" onClick={handleSubmit}>
                Submit Form
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Field Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Form Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 md:grid-cols-6 gap-2">
              {fields.map((field, index) => (
                <Tooltip key={field.id}>
                  <TooltipTrigger asChild>
                    <button
                      className={cn(
                        'p-2 rounded border text-xs text-center transition-colors',
                        index === currentFieldIndex && 'border-indigo-500 bg-indigo-50',
                        formData[field.id] && 'bg-green-50 border-green-200',
                        !formData[field.id] && index < currentFieldIndex && 'bg-yellow-50 border-yellow-200'
                      )}
                      onClick={() => goToField(index)}
                    >
                      {formData[field.id] ? (
                        <Check className="h-3 w-3 mx-auto text-green-600" />
                      ) : (
                        <span>{index + 1}</span>
                      )}
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="font-medium">{field.label}</p>
                    {formData[field.id] && (
                      <p className="text-xs text-muted-foreground">{formData[field.id]}</p>
                    )}
                  </TooltipContent>
                </Tooltip>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </TooltipProvider>
  );
}

export default VoiceFormFilling;
