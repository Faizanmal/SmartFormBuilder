"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Star, Heart, ThumbsUp } from "lucide-react";
import { cn } from "@/lib/utils";
import type { FormField } from "@/types";

interface RatingFieldProps {
  field: FormField;
  value: number;
  onChange: (value: number) => void;
}

export function RatingField({ field, value, onChange }: RatingFieldProps) {
  const [hovered, setHovered] = useState<number | null>(null);
  const maxRating = field.maxRating ?? 5;
  const iconType = field.ratingIcon ?? 'star';

  const getIcon = (filled: boolean, index: number) => {
    const isActive = hovered !== null ? index <= hovered : index <= (value || 0);
    const className = cn(
      "w-8 h-8 cursor-pointer transition-all duration-150",
      isActive ? "fill-current" : "fill-none",
      iconType === 'star' && (isActive ? "text-yellow-400" : "text-gray-300 hover:text-yellow-200"),
      iconType === 'heart' && (isActive ? "text-red-500" : "text-gray-300 hover:text-red-200"),
      iconType === 'thumbsup' && (isActive ? "text-blue-500" : "text-gray-300 hover:text-blue-200")
    );

    switch (iconType) {
      case 'heart':
        return <Heart className={className} />;
      case 'thumbsup':
        return <ThumbsUp className={className} />;
      default:
        return <Star className={className} />;
    }
  };

  return (
    <div className="space-y-2">
      <Label htmlFor={field.id}>
        {field.label}
        {field.required && <span className="text-red-500 ml-1">*</span>}
      </Label>
      <div 
        className="flex gap-1"
        onMouseLeave={() => setHovered(null)}
      >
        {Array.from({ length: maxRating }, (_, i) => (
          <button
            key={i + 1}
            type="button"
            onClick={() => onChange(i + 1)}
            onMouseEnter={() => setHovered(i + 1)}
            className="focus:outline-none focus:ring-2 focus:ring-primary rounded"
          >
            {getIcon(i + 1 <= (value || 0), i + 1)}
          </button>
        ))}
        {value && (
          <span className="ml-2 text-sm text-muted-foreground self-center">
            {value} / {maxRating}
          </span>
        )}
      </div>
      {field.help && (
        <p className="text-xs text-muted-foreground">{field.help}</p>
      )}
    </div>
  );
}
