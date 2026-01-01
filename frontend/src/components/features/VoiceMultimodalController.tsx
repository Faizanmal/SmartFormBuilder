'use client';

import React, { useState, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  useVoiceFormConfig, 
  useUpdateVoiceConfig,
  useTranscribeVoice,
  useMultimodalConfig,
  useUpdateMultimodalConfig,
  useOCRExtract,
  useARPreviewConfig
} from '@/hooks/use-emerging-features';
import { 
  Mic, Camera, QrCode, Scan, Nfc, Box, 
  Loader2, Upload, CheckCircle2, AlertCircle 
} from 'lucide-react';

interface VoiceMultimodalControllerProps {
  formId: string;
}

export function VoiceMultimodalController({ formId }: VoiceMultimodalControllerProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordedAudio, setRecordedAudio] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: voiceConfig } = useVoiceFormConfig(formId);
  const updateVoiceConfig = useUpdateVoiceConfig();
  const transcribeVoice = useTranscribeVoice();

  const { data: multimodalConfig } = useMultimodalConfig(formId);
  const updateMultimodalConfig = useUpdateMultimodalConfig();
  const ocrExtract = useOCRExtract();

  const { data: arConfig } = useARPreviewConfig(formId);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const audioChunks: BlobPart[] = [];
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        setRecordedAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleTranscribe = () => {
    if (recordedAudio) {
      transcribeVoice.mutate({ formId, audioBlob: recordedAudio });
    }
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      ocrExtract.mutate({ formId, image: file });
    }
  };

  return (
    <div className="space-y-6">
      <Tabs defaultValue="voice" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="voice">Voice Input</TabsTrigger>
          <TabsTrigger value="camera">Camera/OCR</TabsTrigger>
          <TabsTrigger value="nfc">NFC</TabsTrigger>
          <TabsTrigger value="ar">AR Preview</TabsTrigger>
        </TabsList>

        {/* Voice Input Tab */}
        <TabsContent value="voice" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mic className="h-5 w-5 text-blue-500" />
                Voice Form Configuration
              </CardTitle>
              <CardDescription>
                Enable voice input and configure transcription settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="voice-enabled">Enable Voice Input</Label>
                <Switch
                  id="voice-enabled"
                  checked={voiceConfig?.is_enabled}
                  onCheckedChange={(checked) => {
                    updateVoiceConfig.mutate({
                      formId,
                      config: { is_enabled: checked }
                    });
                  }}
                />
              </div>

              {voiceConfig?.is_enabled && (
                <>
                  <div className="space-y-2">
                    <Label>Transcription Engine</Label>
                    <Select
                      value={voiceConfig.transcription_engine}
                      onValueChange={(value) => {
                        updateVoiceConfig.mutate({
                          formId,
                          config: { transcription_engine: String(value) as 'whisper' | 'google' | 'azure' | 'aws' }
                        });
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="whisper">OpenAI Whisper</SelectItem>
                        <SelectItem value="google">Google Speech-to-Text</SelectItem>
                        <SelectItem value="azure">Azure Speech</SelectItem>
                        <SelectItem value="aws">AWS Transcribe</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="border rounded-lg p-4 space-y-4">
                    <h4 className="font-medium">Test Voice Input</h4>
                    
                    <div className="flex gap-2">
                      {!isRecording ? (
                        <Button onClick={startRecording}>
                          <Mic className="mr-2 h-4 w-4" />
                          Start Recording
                        </Button>
                      ) : (
                        <Button variant="destructive" onClick={stopRecording}>
                          <Mic className="mr-2 h-4 w-4 animate-pulse" />
                          Stop Recording
                        </Button>
                      )}

                      {recordedAudio && (
                        <Button
                          onClick={handleTranscribe}
                          disabled={transcribeVoice.isPending}
                        >
                          {transcribeVoice.isPending && (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          )}
                          Transcribe
                        </Button>
                      )}
                    </div>

                    {transcribeVoice.isSuccess && (
                      <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                        <div className="flex items-start gap-2">
                          <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
                          <div>
                            <p className="text-sm font-medium text-green-900">Transcription Complete</p>
                            <p className="text-sm text-green-700 mt-1">
                              {transcribeVoice.data?.transcription}
                            </p>
                            <p className="text-xs text-green-600 mt-1">
                              Confidence: {(transcribeVoice.data?.confidence_score * 100).toFixed(1)}%
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Camera/OCR Tab */}
        <TabsContent value="camera" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="h-5 w-5 text-green-500" />
                Camera & OCR Configuration
              </CardTitle>
              <CardDescription>
                Enable camera, QR/barcode scanning, and OCR extraction
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="camera-enabled">Camera Access</Label>
                  <Switch
                    id="camera-enabled"
                    checked={multimodalConfig?.camera_enabled}
                    onCheckedChange={(checked) => {
                      updateMultimodalConfig.mutate({
                        formId,
                        config: { camera_enabled: checked }
                      });
                    }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="qr-enabled">QR Scanner</Label>
                  <Switch
                    id="qr-enabled"
                    checked={multimodalConfig?.qr_scanner_enabled}
                    onCheckedChange={(checked) => {
                      updateMultimodalConfig.mutate({
                        formId,
                        config: { qr_scanner_enabled: checked }
                      });
                    }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="barcode-enabled">Barcode Scanner</Label>
                  <Switch
                    id="barcode-enabled"
                    checked={multimodalConfig?.barcode_scanner_enabled}
                    onCheckedChange={(checked) => {
                      updateMultimodalConfig.mutate({
                        formId,
                        config: { barcode_scanner_enabled: checked }
                      });
                    }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="ocr-enabled">OCR Extraction</Label>
                  <Switch
                    id="ocr-enabled"
                    checked={multimodalConfig?.ocr_enabled}
                    onCheckedChange={(checked) => {
                      updateMultimodalConfig.mutate({
                        formId,
                        config: { ocr_enabled: checked }
                      });
                    }}
                  />
                </div>
              </div>

              {multimodalConfig?.ocr_enabled && (
                <div className="border rounded-lg p-4 space-y-4">
                  <h4 className="font-medium">Test OCR Extraction</h4>
                  
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />

                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={ocrExtract.isPending}
                  >
                    {ocrExtract.isPending ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Upload className="mr-2 h-4 w-4" />
                    )}
                    Upload Image for OCR
                  </Button>

                  {ocrExtract.isSuccess && (
                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-start gap-2">
                        <Scan className="h-5 w-5 text-blue-600 mt-0.5" />
                        <div>
                          <p className="text-sm font-medium text-blue-900">OCR Complete</p>
                          <p className="text-sm text-blue-700 mt-1">
                            {ocrExtract.data?.extracted_text}
                          </p>
                          <p className="text-xs text-blue-600 mt-1">
                            Confidence: {(ocrExtract.data?.confidence_score * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* NFC Tab */}
        <TabsContent value="nfc" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Nfc className="h-5 w-5 text-orange-500" />
                NFC Tap-to-Fill
              </CardTitle>
              <CardDescription>
                Enable NFC for quick form filling
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="nfc-enabled">Enable NFC</Label>
                <Switch
                  id="nfc-enabled"
                  checked={multimodalConfig?.nfc_enabled}
                  onCheckedChange={(checked) => {
                    updateMultimodalConfig.mutate({
                      formId,
                      config: { nfc_enabled: checked }
                    });
                  }}
                />
              </div>

              {multimodalConfig?.nfc_enabled && (
                <div className="p-4 border rounded-lg bg-muted">
                  <p className="text-sm text-center text-muted-foreground">
                    NFC functionality requires compatible hardware and browser support
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* AR Preview Tab */}
        <TabsContent value="ar" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Box className="h-5 w-5 text-purple-500" />
                Augmented Reality Preview
              </CardTitle>
              <CardDescription>
                Enable AR preview for immersive form experiences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {arConfig ? (
                <>
                  <div className="flex items-center justify-between">
                    <Label>AR Preview Enabled</Label>
                    <Badge variant={arConfig.is_enabled ? 'default' : 'secondary'}>
                      {arConfig.is_enabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </div>

                  <div className="space-y-2">
                    <Label>Preview Type</Label>
                    <p className="text-sm text-muted-foreground">{arConfig.preview_type}</p>
                  </div>

                  <div className="space-y-2">
                    <Label>3D Model</Label>
                    <p className="text-sm text-muted-foreground break-all">{arConfig.model_url}</p>
                  </div>
                </>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No AR configuration found
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
