/**
 * Gamification System for Form Building
 * Tracks user progress, achievements, and rewards
 */
'use client';

import React, { useState, useEffect, useCallback, createContext, useContext } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import {
  Trophy,
  Star,
  Zap,
  Target,
  Award,
  Flame,
  Crown,
  Gift,
  TrendingUp,
  CheckCircle,
  Lock,
  Sparkles,
  Medal,
  Rocket,
  Heart,
  ThumbsUp,
  Users,
  Calendar,
  BarChart3,
  Palette,
  Settings,
  Share2,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Types
interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  category: 'forms' | 'fields' | 'submissions' | 'engagement' | 'mastery';
  requirement: number;
  current: number;
  unlocked: boolean;
  unlockedAt?: string;
  points: number;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

interface Level {
  level: number;
  title: string;
  minPoints: number;
  maxPoints: number;
  icon: React.ReactNode;
  color: string;
}

interface DailyChallenge {
  id: string;
  title: string;
  description: string;
  reward: number;
  progress: number;
  target: number;
  expiresAt: string;
  completed: boolean;
}

interface GamificationState {
  points: number;
  level: Level;
  streak: number;
  achievements: Achievement[];
  dailyChallenges: DailyChallenge[];
  recentActivity: Array<{
    type: string;
    description: string;
    points: number;
    timestamp: string;
  }>;
}

// Levels configuration
const LEVELS: Level[] = [
  { level: 1, title: 'Form Newbie', minPoints: 0, maxPoints: 100, icon: <Star className="h-5 w-5" />, color: 'text-gray-500' },
  { level: 2, title: 'Form Apprentice', minPoints: 100, maxPoints: 300, icon: <Zap className="h-5 w-5" />, color: 'text-blue-500' },
  { level: 3, title: 'Form Builder', minPoints: 300, maxPoints: 600, icon: <Target className="h-5 w-5" />, color: 'text-green-500' },
  { level: 4, title: 'Form Expert', minPoints: 600, maxPoints: 1000, icon: <Award className="h-5 w-5" />, color: 'text-purple-500' },
  { level: 5, title: 'Form Master', minPoints: 1000, maxPoints: 2000, icon: <Crown className="h-5 w-5" />, color: 'text-yellow-500' },
  { level: 6, title: 'Form Legend', minPoints: 2000, maxPoints: 5000, icon: <Trophy className="h-5 w-5" />, color: 'text-orange-500' },
  { level: 7, title: 'Form Wizard', minPoints: 5000, maxPoints: Infinity, icon: <Sparkles className="h-5 w-5" />, color: 'text-pink-500' },
];

// Default achievements
const DEFAULT_ACHIEVEMENTS: Omit<Achievement, 'current' | 'unlocked' | 'unlockedAt'>[] = [
  // Forms category
  { id: 'first_form', title: 'First Steps', description: 'Create your first form', icon: <Rocket className="h-5 w-5" />, category: 'forms', requirement: 1, points: 10, rarity: 'common' },
  { id: 'five_forms', title: 'Form Collector', description: 'Create 5 forms', icon: <Target className="h-5 w-5" />, category: 'forms', requirement: 5, points: 25, rarity: 'common' },
  { id: 'ten_forms', title: 'Form Factory', description: 'Create 10 forms', icon: <Flame className="h-5 w-5" />, category: 'forms', requirement: 10, points: 50, rarity: 'rare' },
  { id: 'twentyfive_forms', title: 'Form Mogul', description: 'Create 25 forms', icon: <Crown className="h-5 w-5" />, category: 'forms', requirement: 25, points: 100, rarity: 'epic' },
  
  // Fields category
  { id: 'ten_fields', title: 'Field Farmer', description: 'Add 10 fields across forms', icon: <BarChart3 className="h-5 w-5" />, category: 'fields', requirement: 10, points: 15, rarity: 'common' },
  { id: 'fifty_fields', title: 'Field Master', description: 'Add 50 fields across forms', icon: <Medal className="h-5 w-5" />, category: 'fields', requirement: 50, points: 40, rarity: 'rare' },
  { id: 'all_field_types', title: 'Jack of All Fields', description: 'Use every field type at least once', icon: <Palette className="h-5 w-5" />, category: 'fields', requirement: 11, points: 75, rarity: 'epic' },
  
  // Submissions category
  { id: 'first_submission', title: 'First Response', description: 'Receive your first form submission', icon: <Heart className="h-5 w-5" />, category: 'submissions', requirement: 1, points: 20, rarity: 'common' },
  { id: 'hundred_submissions', title: 'Popular Forms', description: 'Receive 100 total submissions', icon: <Users className="h-5 w-5" />, category: 'submissions', requirement: 100, points: 75, rarity: 'rare' },
  { id: 'thousand_submissions', title: 'Form Celebrity', description: 'Receive 1000 total submissions', icon: <Trophy className="h-5 w-5" />, category: 'submissions', requirement: 1000, points: 200, rarity: 'legendary' },
  
  // Engagement category
  { id: 'share_form', title: 'Social Butterfly', description: 'Share a form publicly', icon: <Share2 className="h-5 w-5" />, category: 'engagement', requirement: 1, points: 15, rarity: 'common' },
  { id: 'use_template', title: 'Template Explorer', description: 'Create a form from a template', icon: <Gift className="h-5 w-5" />, category: 'engagement', requirement: 1, points: 10, rarity: 'common' },
  { id: 'seven_day_streak', title: 'Week Warrior', description: 'Log in 7 days in a row', icon: <Calendar className="h-5 w-5" />, category: 'engagement', requirement: 7, points: 50, rarity: 'rare' },
  { id: 'thirty_day_streak', title: 'Monthly Master', description: 'Log in 30 days in a row', icon: <Flame className="h-5 w-5" />, category: 'engagement', requirement: 30, points: 150, rarity: 'epic' },
  
  // Mastery category
  { id: 'conditional_logic', title: 'Logic Pro', description: 'Add conditional logic to a form', icon: <Settings className="h-5 w-5" />, category: 'mastery', requirement: 1, points: 30, rarity: 'rare' },
  { id: 'voice_design', title: 'Voice Commander', description: 'Create a form using voice commands', icon: <Sparkles className="h-5 w-5" />, category: 'mastery', requirement: 1, points: 40, rarity: 'rare' },
  { id: 'ab_test', title: 'Optimizer', description: 'Run an A/B test on a form', icon: <TrendingUp className="h-5 w-5" />, category: 'mastery', requirement: 1, points: 50, rarity: 'epic' },
  { id: 'high_conversion', title: 'Conversion King', description: 'Achieve 50% conversion rate on a form', icon: <Crown className="h-5 w-5" />, category: 'mastery', requirement: 50, points: 100, rarity: 'legendary' },
];

// Context
interface GamificationContextType {
  state: GamificationState;
  addPoints: (points: number, reason: string) => void;
  trackAction: (action: string, value?: number) => void;
  checkAchievement: (achievementId: string, currentValue: number) => void;
}

const GamificationContext = createContext<GamificationContextType | null>(null);

export function useGamification() {
  const context = useContext(GamificationContext);
  if (!context) {
    throw new Error('useGamification must be used within GamificationProvider');
  }
  return context;
}

// Provider Component
interface GamificationProviderProps {
  children: React.ReactNode;
  userId: string;
}

export function GamificationProvider({ children, userId }: GamificationProviderProps) {
  const [state, setState] = useState<GamificationState>({
    points: 0,
    level: LEVELS[0],
    streak: 0,
    achievements: DEFAULT_ACHIEVEMENTS.map(a => ({ ...a, current: 0, unlocked: false })),
    dailyChallenges: [],
    recentActivity: [],
  });
  
  const [showLevelUp, setShowLevelUp] = useState(false);
  const [showAchievement, setShowAchievement] = useState<Achievement | null>(null);

  // Load state from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(`gamification_${userId}`);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setState(prev => ({
          ...prev,
          ...parsed,
          level: LEVELS.find(l => parsed.points >= l.minPoints && parsed.points < l.maxPoints) || LEVELS[0],
        }));
      } catch {
        console.error('Failed to load gamification state');
      }
    }
  }, [userId]);

  // Save state to localStorage
  useEffect(() => {
    localStorage.setItem(`gamification_${userId}`, JSON.stringify({
      points: state.points,
      streak: state.streak,
      achievements: state.achievements,
      recentActivity: state.recentActivity.slice(0, 50),
    }));
  }, [state, userId]);

  // Calculate level from points
  const calculateLevel = useCallback((points: number): Level => {
    return LEVELS.find(l => points >= l.minPoints && points < l.maxPoints) || LEVELS[LEVELS.length - 1];
  }, []);

  // Add points
  const addPoints = useCallback((points: number, reason: string) => {
    setState(prev => {
      const newPoints = prev.points + points;
      const newLevel = calculateLevel(newPoints);
      
      // Check for level up
      if (newLevel.level > prev.level.level) {
        setTimeout(() => setShowLevelUp(true), 500);
      }
      
      return {
        ...prev,
        points: newPoints,
        level: newLevel,
        recentActivity: [
          { type: 'points', description: reason, points, timestamp: new Date().toISOString() },
          ...prev.recentActivity,
        ].slice(0, 50),
      };
    });
  }, [calculateLevel]);

  // Track action for achievements
  const trackAction = useCallback((action: string, value: number = 1) => {
    setState(prev => {
      const achievements = prev.achievements.map(achievement => {
        if (achievement.unlocked) return achievement;
        
        // Map actions to achievement IDs
        const actionAchievementMap: Record<string, string[]> = {
          'form_created': ['first_form', 'five_forms', 'ten_forms', 'twentyfive_forms'],
          'field_added': ['ten_fields', 'fifty_fields'],
          'submission_received': ['first_submission', 'hundred_submissions', 'thousand_submissions'],
          'form_shared': ['share_form'],
          'template_used': ['use_template'],
          'login': ['seven_day_streak', 'thirty_day_streak'],
          'conditional_logic_added': ['conditional_logic'],
          'voice_design_used': ['voice_design'],
          'ab_test_started': ['ab_test'],
        };
        
        const relatedAchievements = actionAchievementMap[action] || [];
        if (!relatedAchievements.includes(achievement.id)) return achievement;
        
        const newCurrent = achievement.current + value;
        const shouldUnlock = newCurrent >= achievement.requirement;
        
        if (shouldUnlock && !achievement.unlocked) {
          setTimeout(() => setShowAchievement({ ...achievement, current: newCurrent, unlocked: true }), 1000);
          addPoints(achievement.points, `Achievement: ${achievement.title}`);
        }
        
        return {
          ...achievement,
          current: newCurrent,
          unlocked: shouldUnlock,
          unlockedAt: shouldUnlock ? new Date().toISOString() : undefined,
        };
      });
      
      return { ...prev, achievements };
    });
  }, [addPoints]);

  // Check specific achievement
  const checkAchievement = useCallback((achievementId: string, currentValue: number) => {
    setState(prev => {
      const achievements = prev.achievements.map(achievement => {
        if (achievement.id !== achievementId || achievement.unlocked) return achievement;
        
        const shouldUnlock = currentValue >= achievement.requirement;
        
        if (shouldUnlock) {
          setTimeout(() => setShowAchievement({ ...achievement, current: currentValue, unlocked: true }), 500);
          addPoints(achievement.points, `Achievement: ${achievement.title}`);
        }
        
        return {
          ...achievement,
          current: currentValue,
          unlocked: shouldUnlock,
          unlockedAt: shouldUnlock ? new Date().toISOString() : undefined,
        };
      });
      
      return { ...prev, achievements };
    });
  }, [addPoints]);

  return (
    <GamificationContext.Provider value={{ state, addPoints, trackAction, checkAchievement }}>
      {children}
      
      {/* Level Up Dialog */}
      <Dialog open={showLevelUp} onOpenChange={setShowLevelUp}>
        <DialogContent className="text-center">
          <DialogHeader>
            <DialogTitle className="flex flex-col items-center gap-4">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center animate-bounce">
                {state.level.icon}
              </div>
              <span className="text-2xl">Level Up! 🎉</span>
            </DialogTitle>
            <DialogDescription className="text-lg">
              You&apos;ve reached <span className={cn('font-bold', state.level.color)}>{state.level.title}</span>
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <p className="text-muted-foreground">
              Keep building amazing forms to unlock more achievements!
            </p>
          </div>
          <Button onClick={() => setShowLevelUp(false)}>Continue</Button>
        </DialogContent>
      </Dialog>
      
      {/* Achievement Unlocked Dialog */}
      <Dialog open={!!showAchievement} onOpenChange={() => setShowAchievement(null)}>
        <DialogContent className="text-center">
          <DialogHeader>
            <DialogTitle className="flex flex-col items-center gap-4">
              <div className={cn(
                'w-20 h-20 rounded-full flex items-center justify-center animate-pulse',
                showAchievement?.rarity === 'legendary' && 'bg-gradient-to-br from-yellow-400 via-pink-500 to-purple-600',
                showAchievement?.rarity === 'epic' && 'bg-gradient-to-br from-purple-500 to-pink-500',
                showAchievement?.rarity === 'rare' && 'bg-gradient-to-br from-blue-500 to-cyan-500',
                showAchievement?.rarity === 'common' && 'bg-gradient-to-br from-gray-400 to-gray-500',
              )}>
                <div className="text-white">{showAchievement?.icon}</div>
              </div>
              <span className="text-2xl">Achievement Unlocked! 🏆</span>
            </DialogTitle>
            <DialogDescription className="text-lg">
              <span className="font-bold">{showAchievement?.title}</span>
              <br />
              <span className="text-sm text-muted-foreground">{showAchievement?.description}</span>
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 flex items-center justify-center gap-2">
            <Star className="h-5 w-5 text-yellow-500" />
            <span className="text-xl font-bold">+{showAchievement?.points} points</span>
          </div>
          <Button onClick={() => setShowAchievement(null)}>Awesome!</Button>
        </DialogContent>
      </Dialog>
    </GamificationContext.Provider>
  );
}

