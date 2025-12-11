"use client";

import { cn } from "@/lib/utils";
import { Check } from "lucide-react";
import type { FormStep } from "@/types";

interface FormProgressProps {
  steps: FormStep[];
  currentStep: number;
  completedSteps: number[];
  onStepClick?: (stepIndex: number) => void;
  allowNavigation?: boolean;
}

export function FormProgress({
  steps,
  currentStep,
  completedSteps,
  onStepClick,
  allowNavigation = false
}: FormProgressProps) {
  const handleStepClick = (index: number) => {
    if (allowNavigation && onStepClick) {
      // Can only navigate to completed steps or the next available step
      if (completedSteps.includes(index) || index === currentStep || index <= Math.max(...completedSteps, -1) + 1) {
        onStepClick(index);
      }
    }
  };

  return (
    <div className="w-full">
      {/* Progress bar */}
      <div className="relative">
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200">
          <div
            className="h-full bg-primary transition-all duration-300"
            style={{
              width: `${((currentStep) / (steps.length - 1)) * 100}%`
            }}
          />
        </div>

        {/* Step indicators */}
        <div className="relative flex justify-between">
          {steps.map((step, index) => {
            const isCompleted = completedSteps.includes(index);
            const isCurrent = index === currentStep;
            const isClickable = allowNavigation && (isCompleted || index <= Math.max(...completedSteps, -1) + 1);

            return (
              <div
                key={step.id}
                className={cn(
                  "flex flex-col items-center",
                  isClickable && "cursor-pointer"
                )}
                onClick={() => handleStepClick(index)}
              >
                {/* Circle indicator */}
                <div
                  className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-200",
                    isCompleted && "bg-primary text-primary-foreground",
                    isCurrent && !isCompleted && "bg-primary text-primary-foreground ring-4 ring-primary/20",
                    !isCurrent && !isCompleted && "bg-gray-200 text-gray-500"
                  )}
                >
                  {isCompleted ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    index + 1
                  )}
                </div>

                {/* Step title */}
                <div className="mt-2 text-center">
                  <p
                    className={cn(
                      "text-sm font-medium",
                      (isCurrent || isCompleted) ? "text-primary" : "text-gray-500"
                    )}
                  >
                    {step.title}
                  </p>
                  {step.description && (
                    <p className="text-xs text-muted-foreground mt-0.5 max-w-[120px]">
                      {step.description}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

interface FormProgressBarProps {
  currentStep: number;
  totalSteps: number;
  showPercentage?: boolean;
}

export function FormProgressBar({
  currentStep,
  totalSteps,
  showPercentage = true
}: FormProgressBarProps) {
  const percentage = Math.round(((currentStep + 1) / totalSteps) * 100);

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-muted-foreground">
          Step {currentStep + 1} of {totalSteps}
        </span>
        {showPercentage && (
          <span className="text-sm font-medium">{percentage}%</span>
        )}
      </div>
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-primary transition-all duration-300 rounded-full"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
