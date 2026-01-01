'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Mic,
  MicOff,
  Camera,
  MapPin,
  Hand,
  Smartphone,
  Wifi,
  WifiOff,
  Loader2,
  CheckCircle,
  AlertCircle,
  Settings,
  Volume2,
  Globe,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Fingerprint,
  Image,
  FileImage,
} from 'lucide-react';

interface MobileConfig {
  id: string;
  form_id: string;
  enable_touch_gestures: boolean;
  enable_voice_input: boolean;
  enable_camera_upload: boolean;
  enable_geolocation: boolean;
  enable_biometric: boolean;
  swipe_sensitivity: number;
  voice_language: string;
  offline_mode: boolean;
  compress_images: boolean;
  max_image_size_mb: number;
}

interface VoiceInputState {
  isListening: boolean;
  transcript: string;
  confidence: number;
  language: string;
}

interface GeolocationState {
  latitude: number | null;
  longitude: number | null;
  accuracy: number | null;
  timestamp: number | null;
  error: string | null;
}

interface MobileInteractionsProps {
  formId: string;
}

const SUPPORTED_LANGUAGES = [
  { code: 'en-US', label: 'English (US)' },
  { code: 'en-GB', label: 'English (UK)' },
  { code: 'es-ES', label: 'Spanish' },
  { code: 'fr-FR', label: 'French' },
  { code: 'de-DE', label: 'German' },
  { code: 'it-IT', label: 'Italian' },
  { code: 'pt-BR', label: 'Portuguese (Brazil)' },
  { code: 'ja-JP', label: 'Japanese' },
  { code: 'zh-CN', label: 'Chinese (Simplified)' },
  { code: 'ko-KR', label: 'Korean' },
];

