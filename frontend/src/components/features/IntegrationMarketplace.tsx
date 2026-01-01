'use client';

import { useState, useEffect, useCallback } from 'react';
import { integrationAPI } from '@/lib/advancedFeaturesAPI';
import { IntegrationProvider, IntegrationConnection, IntegrationWorkflow } from '@/types/advancedFeatures';

interface IntegrationMarketplaceProps {
  formId?: string;
}

export default function IntegrationMarketplace({ formId }: IntegrationMarketplaceProps) {
  const [providers, setProviders] = useState<IntegrationProvider[]>([]);
  const [connections, setConnections] = useState<IntegrationConnection[]>([]);
  const [workflows, setWorkflows] = useState<IntegrationWorkflow[]>([]);
  const [activeTab, setActiveTab] = useState<'browse' | 'connections' | 'workflows'>('browse');
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [providersData, connectionsData, workflowsData] = await Promise.all([
        integrationAPI.getProviders(selectedCategory === 'all' ? undefined : selectedCategory),
        integrationAPI.getConnections(),
        formId ? integrationAPI.getWorkflows(formId) : Promise.resolve([]),
      ]);
      setProviders(providersData);
      setConnections(connectionsData);
      setWorkflows(workflowsData);
    } catch (error) {
      console.error('Failed to load integration data:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, formId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleConnect = async (provider: IntegrationProvider) => {
    const name = prompt(`Connect to ${provider.name}.\nEnter a name for this connection:`);
    if (!name) return;

    try {
      const connection = await integrationAPI.createConnection({
        provider: provider.id,
        name,
        credentials: {},
        is_active: true,
      });
      await loadData();
      alert(`Successfully connected to ${provider.name}!`);
    } catch (error) {
      console.error('Failed to create connection:', error);
      alert('Failed to create connection');
    }
  };

  const handleTestConnection = async (connection: IntegrationConnection) => {
    try {
      const result = await integrationAPI.testConnection(connection.id) as { success: boolean; error?: string };
      if (result.success) {
        alert('Connection test successful!');
      } else {
        alert(`Connection test failed: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      alert('Connection test failed');
    }
  };

  const categories = [
    { value: 'all', label: 'All' },
    { value: 'crm', label: 'CRM' },
    { value: 'email', label: 'Email Marketing' },
    { value: 'analytics', label: 'Analytics' },
    { value: 'payment', label: 'Payment' },
    { value: 'storage', label: 'Storage' },
    { value: 'communication', label: 'Communication' },
    { value: 'productivity', label: 'Productivity' },
    { value: 'marketing', label: 'Marketing' },
  ];

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b">
        <h2 className="text-2xl font-bold">Integration Marketplace</h2>
        <p className="text-gray-600 mt-1">Connect your forms to powerful third-party tools</p>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex gap-4 px-6">
          {[
            { key: 'browse', label: 'Browse Integrations' },
            { key: 'connections', label: `My Connections (${connections.length})` },
            { key: 'workflows', label: `Workflows (${workflows.length})` },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as 'browse' | 'connections' | 'workflows')}
              className={`px-4 py-3 font-medium border-b-2 transition ${
                activeTab === tab.key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="p-6">
        {/* Browse Tab */}
        {activeTab === 'browse' && (
          <div>
            {/* Category Filter */}
            <div className="mb-6">
              <div className="flex flex-wrap gap-2">
                {categories.map((cat) => (
                  <button
                    key={cat.value}
                    onClick={() => setSelectedCategory(cat.value)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                      selectedCategory === cat.value
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Provider Grid */}
            {loading ? (
              <div className="text-center py-12">Loading integrations...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {providers.map((provider) => (
                  <div
                    key={provider.id}
                    className="border rounded-lg p-6 hover:shadow-lg transition"
                  >
                    <div className="flex items-start gap-4">
                      {provider.logo_url && (
                        <img
                          src={provider.logo_url}
                          alt={provider.name}
                          className="w-12 h-12 rounded"
                        />
                      )}
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">{provider.name}</h3>
                        <span className="inline-block px-2 py-1 text-xs bg-gray-100 rounded mt-1">
                          {provider.category}
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-600 text-sm mt-3">{provider.description}</p>
                    <div className="mt-4 flex items-center justify-between">
                      <div className="text-xs text-gray-500">
                        ★ {provider.popularity_score} popularity
                      </div>
                      <button
                        onClick={() => handleConnect(provider)}
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                      >
                        Connect
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Connections Tab */}
        {activeTab === 'connections' && (
          <div className="space-y-4">
            {connections.length === 0 ? (
              <div className="text-center text-gray-500 py-12">
                No connections yet. Browse integrations to get started.
              </div>
            ) : (
              connections.map((connection) => (
                <div
                  key={connection.id}
                  className="border rounded-lg p-4 flex items-center justify-between"
                >
                  <div className="flex items-center gap-4">
                    {connection.provider_logo && (
                      <img
                        src={connection.provider_logo}
                        alt={connection.provider_name}
                        className="w-10 h-10 rounded"
                      />
                    )}
                    <div>
                      <h3 className="font-semibold">{connection.name}</h3>
                      <p className="text-sm text-gray-600">{connection.provider_name}</p>
                      {connection.last_sync_at && (
                        <p className="text-xs text-gray-500">
                          Last synced: {new Date(connection.last_sync_at).toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        connection.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {connection.is_active ? 'Active' : 'Inactive'}
                    </span>
                    <button
                      onClick={() => handleTestConnection(connection)}
                      className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                    >
                      Test
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Workflows Tab */}
        {activeTab === 'workflows' && (
          <div className="space-y-4">
            {workflows.length === 0 ? (
              <div className="text-center text-gray-500 py-12">
                No workflows configured. Create automations with your integrations.
              </div>
            ) : (
              workflows.map((workflow) => (
                <div
                  key={workflow.id}
                  className="border rounded-lg p-4"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold">{workflow.name}</h3>
                      {workflow.description && (
                        <p className="text-sm text-gray-600 mt-1">{workflow.description}</p>
                      )}
                      <div className="flex gap-2 mt-2">
                        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                          {workflow.trigger}
                        </span>
                        <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                          {workflow.actions.length} actions
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          workflow.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {workflow.is_active ? 'Active' : 'Inactive'}
                      </span>
                      <p className="text-xs text-gray-500 mt-2">
                        {workflow.execution_count} executions
                      </p>
                      <p className="text-xs text-green-600">
                        {workflow.success_count} successful
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
