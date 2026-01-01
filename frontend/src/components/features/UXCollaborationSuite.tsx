'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { 
  useThemeMarketplace,
  useBrandGuidelines,
  useUpdateBrandGuideline,
  useConversationSessions,
  useTeamWorkspaces,
  useFormTemplates,
  useAccessibilityAutoFix
} from '@/hooks/use-emerging-features';
import { 
  Palette, Sparkles, Users, MessageSquare, 
  FolderKanban, FileText, Eye, Download,
  Star, TrendingUp, CheckCircle2, Clock
} from 'lucide-react';

interface UXCollaborationSuiteProps {
  formId: string;
}

export function UXCollaborationSuite({ formId }: UXCollaborationSuiteProps) {
  const { data: themes } = useThemeMarketplace();
  const updateBrandGuideline = useUpdateBrandGuideline();
  const { data: brandGuidelines } = useBrandGuidelines();
  const { data: collaborationSessions } = useConversationSessions(formId);
  const { data: workspaces } = useTeamWorkspaces();
  const { data: templates } = useFormTemplates();
  const { data: accessibility } = useAccessibilityAutoFix(formId);

  const [selectedTheme, setSelectedTheme] = useState<string>('');
  const activeSessions = collaborationSessions?.filter(s => s.is_active) || [];

  return (
    <div className="space-y-6">
      <Tabs defaultValue="themes" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="themes">Themes</TabsTrigger>
          <TabsTrigger value="branding">Branding</TabsTrigger>
          <TabsTrigger value="collaboration">Collaboration</TabsTrigger>
          <TabsTrigger value="workspaces">Workspaces</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
        </TabsList>

        {/* Themes Tab */}
        <TabsContent value="themes" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Palette className="h-5 w-5 text-purple-500" />
                    Theme Marketplace
                  </CardTitle>
                  <CardDescription>
                    Browse and apply professional themes
                  </CardDescription>
                </div>
                <Button size="sm" variant="outline">
                  <Sparkles className="mr-2 h-4 w-4" />
                  Create Theme
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                {themes?.map((theme) => (
                  <Card key={theme.id} className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
                    <div className="h-24 bg-gradient-to-br from-purple-400 to-pink-400 relative">
                      {theme.preview_url && (
                        <img 
                          src={theme.preview_url} 
                          alt={theme.name}
                          className="w-full h-full object-cover"
                        />
                      )}
                      {theme.is_premium && (
                        <Badge className="absolute top-2 right-2" variant="secondary">
                          <Star className="h-3 w-3 mr-1" />
                          Premium
                        </Badge>
                      )}
                    </div>
                    <CardContent className="pt-4">
                      <h3 className="font-medium mb-1">{theme.name}</h3>
                      <p className="text-xs text-muted-foreground mb-2">{theme.description}</p>
                      
                      <div className="flex items-center justify-between mb-3">
                        <Badge variant="outline" className="text-xs">{theme.category}</Badge>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                          {theme.rating}
                        </div>
                      </div>

                      <div className="flex items-center justify-between text-xs text-muted-foreground mb-3">
                        <span>{theme.downloads} downloads</span>
                        <span>by {theme.author}</span>
                      </div>

                      <Button size="sm" className="w-full">
                        {theme.is_installed ? 'Apply' : 'Install'}
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Branding Tab */}
        <TabsContent value="branding" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-blue-500" />
                Brand Guidelines
              </CardTitle>
              <CardDescription>
                Maintain consistent brand identity across forms
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {brandGuidelines && brandGuidelines.length > 0 ? (
                brandGuidelines.map((guideline) => (
                  <div key={guideline.id} className="p-4 border rounded-lg space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">{guideline.name}</h4>
                      <Switch
                        checked={guideline.is_active}
                        onCheckedChange={(checked) => {
                          updateBrandGuideline.mutate({
                            guidelineId: guideline.id,
                            guideline: { is_active: checked }
                          });
                        }}
                      />
                    </div>

                    {/* Color Palette */}
                    {guideline.color_palette && (
                      <div>
                        <Label className="text-xs text-muted-foreground">Color Palette</Label>
                        <div className="flex gap-2 mt-2">
                          {Object.entries(guideline.color_palette).map(([key, color]) => (
                            <div key={key} className="text-center">
                              <div
                                className="w-12 h-12 rounded border-2 border-muted"
                                style={{ backgroundColor: String(color) }}
                              />
                              <p className="text-xs mt-1 capitalize">{key}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Typography */}
                    {guideline.typography && (
                      <div>
                        <Label className="text-xs text-muted-foreground">Typography</Label>
                        <div className="grid grid-cols-2 gap-2 mt-2">
                          {Object.entries(guideline.typography).map(([key, font]) => (
                            <div key={key} className="p-2 bg-muted rounded">
                              <p className="text-xs text-muted-foreground capitalize">{key}</p>
                              <p className="font-medium text-sm" style={{ fontFamily: String(font) }}>
                                {String(font)}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Spacing & Design Tokens */}
                    <div className="grid grid-cols-2 gap-4">
                      {guideline.spacing && (
                        <div>
                          <Label className="text-xs text-muted-foreground">Spacing Scale</Label>
                          <div className="flex gap-1 mt-2">
                            {Object.entries(guideline.spacing).slice(0, 4).map(([key, value]) => (
                              <Badge key={key} variant="outline" className="text-xs">
                                {key}: {String(value)}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {guideline.border_radius && (
                        <div>
                          <Label className="text-xs text-muted-foreground">Border Radius</Label>
                          <div className="flex gap-1 mt-2">
                            {Object.entries(guideline.border_radius).slice(0, 3).map(([key, value]) => (
                              <Badge key={key} variant="outline" className="text-xs">
                                {key}: {String(value)}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {guideline.auto_apply && (
                        <Badge variant="default" className="text-xs">
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                          Auto-applied to new forms
                        </Badge>
                      )}
                      {guideline.enforce_compliance && (
                        <Badge variant="secondary" className="text-xs">
                          Compliance enforced
                        </Badge>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Sparkles className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No brand guidelines configured</p>
                  <Button size="sm" className="mt-4">Create Guideline</Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Collaboration Tab */}
        <TabsContent value="collaboration" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-green-500" />
                Real-Time Collaboration
              </CardTitle>
              <CardDescription>
                Active collaboration sessions on this form
              </CardDescription>
            </CardHeader>
            <CardContent>
              {activeSessions.length > 0 ? (
                <div className="space-y-4">
                  {activeSessions.map((session) => (
                    <div key={session.id} className="p-4 border rounded-lg space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="relative">
                            <div className="w-2 h-2 bg-green-500 rounded-full absolute -top-1 -right-1 animate-pulse" />
                            <Users className="h-5 w-5 text-green-600" />
                          </div>
                          <div>
                            <h4 className="font-medium">Session {session.session_id.slice(0, 8)}</h4>
                            <p className="text-xs text-muted-foreground">
                              Started {new Date(session.started_at).toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                        <Badge variant="default">{session.participants.length} active</Badge>
                      </div>

                      {/* Participants */}
                      <div className="flex items-center gap-2">
                        <Label className="text-xs text-muted-foreground">Participants:</Label>
                        <div className="flex -space-x-2">
                          {(session.participants as Record<string, unknown>[]).slice(0, 5).map((participant, index: number) => (
                            <Avatar key={index} className="w-8 h-8 border-2 border-background">
                              <AvatarFallback className="text-xs">
                                {String(participant.user_name || 'U').charAt(0)}
                              </AvatarFallback>
                            </Avatar>
                          ))}
                          {session.participants.length > 5 && (
                            <div className="w-8 h-8 rounded-full bg-muted border-2 border-background flex items-center justify-center text-xs">
                              +{session.participants.length - 5}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Recent Changes */}
                      {session.change_history && session.change_history.length > 0 && (
                        <div className="space-y-1">
                          <Label className="text-xs text-muted-foreground">Recent Changes:</Label>
                          {(session.change_history as Record<string, unknown>[]).slice(0, 2).map((change, index: number) => (
                            <div key={index} className="flex items-center gap-2 text-xs p-2 bg-muted rounded">
                              <Clock className="h-3 w-3" />
                              <span>{String(change.user || '')} {String(change.action || '')}</span>
                              <Badge variant="outline" className="text-xs ml-auto">
                                {new Date(String(change.timestamp || '')).toLocaleTimeString()}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      )}

                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          CRDT Sync: {session.crdt_enabled ? 'Enabled' : 'Disabled'}
                        </Badge>
                        {session.conflict_resolution_strategy && (
                          <Badge variant="outline" className="text-xs capitalize">
                            {session.conflict_resolution_strategy}
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No active collaboration sessions</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Workspaces Tab */}
        <TabsContent value="workspaces" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <FolderKanban className="h-5 w-5 text-orange-500" />
                    Team Workspaces
                  </CardTitle>
                  <CardDescription>
                    Organize forms and teams by workspace
                  </CardDescription>
                </div>
                <Button size="sm">
                  <FolderKanban className="mr-2 h-4 w-4" />
                  New Workspace
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                {workspaces?.map((workspace) => (
                  <Card key={workspace.id}>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-base">{workspace.name}</CardTitle>
                        <Badge variant={workspace.is_active ? 'default' : 'secondary'}>
                          {workspace.is_active ? 'Active' : 'Archived'}
                        </Badge>
                      </div>
                      <CardDescription className="text-xs">
                        {workspace.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <p className="text-muted-foreground text-xs">Members</p>
                          <p className="font-medium">{workspace.member_count}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground text-xs">Forms</p>
                          <p className="font-medium">{workspace.form_count || 0}</p>
                        </div>
                      </div>

                      {workspace.tags && workspace.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {workspace.tags.slice(0, 3).map((tag: string) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}

                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" className="flex-1">
                          <Eye className="h-3 w-3 mr-1" />
                          View
                        </Button>
                        <Button size="sm" variant="outline" className="flex-1">
                          Settings
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-indigo-500" />
                    Form Templates
                  </CardTitle>
                  <CardDescription>
                    Pre-built templates for common use cases
                  </CardDescription>
                </div>
                <Button size="sm" variant="outline">
                  <FileText className="mr-2 h-4 w-4" />
                  Save as Template
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                {templates?.map((template) => (
                  <Card key={template.id} className="hover:shadow-md transition-shadow">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between mb-2">
                        <Badge variant="outline" className="text-xs">{template.category}</Badge>
                        {template.is_featured && (
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        )}
                      </div>
                      <CardTitle className="text-sm">{template.name}</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {template.description}
                      </p>

                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <TrendingUp className="h-3 w-3" />
                          {template.usage_count} uses
                        </div>
                        <div className="flex items-center gap-1">
                          <Star className="h-3 w-3" />
                          {template.rating}
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button size="sm" className="flex-1">
                          Use Template
                        </Button>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
