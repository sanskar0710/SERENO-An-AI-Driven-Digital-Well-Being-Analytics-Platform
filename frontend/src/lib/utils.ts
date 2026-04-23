import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export function formatTime(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDateTime(date: string | Date): string {
  return `${formatDate(date)} at ${formatTime(date)}`
}

export function getRelativeTime(date: string | Date): string {
  const now = new Date()
  const past = new Date(date)
  const diffInSeconds = Math.floor((now.getTime() - past.getTime()) / 1000)

  if (diffInSeconds < 60) {
    return 'just now'
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60)
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`
  }

  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`
  }

  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) {
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`
  }

  return formatDate(date)
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text
  }
  return text.substring(0, maxLength) + '...'
}

export function getEmotionColor(emotion?: string): string {
  if (!emotion) return '#6b7280'
  const colors: Record<string, string> = {
    joy: '#fbbf24',
    happy: '#fbbf24',
    sadness: '#60a5fa',
    sad: '#60a5fa',
    anger: '#f87171',
    angry: '#f87171',
    fear: '#a78bfa',
    surprise: '#34d399',
    disgust: '#fb923c',
    stress: '#f472b6',
    stressed: '#f472b6',
    anxiety: '#c084fc',
    anxious: '#c084fc',
    calm: '#6ee7b7',
    excitement: '#fbbf24',
    no_data: '#6b7280',
  }
  return colors[emotion] || '#6b7280'
}

export function getEmotionIcon(emotion?: string): string {
  if (!emotion) return '😐'
  const icons: Record<string, string> = {
    joy: '😊',
    happy: '😊',
    sadness: '😢',
    sad: '😢',
    anger: '😠',
    angry: '😠',
    fear: '😨',
    surprise: '😮',
    disgust: '🤢',
    stress: '😰',
    stressed: '😰',
    anxiety: '😟',
    anxious: '😟',
    calm: '😌',
    excitement: '🤗',
    no_data: '📝',
  }
  return icons[emotion] || '😐'
}

export function getMoodColor(mood: number): string {
  if (mood >= 8) return '#10b981' // green
  if (mood >= 6) return '#3b82f6' // blue
  if (mood >= 4) return '#f59e0b' // yellow
  return '#ef4444' // red
}

export function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func.apply(this, args), wait)
  }
}
