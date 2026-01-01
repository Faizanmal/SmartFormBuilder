/**
 * Audio feedback utilities for voice commands
 */

// Audio context for generating sounds
let audioContext: AudioContext | null = null;

function getAudioContext(): AudioContext {
  if (!audioContext) {
    audioContext = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
  }
  return audioContext;
}

export type SoundType = 'success' | 'error' | 'start' | 'stop' | 'notification' | 'click';

// Generate different types of audio feedback
export function playSound(type: SoundType): void {
  try {
    const ctx = getAudioContext();
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);
    
    const now = ctx.currentTime;
    
    switch (type) {
      case 'success':
        // Pleasant ascending tone
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(523.25, now); // C5
        oscillator.frequency.setValueAtTime(659.25, now + 0.1); // E5
        oscillator.frequency.setValueAtTime(783.99, now + 0.2); // G5
        gainNode.gain.setValueAtTime(0.3, now);
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
        oscillator.start(now);
        oscillator.stop(now + 0.4);
        break;
        
      case 'error':
        // Descending warning tone
        oscillator.type = 'sawtooth';
        oscillator.frequency.setValueAtTime(400, now);
        oscillator.frequency.setValueAtTime(300, now + 0.1);
        oscillator.frequency.setValueAtTime(200, now + 0.2);
        gainNode.gain.setValueAtTime(0.2, now);
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
        oscillator.start(now);
        oscillator.stop(now + 0.3);
        break;
        
      case 'start':
        // Quick high beep
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(880, now); // A5
        gainNode.gain.setValueAtTime(0.3, now);
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
        oscillator.start(now);
        oscillator.stop(now + 0.15);
        break;
        
      case 'stop':
        // Double beep
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(660, now);
        oscillator.frequency.setValueAtTime(0, now + 0.1);
        oscillator.frequency.setValueAtTime(660, now + 0.15);
        gainNode.gain.setValueAtTime(0.3, now);
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
        oscillator.start(now);
        oscillator.stop(now + 0.25);
        break;
        
      case 'notification':
        // Gentle chime
        oscillator.type = 'triangle';
        oscillator.frequency.setValueAtTime(1046.5, now); // C6
        gainNode.gain.setValueAtTime(0.2, now);
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.5);
        oscillator.start(now);
        oscillator.stop(now + 0.5);
        break;
        
      case 'click':
        // Quick click sound
        oscillator.type = 'square';
        oscillator.frequency.setValueAtTime(1000, now);
        gainNode.gain.setValueAtTime(0.1, now);
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.05);
        oscillator.start(now);
        oscillator.stop(now + 0.05);
        break;
    }
  } catch (error) {
    console.warn('Audio playback not available:', error);
  }
}

// Haptic feedback (for mobile devices)
export function vibrate(pattern: number | number[]): void {
  if ('vibrate' in navigator) {
    navigator.vibrate(pattern);
  }
}

// Combined feedback
export function feedback(type: SoundType, haptic: boolean = true): void {
  playSound(type);
  
  if (haptic) {
    switch (type) {
      case 'success':
        vibrate([50, 30, 50]);
        break;
      case 'error':
        vibrate([100, 50, 100, 50, 100]);
        break;
      case 'start':
        vibrate(30);
        break;
      case 'stop':
        vibrate([30, 20, 30]);
        break;
      default:
        vibrate(20);
    }
  }
}

// Text-to-speech utility
export function speak(text: string, options?: { rate?: number; pitch?: number; volume?: number }): Promise<void> {
  return new Promise((resolve, reject) => {
    if (!('speechSynthesis' in window)) {
      reject(new Error('Speech synthesis not supported'));
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = options?.rate ?? 1;
    utterance.pitch = options?.pitch ?? 1;
    utterance.volume = options?.volume ?? 1;
    
    utterance.onend = () => resolve();
    utterance.onerror = (event) => reject(event);
    
    window.speechSynthesis.speak(utterance);
  });
}

// Cancel any ongoing speech
export function stopSpeaking(): void {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}
