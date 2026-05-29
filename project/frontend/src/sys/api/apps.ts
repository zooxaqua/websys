/**
 * アプリ管理API
 */
import { http } from '../utils/http';

export interface App {
  id: string;
  name: string;
  version: string;
  description: string;
  icon: string;
  entryPoint: string;
  apiPrefix: string;
  enabled: boolean;
  author: string;
  lastUpdated: string;
}

export async function listApps(enabled?: boolean): Promise<App[]> {
  const params = new URLSearchParams();
  if (enabled !== undefined) params.append('enabled', enabled.toString());
  
  return http.get<App[]>(`/api/sys/apps?${params.toString()}`);
}

export async function getApp(appId: string): Promise<App> {
  return http.get<App>(`/api/sys/apps/${appId}`);
}

export async function scanApps(): Promise<{ success: boolean; message: string; apps: App[] }> {
  return http.post<{ success: boolean; message: string; apps: App[] }>('/api/sys/apps/scan', {});
}

export async function enableApp(appId: string): Promise<void> {
  await http.put<void>(`/api/sys/apps/${appId}/enable`, {});
}

export async function disableApp(appId: string): Promise<void> {
  await http.put<void>(`/api/sys/apps/${appId}/disable`, {});
}
