'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Workflow,
  Plus,
  Play,
  Pause,
  Mail,
  MessageSquare,
  Webhook,
  Users,
  Clock,
  Settings,
  Trash2,
  ChevronRight,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';

interface WorkflowAction {
  type: string;
  config: Record<string, unknown>;
  delay_minutes?: number;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'paused' | 'archived';
  trigger_type: string;
  trigger_conditions: Record<string, unknown>;
  actions: WorkflowAction[];
  is_active: boolean;
  total_triggered: number;
  total_completed: number;
  total_failed: number;
}

interface WorkflowBuilderProps {
  formId: string;
}

const ACTION_TYPES = [
  { value: 'send_email', label: 'Send Email', icon: Mail },
  { value: 'send_sms', label: 'Send SMS', icon: MessageSquare },
  { value: 'webhook', label: 'Call Webhook', icon: Webhook },
  { value: 'crm_sync', label: 'Sync to CRM', icon: Users },
  { value: 'delay', label: 'Wait/Delay', icon: Clock },
];

const TRIGGER_TYPES = [
  { value: 'submission', label: 'Form Submission' },
  { value: 'score_threshold', label: 'Lead Score Threshold' },
  { value: 'abandonment', label: 'Form Abandonment' },
  { value: 'time_delay', label: 'Time After Previous' },
];