// Gamification Dashboard Component
export function GamificationDashboard() {
  const { state } = useGamification();
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  
  const progressToNextLevel = state.level.maxPoints === Infinity 
    ? 100 
    : ((state.points - state.level.minPoints) / (state.level.maxPoints - state.level.minPoints)) * 100;
  
  const unlockedCount = state.achievements.filter(a => a.unlocked).length;
  const totalCount = state.achievements.length;
  
  const categories = ['forms', 'fields', 'submissions', 'engagement', 'mastery'] as const;

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className={cn('p-3 rounded-full bg-muted', state.level.color)}>
                {state.level.icon}
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Current Level</p>
                <p className={cn('text-lg font-bold', state.level.color)}>{state.level.title}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-yellow-100">
                <Star className="h-6 w-6 text-yellow-500" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Points</p>
                <p className="text-2xl font-bold">{state.points.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-orange-100">
                <Flame className="h-6 w-6 text-orange-500" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Current Streak</p>
                <p className="text-2xl font-bold">{state.streak} days</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-purple-100">
                <Trophy className="h-6 w-6 text-purple-500" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Achievements</p>
                <p className="text-2xl font-bold">{unlockedCount}/{totalCount}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Level Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Level Progress</span>
            <Badge variant="secondary">
              {state.level.maxPoints === Infinity 
                ? 'Max Level!' 
                : `${state.level.maxPoints - state.points} pts to next level`}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className={state.level.color}>{state.level.title}</span>
              {state.level.level < LEVELS.length && (
                <span className={LEVELS[state.level.level].color}>
                  {LEVELS[state.level.level].title}
                </span>
              )}
            </div>
            <Progress value={progressToNextLevel} className="h-3" />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>{state.points.toLocaleString()} pts</span>
              {state.level.maxPoints !== Infinity && (
                <span>{state.level.maxPoints.toLocaleString()} pts</span>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Achievements */}
      <Card>
        <CardHeader>
          <CardTitle>Achievements</CardTitle>
          <CardDescription>
            Complete challenges to earn points and unlock badges
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Category Filter */}
          <div className="flex flex-wrap gap-2 mb-6">
            <Button
              variant={selectedCategory === null ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(null)}
            >
              All
            </Button>
            {categories.map(cat => (
              <Button
                key={cat}
                variant={selectedCategory === cat ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(cat)}
                className="capitalize"
              >
                {cat}
              </Button>
            ))}
          </div>
          
          {/* Achievements Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {state.achievements
              .filter(a => !selectedCategory || a.category === selectedCategory)
              .map(achievement => (
                <div
                  key={achievement.id}
                  className={cn(
                    'relative p-4 border rounded-lg transition-all',
                    achievement.unlocked 
                      ? 'bg-gradient-to-br from-white to-muted' 
                      : 'bg-muted/50 opacity-60'
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div className={cn(
                      'p-2 rounded-full',
                      achievement.unlocked && achievement.rarity === 'legendary' && 'bg-gradient-to-br from-yellow-400 via-pink-500 to-purple-600',
                      achievement.unlocked && achievement.rarity === 'epic' && 'bg-gradient-to-br from-purple-500 to-pink-500',
                      achievement.unlocked && achievement.rarity === 'rare' && 'bg-gradient-to-br from-blue-500 to-cyan-500',
                      achievement.unlocked && achievement.rarity === 'common' && 'bg-gradient-to-br from-gray-400 to-gray-500',
                      !achievement.unlocked && 'bg-gray-200',
                    )}>
                      <div className={achievement.unlocked ? 'text-white' : 'text-gray-400'}>
                        {achievement.unlocked ? achievement.icon : <Lock className="h-5 w-5" />}
                      </div>
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium">{achievement.title}</h4>
                        <Badge 
                          variant="outline" 
                          className={cn(
                            'text-xs capitalize',
                            achievement.rarity === 'legendary' && 'border-yellow-500 text-yellow-600',
                            achievement.rarity === 'epic' && 'border-purple-500 text-purple-600',
                            achievement.rarity === 'rare' && 'border-blue-500 text-blue-600',
                          )}
                        >
                          {achievement.rarity}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{achievement.description}</p>
                      
                      {/* Progress */}
                      {!achievement.unlocked && (
                        <div className="mt-2 space-y-1">
                          <Progress 
                            value={(achievement.current / achievement.requirement) * 100} 
                            className="h-1"
                          />
                          <p className="text-xs text-muted-foreground">
                            {achievement.current} / {achievement.requirement}
                          </p>
                        </div>
                      )}
                      
                      {/* Points */}
                      <div className="mt-2 flex items-center gap-1 text-sm">
                        <Star className="h-3 w-3 text-yellow-500" />
                        <span>{achievement.points} pts</span>
                      </div>
                    </div>
                  </div>
                  
                  {achievement.unlocked && (
                    <div className="absolute top-2 right-2">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    </div>
                  )}
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
      
      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          {state.recentActivity.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              No recent activity. Start building forms to earn points!
            </p>
          ) : (
            <div className="space-y-2">
              {state.recentActivity.slice(0, 10).map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-2 border rounded">
                  <span className="text-sm">{activity.description}</span>
                  <Badge variant="secondary" className="gap-1">
                    <Star className="h-3 w-3" />
                    +{activity.points}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Compact Gamification Widget for sidebar/header
export function GamificationWidget() {
  const { state } = useGamification();
  
  const progressToNextLevel = state.level.maxPoints === Infinity 
    ? 100 
    : ((state.points - state.level.minPoints) / (state.level.maxPoints - state.level.minPoints)) * 100;

  return (
    <div className="flex items-center gap-3 p-2 border rounded-lg bg-background">
      <div className={cn('p-2 rounded-full bg-muted', state.level.color)}>
        {state.level.icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <span className={cn('text-sm font-medium', state.level.color)}>
            Lv.{state.level.level}
          </span>
          <span className="text-xs text-muted-foreground">
            {state.points} pts
          </span>
        </div>
        <Progress value={progressToNextLevel} className="h-1 mt-1" />
      </div>
      {state.streak > 0 && (
        <div className="flex items-center gap-1 text-orange-500">
          <Flame className="h-4 w-4" />
          <span className="text-sm font-medium">{state.streak}</span>
        </div>
      )}
    </div>
  );
}

export default GamificationDashboard;
