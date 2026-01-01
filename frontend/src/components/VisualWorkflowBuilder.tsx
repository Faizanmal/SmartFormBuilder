/**
 * Visual Workflow Automation Builder
 * Drag-and-drop workflow creation with nodes and connections
 */
'use client';

import React, { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import {
  Play,
  Plus,
  Trash2,
  Settings,
  Save,
  Copy,
  Undo,
  Redo,
  ZoomIn,
  ZoomOut,
  Maximize2,
  GripVertical,
  ArrowRight,
  ArrowDown,
  Mail,
  MessageSquare,
  Database,
  Webhook,
  Clock,
  Filter,
  GitBranch,
  Repeat,
  Bell,
  FileText,
  Code,
  Cloud,
  Zap,
  CheckCircle,
  AlertCircle,
  XCircle,
  Loader2,
  ChevronRight,
  Link2,
  Unlink,
  Eye,
  EyeOff,
  Box,
  Layers,
  Activity,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Types
type NodeType = 
  | 'trigger' 
  | 'action' 
  | 'condition' 
  | 'loop' 
  | 'delay' 
  | 'email' 
  | 'webhook' 
  | 'notification' 
  | 'database' 
  | 'code'
  | 'end';

interface Position {
  x: number;
  y: number;
}

interface WorkflowNode {
  id: string;
  type: NodeType;
  title: string;
  description?: string;
  position: Position;
  config: Record<string, unknown>;
  inputs: string[];
  outputs: string[];
  status?: 'idle' | 'running' | 'success' | 'error';
}

interface WorkflowConnection {
  id: string;
  sourceId: string;
  sourcePort: 'default' | 'true' | 'false';
  targetId: string;
}

interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  connections: WorkflowConnection[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

interface NodeTemplate {
  type: NodeType;
  title: string;
  description: string;
  icon: React.ReactNode;
  category: 'trigger' | 'action' | 'logic' | 'integration';
  defaultConfig: Record<string, unknown>;
}

interface VisualWorkflowBuilderProps {
  workflow?: Workflow;
  onSave?: (workflow: Workflow) => void;
  onRun?: (workflow: Workflow) => void;
}

// Node templates
const NODE_TEMPLATES: NodeTemplate[] = [
  {
    type: 'trigger',
    title: 'Form Submitted',
    description: 'Triggered when a form is submitted',
    icon: <Zap className="h-5 w-5" />,
    category: 'trigger',
    defaultConfig: { formId: '', conditions: [] },
  },
  {
    type: 'email',
    title: 'Send Email',
    description: 'Send an email notification',
    icon: <Mail className="h-5 w-5" />,
    category: 'action',
    defaultConfig: { to: '', subject: '', body: '', useTemplate: false },
  },
  {
    type: 'webhook',
    title: 'Webhook',
    description: 'Send data to an external URL',
    icon: <Webhook className="h-5 w-5" />,
    category: 'integration',
    defaultConfig: { url: '', method: 'POST', headers: {}, body: '' },
  },
  {
    type: 'notification',
    title: 'Push Notification',
    description: 'Send a push notification',
    icon: <Bell className="h-5 w-5" />,
    category: 'action',
    defaultConfig: { title: '', body: '', icon: '' },
  },
  {
    type: 'condition',
    title: 'If/Else',
    description: 'Branch based on conditions',
    icon: <GitBranch className="h-5 w-5" />,
    category: 'logic',
    defaultConfig: { field: '', operator: 'equals', value: '' },
  },
  {
    type: 'loop',
    title: 'Loop',
    description: 'Iterate over items',
    icon: <Repeat className="h-5 w-5" />,
    category: 'logic',
    defaultConfig: { collection: '', maxIterations: 100 },
  },
  {
    type: 'delay',
    title: 'Delay',
    description: 'Wait before continuing',
    icon: <Clock className="h-5 w-5" />,
    category: 'logic',
    defaultConfig: { duration: 60, unit: 'seconds' },
  },
  {
    type: 'database',
    title: 'Database',
    description: 'Save or query data',
    icon: <Database className="h-5 w-5" />,
    category: 'integration',
    defaultConfig: { operation: 'insert', table: '', data: {} },
  },
  {
    type: 'code',
    title: 'Custom Code',
    description: 'Run custom JavaScript',
    icon: <Code className="h-5 w-5" />,
    category: 'action',
    defaultConfig: { code: '// Your code here\nreturn data;' },
  },
  {
    type: 'end',
    title: 'End',
    description: 'End workflow execution',
    icon: <CheckCircle className="h-5 w-5" />,
    category: 'action',
    defaultConfig: { status: 'success', message: '' },
  },
];

// Colors for node types
const NODE_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  trigger: { bg: 'bg-green-50', border: 'border-green-300', text: 'text-green-700' },
  action: { bg: 'bg-blue-50', border: 'border-blue-300', text: 'text-blue-700' },
  condition: { bg: 'bg-yellow-50', border: 'border-yellow-300', text: 'text-yellow-700' },
  loop: { bg: 'bg-purple-50', border: 'border-purple-300', text: 'text-purple-700' },
  delay: { bg: 'bg-orange-50', border: 'border-orange-300', text: 'text-orange-700' },
  email: { bg: 'bg-blue-50', border: 'border-blue-300', text: 'text-blue-700' },
  webhook: { bg: 'bg-indigo-50', border: 'border-indigo-300', text: 'text-indigo-700' },
  notification: { bg: 'bg-pink-50', border: 'border-pink-300', text: 'text-pink-700' },
  database: { bg: 'bg-cyan-50', border: 'border-cyan-300', text: 'text-cyan-700' },
  code: { bg: 'bg-gray-50', border: 'border-gray-300', text: 'text-gray-700' },
  end: { bg: 'bg-red-50', border: 'border-red-300', text: 'text-red-700' },
};

// Generate unique ID
const generateId = () => `node_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;

export function VisualWorkflowBuilder({
  workflow: initialWorkflow,
  onSave,
  onRun,
}: VisualWorkflowBuilderProps) {
  // State
  const [nodes, setNodes] = useState<WorkflowNode[]>(initialWorkflow?.nodes || []);
  const [connections, setConnections] = useState<WorkflowConnection[]>(initialWorkflow?.connections || []);
  const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStart, setConnectionStart] = useState<{ nodeId: string; port: string } | null>(null);
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState<Position>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<Position | null>(null);
  const [showNodePanel, setShowNodePanel] = useState(true);
  const [workflowName, setWorkflowName] = useState(initialWorkflow?.name || 'New Workflow');
  const [isActive, setIsActive] = useState(initialWorkflow?.isActive || false);
  const [history, setHistory] = useState<{ nodes: WorkflowNode[]; connections: WorkflowConnection[] }[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  // Refs
  const canvasRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  // Save to history
  const saveToHistory = useCallback(() => {
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push({ nodes: [...nodes], connections: [...connections] });
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  }, [history, historyIndex, nodes, connections]);

  // Undo/Redo
  const undo = useCallback(() => {
    if (historyIndex > 0) {
      const prevState = history[historyIndex - 1];
      setNodes(prevState.nodes);
      setConnections(prevState.connections);
      setHistoryIndex(historyIndex - 1);
    }
  }, [history, historyIndex]);

  const redo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      const nextState = history[historyIndex + 1];
      setNodes(nextState.nodes);
      setConnections(nextState.connections);
      setHistoryIndex(historyIndex + 1);
    }
  }, [history, historyIndex]);

  // Add node from template
  const addNode = useCallback((template: NodeTemplate, position?: Position) => {
    const newNode: WorkflowNode = {
      id: generateId(),
      type: template.type,
      title: template.title,
      description: template.description,
      position: position || { x: 100 + nodes.length * 50, y: 100 + nodes.length * 30 },
      config: { ...template.defaultConfig },
      inputs: template.type === 'trigger' ? [] : ['input'],
      outputs: template.type === 'condition' ? ['true', 'false'] : template.type === 'end' ? [] : ['output'],
      status: 'idle',
    };

    setNodes([...nodes, newNode]);
    saveToHistory();
  }, [nodes, saveToHistory]);

  // Delete node
  const deleteNode = useCallback((nodeId: string) => {
    setNodes(nodes.filter(n => n.id !== nodeId));
    setConnections(connections.filter(c => c.sourceId !== nodeId && c.targetId !== nodeId));
    if (selectedNode?.id === nodeId) {
      setSelectedNode(null);
    }
    saveToHistory();
  }, [nodes, connections, selectedNode, saveToHistory]);

  // Duplicate node
  const duplicateNode = useCallback((node: WorkflowNode) => {
    const newNode: WorkflowNode = {
      ...node,
      id: generateId(),
      position: { x: node.position.x + 50, y: node.position.y + 50 },
      status: 'idle',
    };
    setNodes([...nodes, newNode]);
    saveToHistory();
  }, [nodes, saveToHistory]);

  // Update node position
  const updateNodePosition = useCallback((nodeId: string, position: Position) => {
    setNodes(nodes.map(n => 
      n.id === nodeId ? { ...n, position } : n
    ));
  }, [nodes]);

  // Update node config
  const updateNodeConfig = useCallback((nodeId: string, config: Record<string, unknown>) => {
    setNodes(nodes.map(n => 
      n.id === nodeId ? { ...n, config } : n
    ));
    saveToHistory();
  }, [nodes, saveToHistory]);

  // Start connection
  const startConnection = useCallback((nodeId: string, port: string) => {
    setIsConnecting(true);
    setConnectionStart({ nodeId, port });
  }, []);

  // Complete connection
  const completeConnection = useCallback((targetNodeId: string) => {
    if (!connectionStart || connectionStart.nodeId === targetNodeId) {
      setIsConnecting(false);
      setConnectionStart(null);
      return;
    }

    // Check if connection already exists
    const exists = connections.some(
      c => c.sourceId === connectionStart.nodeId && c.targetId === targetNodeId
    );

    if (!exists) {
      const newConnection: WorkflowConnection = {
        id: generateId(),
        sourceId: connectionStart.nodeId,
        sourcePort: connectionStart.port as WorkflowConnection['sourcePort'],
        targetId: targetNodeId,
      };
      setConnections([...connections, newConnection]);
      saveToHistory();
    }

    setIsConnecting(false);
    setConnectionStart(null);
  }, [connectionStart, connections, saveToHistory]);

  // Delete connection
  const deleteConnection = useCallback((connectionId: string) => {
    setConnections(connections.filter(c => c.id !== connectionId));
    saveToHistory();
  }, [connections, saveToHistory]);

  // Zoom controls
  const zoomIn = () => setZoom(Math.min(zoom + 0.1, 2));
  const zoomOut = () => setZoom(Math.max(zoom - 0.1, 0.5));
  const resetZoom = () => { setZoom(1); setOffset({ x: 0, y: 0 }); };

  // Save workflow
  const handleSave = useCallback(() => {
    const workflow: Workflow = {
      id: initialWorkflow?.id || generateId(),
      name: workflowName,
      nodes,
      connections,
      isActive,
      createdAt: initialWorkflow?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    onSave?.(workflow);
  }, [initialWorkflow, workflowName, nodes, connections, isActive, onSave]);

  // Run workflow
  const handleRun = useCallback(async () => {
    if (nodes.length === 0) return;

    setIsRunning(true);
    
    // Simulate workflow execution
    const triggerNode = nodes.find(n => n.type === 'trigger');
    if (!triggerNode) {
      setIsRunning(false);
      return;
    }

    // Mark nodes as running one by one
    const executeOrder = [triggerNode.id];
    const visited = new Set([triggerNode.id]);

    // Simple BFS to find execution order
    const queue = [triggerNode.id];
    while (queue.length > 0) {
      const current = queue.shift()!;
      const outgoing = connections.filter(c => c.sourceId === current);
      for (const conn of outgoing) {
        if (!visited.has(conn.targetId)) {
          visited.add(conn.targetId);
          executeOrder.push(conn.targetId);
          queue.push(conn.targetId);
        }
      }
    }

    // Animate execution
    for (const nodeId of executeOrder) {
      setNodes(prev => prev.map(n => 
        n.id === nodeId ? { ...n, status: 'running' } : n
      ));
      await new Promise(r => setTimeout(r, 500));
      setNodes(prev => prev.map(n => 
        n.id === nodeId ? { ...n, status: 'success' } : n
      ));
    }

    setIsRunning(false);

    const workflow: Workflow = {
      id: initialWorkflow?.id || generateId(),
      name: workflowName,
      nodes,
      connections,
      isActive,
      createdAt: initialWorkflow?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    onRun?.(workflow);
  }, [nodes, connections, initialWorkflow, workflowName, isActive, onRun]);

  // Handle canvas pan
  const handleCanvasMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 1 || (e.button === 0 && e.altKey)) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
    }
  }, [offset]);

  const handleCanvasMouseMove = useCallback((e: React.MouseEvent) => {
    if (isDragging && dragStart) {
      setOffset({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  }, [isDragging, dragStart]);

  const handleCanvasMouseUp = useCallback(() => {
    setIsDragging(false);
    setDragStart(null);
    if (isConnecting) {
      setIsConnecting(false);
      setConnectionStart(null);
    }
  }, [isConnecting]);

  // Calculate connection path
  const getConnectionPath = useCallback((sourceNode: WorkflowNode, targetNode: WorkflowNode, sourcePort: string) => {
    const sourceX = sourceNode.position.x + 180;
    const sourceY = sourceNode.position.y + (sourcePort === 'false' ? 80 : 50);
    const targetX = targetNode.position.x;
    const targetY = targetNode.position.y + 50;

    const midX = (sourceX + targetX) / 2;

    return `M ${sourceX} ${sourceY} C ${midX} ${sourceY}, ${midX} ${targetY}, ${targetX} ${targetY}`;
  }, []);

  return (
    <div className="h-[calc(100vh-200px)] flex flex-col border rounded-lg overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 border-b bg-background">
        <div className="flex items-center gap-4">
          <Input
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            className="w-48 font-medium"
          />
          <div className="flex items-center gap-2">
            <Switch checked={isActive} onCheckedChange={setIsActive} />
            <Label className="text-sm">Active</Label>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={undo} disabled={historyIndex <= 0}>
            <Undo className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={redo} disabled={historyIndex >= history.length - 1}>
            <Redo className="h-4 w-4" />
          </Button>
          <Separator orientation="vertical" className="h-6" />
          <Button variant="ghost" size="icon" onClick={zoomOut}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm w-12 text-center">{Math.round(zoom * 100)}%</span>
          <Button variant="ghost" size="icon" onClick={zoomIn}>
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={resetZoom}>
            <Maximize2 className="h-4 w-4" />
          </Button>
          <Separator orientation="vertical" className="h-6" />
          <Button variant="ghost" size="icon" onClick={() => setShowNodePanel(!showNodePanel)}>
            {showNodePanel ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </Button>
          <Separator orientation="vertical" className="h-6" />
          <Button variant="outline" onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save
          </Button>
          <Button onClick={handleRun} disabled={isRunning || nodes.length === 0}>
            {isRunning ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            {isRunning ? 'Running...' : 'Run'}
          </Button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Node Panel */}
        {showNodePanel && (
          <div className="w-64 border-r bg-muted/30">
            <ScrollArea className="h-full">
              <div className="p-4 space-y-4">
                <div className="font-medium text-sm flex items-center gap-2">
                  <Layers className="h-4 w-4" />
                  Add Nodes
                </div>
                
                {['trigger', 'action', 'logic', 'integration'].map(category => (
                  <div key={category}>
                    <div className="text-xs text-muted-foreground uppercase tracking-wider mb-2">
                      {category}
                    </div>
                    <div className="space-y-1">
                      {NODE_TEMPLATES.filter(t => t.category === category).map(template => (
                        <button
                          key={template.type}
                          className={cn(
                            'w-full p-2 rounded border text-left transition-colors',
                            'hover:bg-accent hover:border-primary/50',
                            'flex items-center gap-2 text-sm'
                          )}
                          onClick={() => addNode(template)}
                          draggable
                          onDragStart={(e) => {
                            e.dataTransfer.setData('nodeTemplate', JSON.stringify(template));
                          }}
                        >
                          <span className={NODE_COLORS[template.type]?.text}>
                            {template.icon}
                          </span>
                          <span>{template.title}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>
        )}

        {/* Canvas */}
        <div
          ref={canvasRef}
          className={cn(
            'flex-1 relative overflow-hidden bg-grid-pattern',
            isDragging && 'cursor-grabbing',
            isConnecting && 'cursor-crosshair'
          )}
          style={{
            backgroundSize: `${20 * zoom}px ${20 * zoom}px`,
            backgroundPosition: `${offset.x}px ${offset.y}px`,
          }}
          onMouseDown={handleCanvasMouseDown}
          onMouseMove={handleCanvasMouseMove}
          onMouseUp={handleCanvasMouseUp}
          onDrop={(e) => {
            e.preventDefault();
            const templateData = e.dataTransfer.getData('nodeTemplate');
            if (templateData) {
              const template = JSON.parse(templateData) as NodeTemplate;
              const rect = canvasRef.current?.getBoundingClientRect();
              if (rect) {
                const position = {
                  x: (e.clientX - rect.left - offset.x) / zoom,
                  y: (e.clientY - rect.top - offset.y) / zoom,
                };
                addNode(template, position);
              }
            }
          }}
          onDragOver={(e) => e.preventDefault()}
        >
          {/* SVG for connections */}
          <svg
            ref={svgRef}
            className="absolute inset-0 pointer-events-none"
            style={{
              transform: `translate(${offset.x}px, ${offset.y}px) scale(${zoom})`,
              transformOrigin: '0 0',
            }}
          >
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7"
                refX="9"
                refY="3.5"
                orient="auto"
              >
                <polygon points="0 0, 10 3.5, 0 7" fill="#6366f1" />
              </marker>
            </defs>
            {connections.map(conn => {
              const sourceNode = nodes.find(n => n.id === conn.sourceId);
              const targetNode = nodes.find(n => n.id === conn.targetId);
              if (!sourceNode || !targetNode) return null;

              return (
                <g key={conn.id} className="pointer-events-auto">
                  <path
                    d={getConnectionPath(sourceNode, targetNode, conn.sourcePort)}
                    fill="none"
                    stroke="#6366f1"
                    strokeWidth="2"
                    markerEnd="url(#arrowhead)"
                    className="cursor-pointer hover:stroke-red-500"
                    onClick={() => deleteConnection(conn.id)}
                  />
                  {conn.sourcePort !== 'default' && (
                    <text
                      x={(sourceNode.position.x + 180 + targetNode.position.x) / 2}
                      y={(sourceNode.position.y + targetNode.position.y) / 2 + 50}
                      className="text-xs fill-muted-foreground"
                    >
                      {conn.sourcePort}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>

          {/* Nodes */}
          <div
            className="absolute inset-0"
            style={{
              transform: `translate(${offset.x}px, ${offset.y}px) scale(${zoom})`,
              transformOrigin: '0 0',
            }}
          >
            {nodes.map(node => (
              <WorkflowNodeComponent
                key={node.id}
                node={node}
                isSelected={selectedNode?.id === node.id}
                isConnecting={isConnecting}
                onSelect={() => {
                  if (isConnecting) {
                    completeConnection(node.id);
                  } else {
                    setSelectedNode(node);
                    setEditDialogOpen(true);
                  }
                }}
                onDelete={() => deleteNode(node.id)}
                onDuplicate={() => duplicateNode(node)}
                onPositionChange={(pos) => updateNodePosition(node.id, pos)}
                onStartConnection={(port) => startConnection(node.id, port)}
              />
            ))}
          </div>

          {/* Empty state */}
          {nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <Box className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <h3 className="font-medium mb-1">No nodes yet</h3>
                <p className="text-sm">
                  Drag nodes from the panel or click to add
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Properties Panel */}
        {selectedNode && (
          <div className="w-72 border-l bg-background">
            <div className="p-4 border-b">
              <h3 className="font-medium flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Node Properties
              </h3>
            </div>
            <ScrollArea className="h-[calc(100%-60px)]">
              <div className="p-4 space-y-4">
                <div>
                  <Label className="text-xs">Title</Label>
                  <Input
                    value={selectedNode.title}
                    onChange={(e) => {
                      setNodes(nodes.map(n =>
                        n.id === selectedNode.id ? { ...n, title: e.target.value } : n
                      ));
                    }}
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label className="text-xs">Description</Label>
                  <Textarea
                    value={selectedNode.description || ''}
                    onChange={(e) => {
                      setNodes(nodes.map(n =>
                        n.id === selectedNode.id ? { ...n, description: e.target.value } : n
                      ));
                    }}
                    className="mt-1"
                    rows={2}
                  />
                </div>
                <Separator />
                <NodeConfigEditor
                  node={selectedNode}
                  onConfigChange={(config) => updateNodeConfig(selectedNode.id, config)}
                />
              </div>
            </ScrollArea>
          </div>
        )}
      </div>

      {/* Status bar */}
      <div className="flex items-center justify-between px-4 py-2 border-t bg-muted/30 text-xs text-muted-foreground">
        <div className="flex items-center gap-4">
          <span>{nodes.length} nodes</span>
          <span>{connections.length} connections</span>
        </div>
        <div className="flex items-center gap-2">
          <Activity className="h-3 w-3" />
          <span>
            {isRunning ? 'Running...' : isActive ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>
    </div>
  );
}

// Workflow Node Component
interface WorkflowNodeComponentProps {
  node: WorkflowNode;
  isSelected: boolean;
  isConnecting: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onDuplicate: () => void;
  onPositionChange: (position: Position) => void;
  onStartConnection: (port: string) => void;
}

function WorkflowNodeComponent({
  node,
  isSelected,
  isConnecting,
  onSelect,
  onDelete,
  onDuplicate,
  onPositionChange,
  onStartConnection,
}: WorkflowNodeComponentProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState<Position>({ x: 0, y: 0 });

  const colors = NODE_COLORS[node.type] || NODE_COLORS.action;
  const template = NODE_TEMPLATES.find(t => t.type === node.type);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0 && !isConnecting) {
      e.stopPropagation();
      setIsDragging(true);
      setDragOffset({
        x: e.clientX - node.position.x,
        y: e.clientY - node.position.y,
      });
    }
  };

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      onPositionChange({
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y,
      });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset, onPositionChange]);

  return (
    <div
      className={cn(
        'absolute w-44 rounded-lg border-2 shadow-sm transition-shadow',
        colors.bg,
        colors.border,
        isSelected && 'ring-2 ring-primary ring-offset-2',
        isDragging && 'shadow-lg',
        isConnecting && 'cursor-crosshair'
      )}
      style={{
        left: node.position.x,
        top: node.position.y,
      }}
      onMouseDown={handleMouseDown}
      onClick={(e) => {
        e.stopPropagation();
        onSelect();
      }}
    >
      {/* Header */}
      <div className={cn('px-3 py-2 flex items-center gap-2', colors.text)}>
        <GripVertical className="h-4 w-4 cursor-grab opacity-50" />
        {template?.icon}
        <span className="font-medium text-sm truncate flex-1">{node.title}</span>
        {node.status === 'running' && (
          <Loader2 className="h-4 w-4 animate-spin" />
        )}
        {node.status === 'success' && (
          <CheckCircle className="h-4 w-4 text-green-600" />
        )}
        {node.status === 'error' && (
          <XCircle className="h-4 w-4 text-red-600" />
        )}
      </div>

      {/* Input port */}
      {node.inputs.length > 0 && (
        <div
          className="absolute left-0 top-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-gray-400 border-2 border-white cursor-crosshair"
          onClick={(e) => {
            e.stopPropagation();
            onSelect();
          }}
        />
      )}

      {/* Output ports */}
      {node.outputs.map((output, index) => (
        <div
          key={output}
          className={cn(
            'absolute right-0 -translate-x-1/2 translate-x-1/2 w-3 h-3 rounded-full border-2 border-white cursor-crosshair',
            output === 'true' ? 'bg-green-500' : output === 'false' ? 'bg-red-500' : 'bg-indigo-500'
          )}
          style={{
            top: node.type === 'condition' 
              ? `${30 + index * 30}%` 
              : '50%',
            transform: 'translate(50%, -50%)',
          }}
          onClick={(e) => {
            e.stopPropagation();
            onStartConnection(output === 'output' ? 'default' : output);
          }}
        />
      ))}

      {/* Quick actions */}
      {isSelected && (
        <div className="absolute -top-8 right-0 flex gap-1">
          <Button
            variant="secondary"
            size="icon"
            className="h-6 w-6"
            onClick={(e) => {
              e.stopPropagation();
              onDuplicate();
            }}
          >
            <Copy className="h-3 w-3" />
          </Button>
          <Button
            variant="destructive"
            size="icon"
            className="h-6 w-6"
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      )}
    </div>
  );
}

// Node Config Editor
interface NodeConfigEditorProps {
  node: WorkflowNode;
  onConfigChange: (config: Record<string, unknown>) => void;
}

function NodeConfigEditor({ node, onConfigChange }: NodeConfigEditorProps) {
  const updateConfig = (key: string, value: unknown) => {
    onConfigChange({ ...node.config, [key]: value });
  };

  switch (node.type) {
    case 'email':
      return (
        <div className="space-y-4">
          <div>
            <Label className="text-xs">To</Label>
            <Input
              value={(node.config.to as string) || ''}
              onChange={(e) => updateConfig('to', e.target.value)}
              placeholder="email@example.com"
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs">Subject</Label>
            <Input
              value={(node.config.subject as string) || ''}
              onChange={(e) => updateConfig('subject', e.target.value)}
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs">Body</Label>
            <Textarea
              value={(node.config.body as string) || ''}
              onChange={(e) => updateConfig('body', e.target.value)}
              className="mt-1"
              rows={4}
            />
          </div>
        </div>
      );

    case 'webhook':
      return (
        <div className="space-y-4">
          <div>
            <Label className="text-xs">URL</Label>
            <Input
              value={(node.config.url as string) || ''}
              onChange={(e) => updateConfig('url', e.target.value)}
              placeholder="https://api.example.com/webhook"
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs">Method</Label>
            <Select
              value={(node.config.method as string) || 'POST'}
              onValueChange={(v) => updateConfig('method', v)}
            >
              <SelectTrigger className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="GET">GET</SelectItem>
                <SelectItem value="POST">POST</SelectItem>
                <SelectItem value="PUT">PUT</SelectItem>
                <SelectItem value="DELETE">DELETE</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      );

    case 'condition':
      return (
        <div className="space-y-4">
          <div>
            <Label className="text-xs">Field</Label>
            <Input
              value={(node.config.field as string) || ''}
              onChange={(e) => updateConfig('field', e.target.value)}
              placeholder="fieldName"
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs">Operator</Label>
            <Select
              value={(node.config.operator as string) || 'equals'}
              onValueChange={(v) => updateConfig('operator', v)}
            >
              <SelectTrigger className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="equals">Equals</SelectItem>
                <SelectItem value="notEquals">Not Equals</SelectItem>
                <SelectItem value="contains">Contains</SelectItem>
                <SelectItem value="greaterThan">Greater Than</SelectItem>
                <SelectItem value="lessThan">Less Than</SelectItem>
                <SelectItem value="isEmpty">Is Empty</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label className="text-xs">Value</Label>
            <Input
              value={(node.config.value as string) || ''}
              onChange={(e) => updateConfig('value', e.target.value)}
              className="mt-1"
            />
          </div>
        </div>
      );

    case 'delay':
      return (
        <div className="space-y-4">
          <div>
            <Label className="text-xs">Duration</Label>
            <Input
              type="number"
              value={(node.config.duration as number) || 60}
              onChange={(e) => updateConfig('duration', parseInt(e.target.value))}
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs">Unit</Label>
            <Select
              value={(node.config.unit as string) || 'seconds'}
              onValueChange={(v) => updateConfig('unit', v)}
            >
              <SelectTrigger className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="seconds">Seconds</SelectItem>
                <SelectItem value="minutes">Minutes</SelectItem>
                <SelectItem value="hours">Hours</SelectItem>
                <SelectItem value="days">Days</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      );

    case 'code':
      return (
        <div>
          <Label className="text-xs">JavaScript Code</Label>
          <Textarea
            value={(node.config.code as string) || ''}
            onChange={(e) => updateConfig('code', e.target.value)}
            className="mt-1 font-mono text-xs"
            rows={8}
          />
        </div>
      );

    default:
      return (
        <p className="text-sm text-muted-foreground">
          No configuration options for this node type.
        </p>
      );
  }
}

export default VisualWorkflowBuilder;
