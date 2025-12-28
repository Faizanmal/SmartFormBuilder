"use client";

import React from "react";
import { FormField, ConditionalRule } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Plus, Trash2, Eye, EyeOff } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface ConditionalLogicBuilderProps {
  field: FormField;
  allFields: FormField[];
  onRulesChange: (rules: ConditionalRule[]) => void;
}

type ConditionOperator = 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'is_empty' | 'is_not_empty';
type RuleAction = 'show' | 'hide' | 'require' | 'unrequire';

export function ConditionalLogicBuilder({ 
  field, 
  allFields, 
  onRulesChange 
}: ConditionalLogicBuilderProps) {
  const rules = field.conditionalRules || [];

  // Filter out current field and fields that come after it
  const availableFields = allFields.filter(f => f.id !== field.id);

  const addRule = () => {
    const newRule: ConditionalRule = {
      id: `rule_${Date.now()}`,
      fieldId: '',
      operator: 'equals',
      value: '',
      action: 'show',
    };
    onRulesChange([...rules, newRule]);
  };

  const updateRule = (ruleId: string, updates: Partial<ConditionalRule>) => {
    onRulesChange(rules.map(r => r.id === ruleId ? { ...r, ...updates } : r));
  };

  const deleteRule = (ruleId: string) => {
    onRulesChange(rules.filter(r => r.id !== ruleId));
  };

  const getOperatorLabel = (operator: string) => {
    const labels: Record<string, string> = {
      equals: 'equals',
      not_equals: 'does not equal',
      contains: 'contains',
      not_contains: 'does not contain',
      greater_than: 'is greater than',
      less_than: 'is less than',
      is_empty: 'is empty',
      is_not_empty: 'is not empty',
    };
    return labels[operator] || operator;
  };

  const getActionLabel = (action: string) => {
    const labels: Record<string, string> = {
      show: 'Show this field',
      hide: 'Hide this field',
      require: 'Make this field required',
      unrequire: 'Make this field optional',
    };
    return labels[action] || action;
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'show':
        return <Eye className="h-4 w-4" />;
      case 'hide':
        return <EyeOff className="h-4 w-4" />;
      default:
        return null;
    }
  };

  const needsValue = (operator: string) => {
    return !['is_empty', 'is_not_empty'].includes(operator);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold">Conditional Logic</h3>
          <p className="text-sm text-muted-foreground">
            Show or hide this field based on other fields
          </p>
        </div>
        <Button onClick={addRule} size="sm" variant="outline">
          <Plus className="h-4 w-4 mr-2" />
          Add Rule
        </Button>
      </div>

      {rules.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground text-center">
              No conditional rules yet. Click &quot;Add Rule&quot; to get started.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {rules.map((rule, index) => {
            const selectedField = availableFields.find(f => f.id === rule.fieldId);
            
            return (
              <Card key={rule.id}>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-sm font-medium">Rule {index + 1}</CardTitle>
                    <div className="flex-1" />
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteRule(rule.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Action */}
                  <div>
                    <Label>Action</Label>
                    <Select
                      value={rule.action}
                      onValueChange={(value) => updateRule(rule.id, { action: value as RuleAction })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="show">
                          <div className="flex items-center gap-2">
                            <Eye className="h-4 w-4" />
                            Show this field
                          </div>
                        </SelectItem>
                        <SelectItem value="hide">
                          <div className="flex items-center gap-2">
                            <EyeOff className="h-4 w-4" />
                            Hide this field
                          </div>
                        </SelectItem>
                        <SelectItem value="require">Make this field required</SelectItem>
                        <SelectItem value="unrequire">Make this field optional</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* When */}
                  <div>
                    <Label>When field</Label>
                    <Select
                      value={rule.fieldId}
                      onValueChange={(value) => updateRule(rule.id, { fieldId: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a field..." />
                      </SelectTrigger>
                      <SelectContent>
                        {availableFields.map(field => (
                          <SelectItem key={field.id} value={field.id}>
                            {field.label} ({field.type})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Operator */}
                  <div>
                    <Label>Condition</Label>
                    <Select
                      value={rule.operator}
                      onValueChange={(value) => updateRule(rule.id, { operator: value as ConditionOperator })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="equals">equals</SelectItem>
                        <SelectItem value="not_equals">does not equal</SelectItem>
                        <SelectItem value="contains">contains</SelectItem>
                        <SelectItem value="not_contains">does not contain</SelectItem>
                        {selectedField?.type === 'number' && (
                          <>
                            <SelectItem value="greater_than">is greater than</SelectItem>
                            <SelectItem value="less_than">is less than</SelectItem>
                          </>
                        )}
                        <SelectItem value="is_empty">is empty</SelectItem>
                        <SelectItem value="is_not_empty">is not empty</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Value */}
                  {needsValue(rule.operator) && (
                    <div>
                      <Label>Value</Label>
                      {selectedField?.type === 'select' || selectedField?.type === 'radio' ? (
                        <Select
                          value={rule.value}
                          onValueChange={(value) => updateRule(rule.id, { value })}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select a value..." />
                          </SelectTrigger>
                          <SelectContent>
                            {selectedField.options?.map(opt => (
                              <SelectItem key={opt.value} value={opt.value}>
                                {opt.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      ) : (
                        <Input
                          type={selectedField?.type === 'number' ? 'number' : 'text'}
                          value={rule.value}
                          onChange={(e) => updateRule(rule.id, { value: e.target.value })}
                          placeholder="Enter value..."
                        />
                      )}
                    </div>
                  )}

                  {/* Rule Summary */}
                  {rule.fieldId && (
                    <div className="p-3 bg-muted rounded-lg">
                      <p className="text-sm">
                        <span className="font-medium">{getActionLabel(rule.action)}</span>
                        {' when '}
                        <span className="font-medium">{selectedField?.label}</span>
                        {' '}
                        {getOperatorLabel(rule.operator)}
                        {needsValue(rule.operator) && rule.value && (
                          <>
                            {' '}
                            <span className="font-medium">&quot;{rule.value}&quot;</span>
                          </>
                        )}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
