export interface StyleTemplate {
  id: string
  name: string
  description: string
  use_case: string
}

export interface VoiceSettings {
  voice_id: string
  stability: number
  similarity_boost: number
  style_exaggeration: number
  use_speaker_boost: boolean
}

export interface StatusUpdate {
  service: string
  status: string
  message: string
  percentage?: number
  eta_seconds?: number
  tokens_used?: number
  estimated_cost?: number
}

export interface DialogueSegment {
  speaker: string
  text: string
}

export interface ExportFormat {
  id: string
  name: string
  description: string
  extension: string
  use_case: string
}

export interface PodcastVersion {
  version_id: string
  job_id: string
  created_at: string
  dialogue: DialogueSegment[]
  segment_count: number
  edits_count: number
  parent_version?: string
  content_hash: string
}

export interface SavedPodcast {
  job_id: string
  filename: string
  created_at: string
  size: number
  transcription_params: any
}
