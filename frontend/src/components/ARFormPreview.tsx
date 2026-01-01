/**
 * AR/VR Form Preview Component
 * Uses WebXR API for augmented reality form visualization
 */
'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Slider } from '@/components/ui/slider';
import {
  Glasses,
  Camera,
  CameraOff,
  RotateCw,
  ZoomIn,
  ZoomOut,
  Move,
  Smartphone,
  Monitor,
  AlertCircle,
  CheckCircle,
  Maximize,
  Minimize,
  Settings,
  Sparkles,
  Box,
  Layers,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface FormField {
  id: string;
  type: string;
  label: string;
  placeholder?: string;
  required?: boolean;
  options?: string[];
}

interface ARFormPreviewProps {
  title: string;
  description?: string;
  fields: FormField[];
  className?: string;
}

interface ARState {
  isSupported: boolean;
  isActive: boolean;
  position: { x: number; y: number; z: number };
  rotation: { x: number; y: number; z: number };
  scale: number;
}

export function ARFormPreview({
  title,
  description,
  fields,
  className,
}: ARFormPreviewProps) {
  const [arState, setArState] = useState<ARState>({
    isSupported: false,
    isActive: false,
    position: { x: 0, y: 0, z: -2 },
    rotation: { x: 0, y: 0, z: 0 },
    scale: 1,
  });
  
  const [showSettings, setShowSettings] = useState(false);
  const [previewMode, setPreviewMode] = useState<'2d' | '3d' | 'ar'>('2d');
  const [cameraActive, setCameraActive] = useState(false);
  const [arError, setArError] = useState<string | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);

  // Check AR support
  useEffect(() => {
    const checkARSupport = async () => {
      if ('xr' in navigator) {
        try {
          const isSupported = await (navigator as Navigator & { xr: { isSessionSupported: (mode: string) => Promise<boolean> } }).xr.isSessionSupported('immersive-ar');
          setArState(prev => ({ ...prev, isSupported }));
        } catch {
          setArState(prev => ({ ...prev, isSupported: false }));
        }
      }
    };
    
    checkARSupport();
  }, []);

  // Start camera for AR simulation
  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setCameraActive(true);
        setArError(null);
      }
    } catch (error) {
      setArError('Unable to access camera. Please check permissions.');
      console.error('Camera error:', error);
    }
  }, []);

  // Stop camera
  const stopCamera = useCallback(() => {
    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  }, []);

  // Handle mode change
  const handleModeChange = useCallback((mode: '2d' | '3d' | 'ar') => {
    setPreviewMode(mode);
    
    if (mode === 'ar') {
      startCamera();
    } else {
      stopCamera();
    }
  }, [startCamera, stopCamera]);

  // Render 3D form visualization
  const render3DPreview = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const { width, height } = canvas;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw 3D-like form preview
    const formWidth = 300 * arState.scale;
    const formHeight = (100 + fields.length * 60) * arState.scale;
    const formX = width / 2 - formWidth / 2 + arState.position.x * 50;
    const formY = height / 2 - formHeight / 2 + arState.position.y * 50;
    
    // Apply rotation transform
    ctx.save();
    ctx.translate(width / 2, height / 2);
    ctx.rotate((arState.rotation.y * Math.PI) / 180);
    ctx.translate(-width / 2, -height / 2);
    
    // Draw form shadow
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.fillRect(formX + 8, formY + 8, formWidth, formHeight);
    
    // Draw form background
    ctx.fillStyle = '#ffffff';
    ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';
    ctx.shadowBlur = 20;
    ctx.shadowOffsetX = 5;
    ctx.shadowOffsetY = 5;
    ctx.fillRect(formX, formY, formWidth, formHeight);
    ctx.shadowBlur = 0;
    
    // Draw form border
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1;
    ctx.strokeRect(formX, formY, formWidth, formHeight);
    
    // Draw title
    ctx.fillStyle = '#111827';
    ctx.font = `bold ${16 * arState.scale}px system-ui`;
    ctx.fillText(title, formX + 20, formY + 30);
    
    // Draw description
    if (description) {
      ctx.fillStyle = '#6b7280';
      ctx.font = `${12 * arState.scale}px system-ui`;
      ctx.fillText(description.slice(0, 40) + '...', formX + 20, formY + 50);
    }
    
    // Draw fields
    fields.forEach((field, index) => {
      const fieldY = formY + 70 + index * 60 * arState.scale;
      
      // Field label
      ctx.fillStyle = '#374151';
      ctx.font = `${12 * arState.scale}px system-ui`;
      ctx.fillText(
        field.label + (field.required ? ' *' : ''),
        formX + 20,
        fieldY
      );
      
      // Field input box
      ctx.fillStyle = '#f9fafb';
      ctx.fillRect(formX + 20, fieldY + 5, formWidth - 40, 30 * arState.scale);
      ctx.strokeStyle = '#d1d5db';
      ctx.strokeRect(formX + 20, fieldY + 5, formWidth - 40, 30 * arState.scale);
      
      // Field placeholder
      ctx.fillStyle = '#9ca3af';
      ctx.font = `${11 * arState.scale}px system-ui`;
      ctx.fillText(
        field.placeholder || `Enter ${field.label.toLowerCase()}`,
        formX + 25,
        fieldY + 25
      );
    });
    
    // Draw submit button
    const buttonY = formY + 70 + fields.length * 60 * arState.scale + 10;
    ctx.fillStyle = '#3b82f6';
    ctx.beginPath();
    ctx.roundRect(formX + 20, buttonY, formWidth - 40, 36 * arState.scale, 6);
    ctx.fill();
    
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold ${14 * arState.scale}px system-ui`;
    ctx.textAlign = 'center';
    ctx.fillText('Submit', formX + formWidth / 2, buttonY + 23);
    ctx.textAlign = 'left';
    
    ctx.restore();
  }, [arState, fields, title, description]);

  // Animation loop for AR/3D mode
  useEffect(() => {
    if (previewMode === '2d') {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      return;
    }
    
    const animate = () => {
      render3DPreview();
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [previewMode, render3DPreview]);

  // Handle rotation via dragging
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (e.buttons !== 1) return;
    
    setArState(prev => ({
      ...prev,
      rotation: {
        ...prev.rotation,
        y: prev.rotation.y + e.movementX * 0.5,
        x: Math.max(-30, Math.min(30, prev.rotation.x + e.movementY * 0.5)),
      },
    }));
  }, []);

  // Reset view
  const resetView = useCallback(() => {
    setArState(prev => ({
      ...prev,
      position: { x: 0, y: 0, z: -2 },
      rotation: { x: 0, y: 0, z: 0 },
      scale: 1,
    }));
  }, []);

  // Render 2D field preview
  const render2DField = (field: FormField) => {
    switch (field.type) {
      case 'textarea':
        return (
          <textarea
            className="w-full p-2 border rounded-md bg-muted/50"
            placeholder={field.placeholder}
            rows={3}
            disabled
          />
        );
      case 'select':
        return (
          <select className="w-full p-2 border rounded-md bg-muted/50" disabled>
            <option>{field.placeholder || 'Select...'}</option>
            {(field.options || []).map((opt, i) => (
              <option key={i}>{opt}</option>
            ))}
          </select>
        );
      case 'checkbox':
        return (
          <label className="flex items-center gap-2">
            <input type="checkbox" disabled className="h-4 w-4" />
            <span className="text-sm">{field.placeholder || field.label}</span>
          </label>
        );
      default:
        return (
          <input
            type={field.type}
            className="w-full p-2 border rounded-md bg-muted/50"
            placeholder={field.placeholder}
            disabled
          />
        );
    }
  };

  return (
    <Card className={cn('overflow-hidden', className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Glasses className="h-5 w-5" />
            AR/VR Preview
          </CardTitle>
          <CardDescription>
            Visualize your form in 2D, 3D, or augmented reality
          </CardDescription>
        </div>
        
        <div className="flex items-center gap-2">
          {arState.isSupported && (
            <Badge variant="outline" className="text-green-600 border-green-600">
              <CheckCircle className="h-3 w-3 mr-1" />
              WebXR Supported
            </Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        {/* Mode Selector */}
        <div className="flex items-center justify-between px-4 py-2 border-b bg-muted/50">
          <div className="flex gap-1">
            <Button
              variant={previewMode === '2d' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleModeChange('2d')}
            >
              <Monitor className="h-4 w-4 mr-1" />
              2D
            </Button>
            <Button
              variant={previewMode === '3d' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleModeChange('3d')}
            >
              <Box className="h-4 w-4 mr-1" />
              3D
            </Button>
            <Button
              variant={previewMode === 'ar' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleModeChange('ar')}
            >
              <Glasses className="h-4 w-4 mr-1" />
              AR
            </Button>
          </div>
          
          <div className="flex items-center gap-1">
            {(previewMode === '3d' || previewMode === 'ar') && (
              <>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setArState(prev => ({ ...prev, scale: Math.max(0.5, prev.scale - 0.1) }))}
                >
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setArState(prev => ({ ...prev, scale: Math.min(2, prev.scale + 0.1) }))}
                >
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  onClick={resetView}
                >
                  <RotateCw className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setShowSettings(!showSettings)}
                >
                  <Settings className="h-4 w-4" />
                </Button>
              </>
            )}
          </div>
        </div>
        
        {/* Settings Panel */}
        {showSettings && (previewMode === '3d' || previewMode === 'ar') && (
          <div className="px-4 py-3 border-b bg-background space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Scale: {arState.scale.toFixed(1)}x</label>
              <Slider
                value={[arState.scale]}
                onValueChange={([value]) => setArState(prev => ({ ...prev, scale: value }))}
                min={0.5}
                max={2}
                step={0.1}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Rotation Y: {arState.rotation.y.toFixed(0)}°</label>
              <Slider
                value={[arState.rotation.y]}
                onValueChange={([value]) => setArState(prev => ({ 
                  ...prev, 
                  rotation: { ...prev.rotation, y: value } 
                }))}
                min={-180}
                max={180}
                step={1}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Position X</label>
              <Slider
                value={[arState.position.x]}
                onValueChange={([value]) => setArState(prev => ({ 
                  ...prev, 
                  position: { ...prev.position, x: value } 
                }))}
                min={-3}
                max={3}
                step={0.1}
              />
            </div>
          </div>
        )}
        
        {/* Error Alert */}
        {arError && (
          <Alert variant="destructive" className="m-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{arError}</AlertDescription>
          </Alert>
        )}
        
        {/* Preview Area */}
        <div className="relative min-h-[400px] bg-gradient-to-br from-gray-100 to-gray-200">
          {/* 2D Preview */}
          {previewMode === '2d' && (
            <div className="p-6">
              <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-xl font-semibold mb-2">{title}</h3>
                {description && (
                  <p className="text-muted-foreground text-sm mb-4">{description}</p>
                )}
                
                <div className="space-y-4">
                  {fields.map((field) => (
                    <div key={field.id} className="space-y-1">
                      <label className="text-sm font-medium">
                        {field.label}
                        {field.required && <span className="text-red-500 ml-1">*</span>}
                      </label>
                      {render2DField(field)}
                    </div>
                  ))}
                </div>
                
                <Button className="w-full mt-6">Submit</Button>
              </div>
            </div>
          )}
          
          {/* 3D Preview */}
          {previewMode === '3d' && (
            <div 
              className="w-full h-[400px] cursor-grab active:cursor-grabbing"
              onMouseMove={handleMouseMove}
            >
              <canvas
                ref={canvasRef}
                width={800}
                height={400}
                className="w-full h-full"
              />
              
              <div className="absolute bottom-4 left-4 text-xs text-muted-foreground bg-white/80 px-2 py-1 rounded">
                <Move className="h-3 w-3 inline mr-1" />
                Drag to rotate
              </div>
            </div>
          )}
          
          {/* AR Preview */}
          {previewMode === 'ar' && (
            <div className="relative w-full h-[400px]">
              {/* Camera Feed */}
              <video
                ref={videoRef}
                className="absolute inset-0 w-full h-full object-cover"
                playsInline
                muted
              />
              
              {/* AR Overlay Canvas */}
              <canvas
                ref={canvasRef}
                width={800}
                height={400}
                className="absolute inset-0 w-full h-full"
                onMouseMove={handleMouseMove}
              />
              
              {/* Camera Controls */}
              <div className="absolute bottom-4 right-4 flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={cameraActive ? stopCamera : startCamera}
                >
                  {cameraActive ? (
                    <>
                      <CameraOff className="h-4 w-4 mr-1" />
                      Stop Camera
                    </>
                  ) : (
                    <>
                      <Camera className="h-4 w-4 mr-1" />
                      Start Camera
                    </>
                  )}
                </Button>
              </div>
              
              {!cameraActive && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50 text-white">
                  <div className="text-center">
                    <Glasses className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="text-lg font-medium">AR Preview</p>
                    <p className="text-sm opacity-70 mb-4">
                      Enable camera to see your form in augmented reality
                    </p>
                    <Button onClick={startCamera}>
                      <Camera className="h-4 w-4 mr-2" />
                      Enable Camera
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Info Footer */}
        <div className="px-4 py-2 border-t bg-muted/50 flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <Layers className="h-3 w-3" />
            {fields.length} fields
          </div>
          <div className="flex items-center gap-2">
            <Sparkles className="h-3 w-3" />
            {previewMode.toUpperCase()} Mode
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default ARFormPreview;
