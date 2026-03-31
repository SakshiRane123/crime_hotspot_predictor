/**
 * Browser Notification Utility
 * Handles browser notifications for alerts
 */

export const requestNotificationPermission = async () => {
  if (!('Notification' in window)) {
    console.log('This browser does not support notifications');
    return false;
  }

  if (Notification.permission === 'granted') {
    return true;
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  return false;
};

export const showBrowserNotification = (title, options = {}) => {
  if (!('Notification' in window)) {
    return;
  }

  if (Notification.permission === 'granted') {
    new Notification(title, {
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      ...options
    });
  }
};

export const getAlertMessage = (severity, location) => {
  const city = location?.city || 'Unknown Location';
  const messages = {
    Critical: `🚨 CRITICAL ALERT: Very high crime risk detected at ${city}! Avoid this area immediately.`,
    High: `⚠️ HIGH RISK: Elevated crime risk at ${city}. Exercise extreme caution.`,
    Medium: `⚠️ MODERATE RISK: Moderate crime risk at ${city}. Stay alert.`,
    Low: `✅ LOW RISK: Area appears relatively safe at ${city}.`
  };
  return messages[severity] || messages.Low;
};

export const getAlertType = (severity) => {
  const types = {
    Critical: 'critical',
    High: 'error',
    Medium: 'warning',
    Low: 'success'
  };
  return types[severity] || 'info';
};