export function WorkflowBuilder({ formId }: WorkflowBuilderProps) {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [newWorkflow, setNewWorkflow] = useState({
    name: '',
    description: '',
    trigger_type: 'submission',
    actions: [] as WorkflowAction[],
  });

  useEffect(() => {
    fetchWorkflows();
  }, [formId]);

  const fetchWorkflows = async () => {
    try {
      const response = await fetch(`/api/v1/automation/workflows/?form_id=${formId}`);
      const data = await response.json();
      setWorkflows(data);
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
    } finally {
      setLoading(false);
    }
  };

  const createWorkflow = async () => {
    try {
      await fetch('/api/v1/automation/workflows/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          form_id: formId,
          ...newWorkflow,
        }),
      });
      setShowCreateDialog(false);
      setNewWorkflow({ name: '', description: '', trigger_type: 'submission', actions: [] });
      fetchWorkflows();
    } catch (error) {
      console.error('Failed to create workflow:', error);
    }
  };

  const activateWorkflow = async (workflowId: string) => {
    try {
      await fetch(`/api/v1/automation/workflows/${workflowId}/activate/`, {
        method: 'POST',
      });
      fetchWorkflows();
    } catch (error) {
      console.error('Failed to activate workflow:', error);
    }
  };

  const pauseWorkflow = async (workflowId: string) => {
    try {
      await fetch(`/api/v1/automation/workflows/${workflowId}/pause/`, {
        method: 'POST',
      });
      fetchWorkflows();
    } catch (error) {
      console.error('Failed to pause workflow:', error);
    }
  };

  const deleteWorkflow = async (workflowId: string) => {
    if (!confirm('Are you sure you want to delete this workflow?')) return;
    try {
      await fetch(`/api/v1/automation/workflows/${workflowId}/`, {
        method: 'DELETE',
      });
      fetchWorkflows();
    } catch (error) {
      console.error('Failed to delete workflow:', error);
    }
  };

  const addAction = () => {
    setNewWorkflow(prev => ({
      ...prev,
      actions: [...prev.actions, { type: 'send_email', config: {} }],
    }));
  };

  const removeAction = (index: number) => {
    setNewWorkflow(prev => ({
      ...prev,
      actions: prev.actions.filter((_, i) => i !== index),
    }));
  };

  const updateAction = (index: number, action: WorkflowAction) => {
    setNewWorkflow(prev => ({
      ...prev,
      actions: prev.actions.map((a, i) => i === index ? action : a),
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'default';
      case 'paused': return 'secondary';
      case 'draft': return 'outline';
      default: return 'outline';
    }
  };

  const getActionIcon = (type: string) => {
    const action = ACTION_TYPES.find(a => a.value === type);
    return action?.icon || Settings;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Workflow className="h-6 w-6 text-primary" />
            Nurturing Workflows
          </h2>
          <p className="text-muted-foreground">Automate follow-ups and lead nurturing</p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Workflow
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create New Workflow</DialogTitle>
              <DialogDescription>
                Build an automated workflow to nurture leads
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Workflow Name</Label>
                  <Input
                    placeholder="e.g., Welcome Sequence"
                    value={newWorkflow.name}
                    onChange={(e) => setNewWorkflow({ ...newWorkflow, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Trigger</Label>
                  <Select
                    value={newWorkflow.trigger_type}
                    onValueChange={(value) => setNewWorkflow({ ...newWorkflow, trigger_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {TRIGGER_TYPES.map((trigger) => (
                        <SelectItem key={trigger.value} value={trigger.value}>
                          {trigger.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Description</Label>
                <Textarea
                  placeholder="Describe what this workflow does..."
                  value={newWorkflow.description}
                  onChange={(e) => setNewWorkflow({ ...newWorkflow, description: e.target.value })}
                />
              </div>

              {/* Actions */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label>Actions</Label>
                  <Button type="button" variant="outline" size="sm" onClick={addAction}>
                    <Plus className="h-3 w-3 mr-1" />
                    Add Action
                  </Button>
                </div>

                {newWorkflow.actions.length === 0 ? (
                  <div className="text-center py-8 border border-dashed rounded-lg">
                    <p className="text-muted-foreground">No actions yet. Add an action to get started.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {newWorkflow.actions.map((action, index) => {
                      const Icon = getActionIcon(action.type);
                      return (
                        <div key={index} className="flex items-center gap-3 p-3 border rounded-lg">
                          <div className="flex items-center gap-2 flex-1">
                            <div className="p-2 bg-muted rounded">
                              <Icon className="h-4 w-4" />
                            </div>
                            <Select
                              value={action.type}
                              onValueChange={(value) => updateAction(index, { ...action, type: value })}
                            >
                              <SelectTrigger className="w-48">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {ACTION_TYPES.map((type) => (
                                  <SelectItem key={type.value} value={type.value}>
                                    {type.label}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            {action.type === 'delay' && (
                              <div className="flex items-center gap-2">
                                <Input
                                  type="number"
                                  className="w-20"
                                  placeholder="0"
                                  value={action.delay_minutes || ''}
                                  onChange={(e) => updateAction(index, { ...action, delay_minutes: parseInt(e.target.value) })}
                                />
                                <span className="text-sm text-muted-foreground">minutes</span>
                              </div>
                            )}
                          </div>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeAction(index)}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button onClick={createWorkflow} disabled={!newWorkflow.name}>
                Create Workflow
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Workflows List */}
      {workflows.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Workflow className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-medium">No workflows yet</p>
            <p className="text-muted-foreground mb-4">Create your first workflow to automate lead nurturing</p>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Workflow
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {workflows.map((workflow) => (
            <Card key={workflow.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{workflow.name}</h3>
                      <Badge variant={getStatusColor(workflow.status)}>
                        {workflow.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{workflow.description}</p>
                    <div className="flex items-center gap-4 mt-2 text-sm">
                      <span className="flex items-center gap-1">
                        <Play className="h-3 w-3" />
                        {workflow.total_triggered} triggered
                      </span>
                      <span className="flex items-center gap-1 text-green-600">
                        <CheckCircle className="h-3 w-3" />
                        {workflow.total_completed} completed
                      </span>
                      {workflow.total_failed > 0 && (
                        <span className="flex items-center gap-1 text-red-600">
                          <AlertCircle className="h-3 w-3" />
                          {workflow.total_failed} failed
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {workflow.status === 'active' ? (
                      <Button variant="outline" size="sm" onClick={() => pauseWorkflow(workflow.id)}>
                        <Pause className="h-4 w-4" />
                      </Button>
                    ) : (
                      <Button variant="outline" size="sm" onClick={() => activateWorkflow(workflow.id)}>
                        <Play className="h-4 w-4" />
                      </Button>
                    )}
                    <Button variant="outline" size="sm" onClick={() => setSelectedWorkflow(workflow)}>
                      <Settings className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => deleteWorkflow(workflow.id)}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

export default WorkflowBuilder;