export function MobileInteractions({ formId }: MobileInteractionsProps) {
  const [config, setConfig] = useState<MobileConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [voiceState, setVoiceState] = useState<VoiceInputState>({
    isListening: false,
    transcript: '',
    confidence: 0,
    language: 'en-US',
  });
  const [geoState, setGeoState] = useState<GeolocationState>({
    latitude: null,
    longitude: null,
    accuracy: null,
    timestamp: null,
    error: null,
  });
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  type SpeechRecognitionLike = {
    continuous?: boolean;
    interimResults?: boolean;
    lang?: string;
    onresult?: (e: unknown) => void;
    onerror?: (e: unknown) => void;
    onend?: () => void;
    start: () => void;
    stop: () => void;
  };

  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);

  const fetchConfig = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/mobile/config/?form_id=${formId}`);
      const data = await response.json();
      if (data.results?.length > 0) {
        setConfig(data.results[0]);
      } else if (data.length > 0) {
        setConfig(data[0]);
      } else {
        // Set default config
        setConfig({
          id: '',
          form_id: formId,
          enable_touch_gestures: true,
          enable_voice_input: true,
          enable_camera_upload: true,
          enable_geolocation: false,
          enable_biometric: false,
          swipe_sensitivity: 50,
          voice_language: 'en-US',
          offline_mode: false,
          compress_images: true,
          max_image_size_mb: 5,
        });
      }
    } catch (error) {
      console.error('Failed to fetch config:', error);
    } finally {
      setLoading(false);
    }
  }, [formId]);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const saveConfig = async () => {
    if (!config) return;
    setSaving(true);
    try {
      const method = config.id ? 'PUT' : 'POST';
      const url = config.id 
        ? `/api/v1/features/mobile/config/${config.id}/`
        : `/api/v1/features/mobile/config/`;
      
      await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
    } catch (error) {
      console.error('Failed to save config:', error);
    } finally {
      setSaving(false);
    }
  };

  const updateConfig = (updates: Partial<MobileConfig>) => {
    if (!config) return;
    setConfig({ ...config, ...updates });
  };

  // Voice Input Functions
  const startVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Voice input is not supported in this browser');
      return;
    }

    const w = window as unknown as { SpeechRecognition?: new () => SpeechRecognitionLike; webkitSpeechRecognition?: new () => SpeechRecognitionLike };
    const RecognitionCtor = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (!RecognitionCtor) {
      alert('Voice input is not supported in this browser');
      return;
    }
    const recognition = new RecognitionCtor();
    
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = voiceState.language;

    recognition.onresult = (event: unknown) => {
      const ev = event as { resultIndex: number; results: Array<Array<{ transcript: string; confidence: number }>> };
      let transcript = '';
      let confidence = 0;
      
      for (let i = ev.resultIndex; i < ev.results.length; i++) {
        transcript += ev.results[i][0].transcript;
        confidence = ev.results[i][0].confidence;
      }
      
      setVoiceState(prev => ({
        ...prev,
        transcript,
        confidence: confidence * 100,
      }));
    };

    recognition.onerror = (event: unknown) => {
      const e = event as { error?: string };
      console.error('Voice recognition error:', e.error);
      setVoiceState(prev => ({ ...prev, isListening: false }));
    }; 

    recognition.onend = () => {
      setVoiceState(prev => ({ ...prev, isListening: false }));
    };

    recognition.start();
    recognitionRef.current = recognition;
    setVoiceState(prev => ({ ...prev, isListening: true }));
  };

  const stopVoiceInput = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setVoiceState(prev => ({ ...prev, isListening: false }));
  };

  // Camera Functions
  const startCamera = async () => {
    setIsCapturing(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (error) {
      console.error('Failed to start camera:', error);
      setIsCapturing(false);
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0);
      const imageData = canvas.toDataURL('image/jpeg', 0.8);
      setCapturedImage(imageData);
      
      // Stop camera stream
      const stream = video.srcObject as MediaStream;
      stream?.getTracks().forEach(track => track.stop());
      setIsCapturing(false);
    }
  };

  const stopCamera = () => {
    if (videoRef.current) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream?.getTracks().forEach(track => track.stop());
    }
    setIsCapturing(false);
  };

  // Geolocation Functions
  const getLocation = () => {
    if (!navigator.geolocation) {
      setGeoState(prev => ({ ...prev, error: 'Geolocation not supported' }));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setGeoState({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: position.timestamp,
          error: null,
        });
      },
      (error) => {
        setGeoState(prev => ({ ...prev, error: error.message }));
      },
      { enableHighAccuracy: true }
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Smartphone className="h-6 w-6" />
            Mobile Interactions
          </h2>
          <p className="text-muted-foreground">Configure mobile-first features for your forms</p>
        </div>
        <Button onClick={saveConfig} disabled={saving}>
          {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <CheckCircle className="h-4 w-4 mr-2" />}
          Save Configuration
        </Button>
      </div>

      <Tabs defaultValue="settings">
        <TabsList>
          <TabsTrigger value="settings">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </TabsTrigger>
          <TabsTrigger value="voice">
            <Mic className="h-4 w-4 mr-2" />
            Voice Input
          </TabsTrigger>
          <TabsTrigger value="camera">
            <Camera className="h-4 w-4 mr-2" />
            Camera
          </TabsTrigger>
          <TabsTrigger value="location">
            <MapPin className="h-4 w-4 mr-2" />
            Location
          </TabsTrigger>
          <TabsTrigger value="gestures">
            <Hand className="h-4 w-4 mr-2" />
            Gestures
          </TabsTrigger>
        </TabsList>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Feature Toggles</CardTitle>
                <CardDescription>Enable or disable mobile features</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Mic className="h-4 w-4" />
                    <Label>Voice Input</Label>
                  </div>
                  <Switch
                    checked={config?.enable_voice_input}
                    onCheckedChange={(checked) => updateConfig({ enable_voice_input: checked })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Camera className="h-4 w-4" />
                    <Label>Camera Upload</Label>
                  </div>
                  <Switch
                    checked={config?.enable_camera_upload}
                    onCheckedChange={(checked) => updateConfig({ enable_camera_upload: checked })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    <Label>Geolocation</Label>
                  </div>
                  <Switch
                    checked={config?.enable_geolocation}
                    onCheckedChange={(checked) => updateConfig({ enable_geolocation: checked })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Hand className="h-4 w-4" />
                    <Label>Touch Gestures</Label>
                  </div>
                  <Switch
                    checked={config?.enable_touch_gestures}
                    onCheckedChange={(checked) => updateConfig({ enable_touch_gestures: checked })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Fingerprint className="h-4 w-4" />
                    <Label>Biometric Auth</Label>
                  </div>
                  <Switch
                    checked={config?.enable_biometric}
                    onCheckedChange={(checked) => updateConfig({ enable_biometric: checked })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <WifiOff className="h-4 w-4" />
                    <Label>Offline Mode</Label>
                  </div>
                  <Switch
                    checked={config?.offline_mode}
                    onCheckedChange={(checked) => updateConfig({ offline_mode: checked })}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Image Settings</CardTitle>
                <CardDescription>Configure camera and image options</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileImage className="h-4 w-4" />
                    <Label>Compress Images</Label>
                  </div>
                  <Switch
                    checked={config?.compress_images}
                    onCheckedChange={(checked) => updateConfig({ compress_images: checked })}
                  />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label>Max Image Size</Label>
                    <span className="text-sm font-medium">{config?.max_image_size_mb} MB</span>
                  </div>
                  <Slider
                    value={[config?.max_image_size_mb || 5]}
                    min={1}
                    max={20}
                    step={1}
                    onValueChange={([value]) => updateConfig({ max_image_size_mb: value })}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Voice Input Tab */}
        <TabsContent value="voice" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Volume2 className="h-5 w-5" />
                Voice Input Demo
              </CardTitle>
              <CardDescription>Test voice-to-text functionality</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Globe className="h-4 w-4" />
                  <Label>Language</Label>
                </div>
                <select
                  className="border rounded-md px-3 py-2"
                  value={voiceState.language}
                  onChange={(e) => setVoiceState(prev => ({ ...prev, language: e.target.value }))}
                >
                  {SUPPORTED_LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-center">
                <Button
                  size="lg"
                  variant={voiceState.isListening ? 'destructive' : 'default'}
                  onClick={voiceState.isListening ? stopVoiceInput : startVoiceInput}
                  className="w-32 h-32 rounded-full"
                >
                  {voiceState.isListening ? (
                    <MicOff className="h-12 w-12" />
                  ) : (
                    <Mic className="h-12 w-12" />
                  )}
                </Button>
              </div>

              {voiceState.isListening && (
                <div className="flex items-center justify-center gap-2 text-sm">
                  <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                  Listening...
                </div>
              )}

              <div className="space-y-2">
                <Label>Transcript</Label>
                <Textarea
                  value={voiceState.transcript}
                  readOnly
                  placeholder="Start speaking to see text here..."
                  className="min-h-[100px]"
                />
                {voiceState.confidence > 0 && (
                  <p className="text-sm text-muted-foreground">
                    Confidence: {voiceState.confidence.toFixed(1)}%
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Camera Tab */}
        <TabsContent value="camera" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="h-5 w-5" />
                Camera Capture Demo
              </CardTitle>
              <CardDescription>Test photo capture functionality</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-center">
                {isCapturing ? (
                  <div className="relative">
                    <video
                      ref={videoRef}
                      className="rounded-lg border max-w-full"
                      style={{ maxHeight: '400px' }}
                    />
                    <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-2">
                      <Button onClick={capturePhoto}>
                        <Camera className="h-4 w-4 mr-2" />
                        Capture
                      </Button>
                      <Button variant="outline" onClick={stopCamera}>
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : capturedImage ? (
                  <div className="space-y-4">
                    <img
                      src={capturedImage}
                      alt="Captured"
                      className="rounded-lg border max-w-full"
                      style={{ maxHeight: '400px' }}
                    />
                    <div className="flex justify-center gap-2">
                      <Button variant="outline" onClick={() => setCapturedImage(null)}>
                        <Image className="h-4 w-4 mr-2" />
                        Clear
                      </Button>
                      <Button onClick={startCamera}>
                        <Camera className="h-4 w-4 mr-2" />
                        Retake
                      </Button>
                    </div>
                  </div>
                ) : (
                  <Button size="lg" onClick={startCamera} className="py-8 px-12">
                    <Camera className="h-8 w-8 mr-2" />
                    Open Camera
                  </Button>
                )}
              </div>
              <canvas ref={canvasRef} className="hidden" />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Location Tab */}
        <TabsContent value="location" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Geolocation Demo
              </CardTitle>
              <CardDescription>Test location capture functionality</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-center">
                <Button size="lg" onClick={getLocation}>
                  <MapPin className="h-4 w-4 mr-2" />
                  Get Current Location
                </Button>
              </div>

              {geoState.error && (
                <div className="flex items-center gap-2 p-4 bg-red-50 text-red-700 rounded-lg">
                  <AlertCircle className="h-5 w-5" />
                  {geoState.error}
                </div>
              )}

              {geoState.latitude && (
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="p-4 border rounded-lg">
                    <p className="text-sm text-muted-foreground">Latitude</p>
                    <p className="text-xl font-mono">{geoState.latitude.toFixed(6)}</p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <p className="text-sm text-muted-foreground">Longitude</p>
                    <p className="text-xl font-mono">{geoState.longitude?.toFixed(6)}</p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <p className="text-sm text-muted-foreground">Accuracy</p>
                    <p className="text-xl font-mono">{geoState.accuracy?.toFixed(0)} m</p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <p className="text-sm text-muted-foreground">Timestamp</p>
                    <p className="text-sm font-mono">
                      {geoState.timestamp && new Date(geoState.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Gestures Tab */}
        <TabsContent value="gestures" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Hand className="h-5 w-5" />
                Touch Gesture Configuration
              </CardTitle>
              <CardDescription>Configure swipe and touch gestures</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Swipe Sensitivity</Label>
                  <span className="text-sm font-medium">{config?.swipe_sensitivity}%</span>
                </div>
                <Slider
                  value={[config?.swipe_sensitivity || 50]}
                  min={10}
                  max={100}
                  step={5}
                  onValueChange={([value]) => updateConfig({ swipe_sensitivity: value })}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <ArrowLeft className="h-4 w-4" />
                    <span className="font-medium">Swipe Left</span>
                  </div>
                  <p className="text-sm text-muted-foreground">Go to previous field</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <ArrowRight className="h-4 w-4" />
                    <span className="font-medium">Swipe Right</span>
                  </div>
                  <p className="text-sm text-muted-foreground">Go to next field</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <ArrowUp className="h-4 w-4" />
                    <span className="font-medium">Swipe Up</span>
                  </div>
                  <p className="text-sm text-muted-foreground">Show form progress</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <ArrowDown className="h-4 w-4" />
                    <span className="font-medium">Swipe Down</span>
                  </div>
                  <p className="text-sm text-muted-foreground">Save and continue later</p>
                </div>
              </div>

              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm font-medium mb-2">Touch Gestures Available:</p>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Double-tap to zoom on text fields</li>
                  <li>• Long-press to copy field value</li>
                  <li>• Pinch to zoom on image fields</li>
                  <li>• Two-finger swipe for quick navigation</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default MobileInteractions;
