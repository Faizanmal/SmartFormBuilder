"use client";

import { useState, useRef } from "react";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Upload, X, FileIcon, ImageIcon, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import type { FormField } from "@/types";

interface FileUploadFieldProps {
  field: FormField;
  value: File | File[] | null;
  onChange: (value: File | File[] | null) => void;
}

interface FilePreview {
  file: File;
  preview?: string;
}

export function FileUploadField({ field, value, onChange }: FileUploadFieldProps) {
  const [previews, setPreviews] = useState<FilePreview[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const allowMultiple = field.allowMultiple ?? false;
  const maxFiles = field.maxFiles ?? 5;
  const accept = field.validation?.accept ?? "*";
  const maxSize = field.validation?.maxSize ?? 10 * 1024 * 1024; // 10MB default

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const isImage = (file: File) => file.type.startsWith('image/');

  const handleFiles = (files: FileList | null) => {
    if (!files) return;

    const fileArray = Array.from(files);
    const validFiles: File[] = [];

    for (const file of fileArray) {
      // Check file size
      if (file.size > maxSize) {
        alert(`${file.name} is too large. Maximum size is ${formatFileSize(maxSize)}`);
        continue;
      }
      validFiles.push(file);
    }

    if (!allowMultiple) {
      // Single file mode
      if (validFiles.length > 0) {
        const file = validFiles[0];
        const preview: FilePreview = { file };
        
        if (isImage(file)) {
          preview.preview = URL.createObjectURL(file);
        }
        
        setPreviews([preview]);
        onChange(file);
      }
    } else {
      // Multiple files mode
      const currentFiles = Array.isArray(value) ? value : value ? [value] : [];
      const newFiles = [...currentFiles, ...validFiles].slice(0, maxFiles);
      
      const newPreviews = newFiles.map(file => {
        const preview: FilePreview = { file };
        if (isImage(file)) {
          preview.preview = URL.createObjectURL(file);
        }
        return preview;
      });
      
      setPreviews(newPreviews);
      onChange(newFiles);
    }
  };

  const removeFile = (index: number) => {
    if (previews[index]?.preview) {
      URL.revokeObjectURL(previews[index].preview!);
    }
    
    const newPreviews = previews.filter((_, i) => i !== index);
    setPreviews(newPreviews);
    
    if (newPreviews.length === 0) {
      onChange(null);
    } else if (allowMultiple) {
      onChange(newPreviews.map(p => p.file));
    } else {
      onChange(newPreviews[0]?.file ?? null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const getFileIcon = (file: File) => {
    if (isImage(file)) return <ImageIcon className="w-8 h-8 text-blue-500" />;
    if (file.type.includes('pdf')) return <FileText className="w-8 h-8 text-red-500" />;
    return <FileIcon className="w-8 h-8 text-gray-500" />;
  };

  return (
    <div className="space-y-2">
      <Label htmlFor={field.id}>
        {field.label}
        {field.required && <span className="text-red-500 ml-1">*</span>}
      </Label>
      
      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors",
          isDragging ? "border-primary bg-primary/5" : "border-gray-300 hover:border-primary/50",
          previews.length > 0 && "border-solid"
        )}
      >
        <input
          ref={inputRef}
          type="file"
          id={field.id}
          accept={accept}
          multiple={allowMultiple}
          onChange={(e) => handleFiles(e.target.files)}
          className="hidden"
        />
        
        {previews.length === 0 ? (
          <div className="space-y-2">
            <Upload className="w-10 h-10 mx-auto text-gray-400" />
            <div>
              <p className="text-sm font-medium">
                Click to upload or drag and drop
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {accept !== "*" && `Accepted: ${accept}`}
                {allowMultiple && ` (Max ${maxFiles} files)`}
              </p>
              <p className="text-xs text-muted-foreground">
                Max size: {formatFileSize(maxSize)}
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {previews.map((preview, index) => (
              <div 
                key={index}
                className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg"
                onClick={(e) => e.stopPropagation()}
              >
                {preview.preview ? (
                  <img 
                    src={preview.preview} 
                    alt={preview.file.name}
                    className="w-12 h-12 object-cover rounded"
                  />
                ) : (
                  getFileIcon(preview.file)
                )}
                <div className="flex-1 text-left min-w-0">
                  <p className="text-sm font-medium truncate">{preview.file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatFileSize(preview.file.size)}
                  </p>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeFile(index)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            ))}
            {allowMultiple && previews.length < maxFiles && (
              <p className="text-xs text-muted-foreground">
                Click to add more files ({previews.length}/{maxFiles})
              </p>
            )}
          </div>
        )}
      </div>
      
      {field.help && (
        <p className="text-xs text-muted-foreground">{field.help}</p>
      )}
    </div>
  );
}
