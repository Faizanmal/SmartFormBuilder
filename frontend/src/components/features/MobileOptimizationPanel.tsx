'use client';

import { useState, useEffect, useCallback } from 'react';
import { mobileAPI } from '@/lib/advancedFeaturesAPI';
import { MobileOptimization, OfflineSubmission } from '@/types/advancedFeatures';

interface MobileOptimizationPanelProps {
  formId: string;
}

export default function MobileOptimizationPanel({ formId }: MobileOptimizationPanelProps) {
  const [optimization, setOptimization] = useState<MobileOptimization | null>(null);
  const [offlineSubmissions, setOfflineSubmissions] = useState<OfflineSubmission[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [optimizationData, offlineData] = await Promise.all([
        mobileAPI.getMobileOptimization(formId),
        mobileAPI.getOfflineSubmissions(),
      ]);
      setOptimization(optimizationData);
      setOfflineSubmissions(offlineData.filter((s: OfflineSubmission) => s.form === formId));
    } catch (error) {
      console.error('Failed to load mobile optimization data:', error);
    } finally {
      setLoading(false);
    }
  }, [formId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleToggleSetting = async (key: keyof Omit<MobileOptimization, 'id' | 'form' | 'created_at' | 'updated_at' | 'pwa_manifest'>) => {
    if (!optimization) return;

    const updated = {
      ...optimization,
      [key]: !optimization[key],
    };

    setSaving(true);
    try {
      await mobileAPI.setMobileOptimization(updated);
      setOptimization(updated);
    } catch (error) {
      console.error('Failed to update setting:', error);
      alert('Failed to update setting');
    } finally {
      setSaving(false);
    }
  };

  const handleSyncOffline = async (submissionId: string) => {
    try {
      await mobileAPI.syncOfflineSubmission(submissionId);
      await loadData();
      alert('Submission synced successfully!');
    } catch (error) {
      console.error('Failed to sync submission:', error);
      alert('Failed to sync submission');
    }
  };

  const settings = [
    {
      key: 'one_field_per_screen' as const,
      label: 'One Field Per Screen',
      description: 'Display one field at a time for better mobile experience',
      icon: '📱',
    },
    {
      key: 'large_tap_targets' as const,
      label: 'Large Tap Targets',
      description: 'Increase button and input sizes for easier tapping',
      icon: '👆',
    },
    {
      key: 'auto_advance_fields' as const,
      label: 'Auto-Advance Fields',
      description: 'Automatically move to next field after completion',
      icon: '⏭️',
    },
    {
      key: 'numeric_keyboard_for_numbers' as const,
      label: 'Numeric Keyboard',
      description: 'Show numeric keyboard for number fields',
      icon: '🔢',
    },
    {
      key: 'simplified_layout' as const,
      label: 'Simplified Layout',
      description: 'Remove unnecessary elements on mobile devices',
      icon: '✨',
    },
    {
      key: 'reduced_animations' as const,
      label: 'Reduced Animations',
      description: 'Minimize animations for better performance',
      icon: '⚡',
    },
    {
      key: 'offline_mode_enabled' as const,
      label: 'Offline Mode',
      description: 'Allow form submissions without internet connection',
      icon: '📶',
    },
  ];

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">Loading mobile settings...</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b">
        <h2 className="text-2xl font-bold">Mobile Optimization</h2>
        <p className="text-gray-600 mt-1">Optimize your form for mobile devices</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
        {/* Settings */}
        <div className="lg:col-span-2">
          <h3 className="font-semibold mb-4">Mobile Settings</h3>
          <div className="space-y-3">
            {settings.map((setting) => (
              <div
                key={setting.key}
                className="flex items-start gap-4 p-4 border rounded hover:bg-gray-50"
              >
                <div className="text-2xl">{setting.icon}</div>
                <div className="flex-1">
                  <h4 className="font-medium">{setting.label}</h4>
                  <p className="text-sm text-gray-600 mt-1">{setting.description}</p>
                </div>
                <label className="relative inline-block w-12 h-6">
                  <input
                    type="checkbox"
                    checked={optimization?.[setting.key] || false}
                    onChange={() => handleToggleSetting(setting.key)}
                    disabled={saving}
                    className="sr-only peer"
                  />
                  <span className="absolute inset-0 bg-gray-300 rounded-full peer-checked:bg-green-600 transition peer-disabled:opacity-50"></span>
                  <span className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition peer-checked:translate-x-6"></span>
                </label>
              </div>
            ))}
          </div>

          {/* PWA Features */}
          <div className="mt-6">
            <h3 className="font-semibold mb-4">Progressive Web App (PWA)</h3>
            <div className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h4 className="font-medium">Install as App</h4>
                  <p className="text-sm text-gray-600 mt-1">
                    Users can install your form as a native app on their devices
                  </p>
                </div>
                <span className="px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded">
                  Enabled
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="p-3 bg-gray-50 rounded">
                  <div className="text-gray-600">Offline Support</div>
                  <div className="font-semibold mt-1">
                    {optimization?.offline_mode_enabled ? 'Enabled' : 'Disabled'}
                  </div>
                </div>
                <div className="p-3 bg-gray-50 rounded">
                  <div className="text-gray-600">Push Notifications</div>
                  <div className="font-semibold mt-1">Supported</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Offline Submissions */}
        <div className="lg:col-span-1">
          <h3 className="font-semibold mb-4">
            Offline Submissions ({offlineSubmissions.length})
          </h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {offlineSubmissions.length === 0 ? (
              <div className="text-center text-gray-500 py-8 text-sm">
                No offline submissions
              </div>
            ) : (
              offlineSubmissions.map((submission) => (
                <div
                  key={submission.id}
                  className="border rounded p-3"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${
                        submission.status === 'synced'
                          ? 'bg-green-100 text-green-700'
                          : submission.status === 'failed'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}
                    >
                      {submission.status}
                    </span>
                    {submission.status === 'pending' && (
                      <button
                        onClick={() => handleSyncOffline(submission.id)}
                        className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                      >
                        Sync
                      </button>
                    )}
                  </div>
                  <div className="text-xs text-gray-600">
                    Created: {new Date(submission.created_at).toLocaleString()}
                  </div>
                  {submission.error_message && (
                    <div className="text-xs text-red-600 mt-1">
                      Error: {submission.error_message}
                    </div>
                  )}
                  {submission.sync_attempts > 0 && (
                    <div className="text-xs text-gray-500 mt-1">
                      Attempts: {submission.sync_attempts}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Mobile Preview */}
      <div className="p-6 border-t bg-gray-50">
        <h3 className="font-semibold mb-4">Mobile Preview</h3>
        <div className="flex justify-center">
          <div className="relative w-80 h-96 bg-white border-4 border-gray-800 rounded-3xl shadow-2xl overflow-hidden">
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-32 h-6 bg-gray-800 rounded-b-2xl"></div>
            <div className="p-6 pt-8 h-full overflow-auto">
              <div className="text-center">
                <h4 className="font-bold text-lg mb-2">Form Preview</h4>
                <p className="text-sm text-gray-600 mb-4">
                  {optimization?.one_field_per_screen
                    ? 'One field per screen mode'
                    : 'Standard layout'}
                </p>
                <div className="space-y-4">
                  <input
                    type="text"
                    placeholder="Sample field"
                    className={`w-full border rounded px-3 ${
                      optimization?.large_tap_targets ? 'py-4 text-lg' : 'py-2'
                    }`}
                    disabled
                  />
                  {!optimization?.one_field_per_screen && (
                    <>
                      <input
                        type="email"
                        placeholder="Email"
                        className={`w-full border rounded px-3 ${
                          optimization?.large_tap_targets ? 'py-4 text-lg' : 'py-2'
                        }`}
                        disabled
                      />
                      <button
                        className={`w-full bg-blue-600 text-white rounded ${
                          optimization?.large_tap_targets ? 'py-4 text-lg' : 'py-2'
                        }`}
                        disabled
                      >
                        Submit
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
