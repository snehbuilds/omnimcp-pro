export const PLATFORM_IDS = ['linkedin', 'twitter', 'wordpress', 'threads', 'facebook'] as const;

export type PlatformId = (typeof PLATFORM_IDS)[number];

interface PlatformMeta {
  label: string;
  short: string;
  glyph: string;
  bg: string;
  fg: string;
}

export const PLATFORM_META: Record<PlatformId, PlatformMeta> = {
  linkedin: { label: 'LinkedIn', short: 'LinkedIn', glyph: 'in', bg: '#0a66c2', fg: '#fff' },
  twitter: { label: 'X (Twitter)', short: 'X', glyph: 'X', bg: '#fafafa', fg: '#09090b' },
  wordpress: { label: 'WordPress', short: 'WP', glyph: 'W', bg: '#21759b', fg: '#fff' },
  threads: { label: 'Threads', short: 'Threads', glyph: '@', bg: '#27272a', fg: '#fff' },
  facebook: { label: 'Facebook', short: 'Facebook', glyph: 'f', bg: '#1877f2', fg: '#fff' },
};

export const getPlatformMeta = (id: string): PlatformMeta =>
  PLATFORM_META[id as PlatformId] ?? { label: id, short: id, glyph: id.charAt(0).toUpperCase(), bg: '#3f3f46', fg: '#fff' };
