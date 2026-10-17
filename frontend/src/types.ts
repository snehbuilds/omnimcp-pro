export interface SlopMatch {
  phrase: string;
  category: string;
  suggestion: string;
  severity: number;
  index: number;
}

export interface HookClassification {
  formula_id: string;
  formula_name: string;
  confidence: number;
  description: string;
  example: string;
}

export interface AuditData {
  slop_score: number;
  slop_rating: string;
  character_count: number;
  word_count: number;
  reading_time_seconds: number;
  flagged_terms: SlopMatch[];
  hook_detected: HookClassification | null;
  advice: string[];
}

export interface TransformedPlatform {
  platform: string;
  body: string;
  first_comment?: string | null;
  thread_items?: string[];
  html_body?: string | null;
  character_count: number;
  warnings: string[];
  metadata?: Record<string, any>;
}

export interface ScheduledPost {
  id: string;
  day: number;
  slot: number;
  theme: string;
  time_utc: string;
  hook_formula: string;
  title: string;
  text: string;
  first_comment?: string | null;
  target_platforms: string[];
  media_paths: string[];
  status: 'PENDING' | 'PUBLISHED' | 'FAILED' | 'SKIPPED';
  published_at?: number | null;
  published_urls?: Record<string, string>;
  metrics?: {
    impressions: number;
    reactions: number;
    comments: number;
    shares: number;
    velocity_score: number;
  } | null;
}

export interface SafetyStatus {
  cooldown_seconds: number;
  cooldown_remaining_seconds: number;
  is_on_cooldown: boolean;
  daily_limit: number;
  posts_today: number;
  can_post_live: boolean;
  write_enabled_in_env: boolean;
  reason?: string | null;
}

export interface PlatformStatus {
  name: string;
  configured: boolean;
  auth_info?: {
    authenticated: boolean;
    name?: string;
    headline?: string;
    vanity_name?: string;
    profile_url?: string;
    response_time_ms?: number;
    error?: string;
  };
}

export interface HookFormula {
  id: string;
  name: string;
  example: string;
  description: string;
}
