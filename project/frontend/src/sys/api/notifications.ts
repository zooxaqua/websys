/**
 * 通知API
 * 
 * システム共通基盤の通知機能APIクライアントを提供します。
 * - 通知一覧取得
 * - 通知を既読にする
 * - 通知削除
 * - SSEによるリアルタイム通知受信
 */

import { get, put, del } from '../utils/fetch';

/**
 * 通知型
 */
export interface Notification {
  id: string;
  userId: string;
  type: string;
  title: string;
  message: string;
  metadata: Record<string, unknown>;
  read: boolean;
  createdAt: string;
  expiresAt: string | null;
}

/**
 * 通知一覧レスポンス
 */
export interface NotificationsResponse {
  notifications: Notification[];
  total: number;
  unreadCount: number;
}

/**
 * 通知一覧を取得
 * 
 * @param unreadOnly - 未読のみ取得するか
 * @param limit - 取得件数
 * @param offset - スキップ件数
 * @returns 通知一覧
 */
export async function getNotifications(
  unreadOnly = false,
  limit = 50,
  offset = 0
): Promise<NotificationsResponse> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });

  if (unreadOnly) {
    params.append('unread_only', 'true');
  }

  return get<NotificationsResponse>(`/api/sys/notifications?${params.toString()}`);
}

/**
 * 通知を既読にする
 * 
 * @param notificationId - 通知ID
 */
export async function markNotificationAsRead(notificationId: string): Promise<void> {
  await put(`/api/sys/notifications/${notificationId}/read`, {});
}

/**
 * 通知を削除
 * 
 * @param notificationId - 通知ID
 */
export async function deleteNotification(notificationId: string): Promise<void> {
  await del(`/api/sys/notifications/${notificationId}`);
}

/**
 * すべての通知を既読にする
 */
export async function markAllNotificationsAsRead(): Promise<void> {
  await put('/api/sys/notifications/read-all', {});
}

/**
 * SSEで通知をリアルタイム受信
 * 
 * @param onNotification - 通知受信時のコールバック
 * @returns EventSourceインスタンス（接続を閉じる際に使用）
 */
export function subscribeToNotifications(
  onNotification: (notification: Notification) => void
): EventSource {
  const eventSource = new EventSource('/api/sys/notifications/stream', {
    withCredentials: true, // httpOnly Cookie送信
  });

  eventSource.onmessage = (event) => {
    try {
      const notification: Notification = JSON.parse(event.data);
      onNotification(notification);
    } catch (error) {
      console.error('Failed to parse notification:', error);
    }
  };

  eventSource.onerror = (error) => {
    console.error('Notification stream error:', error);
    // エラー時は自動再接続される（EventSourceの仕様）
  };

  return eventSource;
}

/**
 * 通知ストリームを閉じる
 * 
 * @param eventSource - EventSourceインスタンス
 */
export function unsubscribeFromNotifications(eventSource: EventSource): void {
  if (eventSource) {
    eventSource.close();
  }
}
