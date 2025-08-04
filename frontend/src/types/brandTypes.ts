export interface BrandEntity {
  id?: string;
  name: string;
  aliases: string[];
  website: string;
  description?: string;
  socialLinks: SocialLink[];
  wikiUrl?: string;
  knowledgePanel?: boolean;
  editedByUser?: boolean;      // Whether user has modified this brand info
}

export interface SocialLink {
  platform: string;
  url: string;
}

export interface Product {
  id?: string;
  name: string;
  valueProps: string[];
  brandId?: string;
}

export interface Topic {
  id?: string;
  name: string;
  description?: string;
  category: 'unbranded' | 'branded' | 'comparative';
  products?: string[]; // Product IDs
  editedByUser?: boolean;      // Whether user has modified this topic
  createdAt?: string;          // ISO timestamp when topic was created
  updatedAt?: string;          // ISO timestamp when topic was last modified
}

export interface Persona {
  id: string;
  name: string;
  description: string;
  painPoints: string[];
  motivators: string[];
  demographics?: {
    ageRange?: string;
    gender?: string;
    location?: string;
    goals?: string[];
  };
  topicId?: string;
  productId?: string;
  additionalContext?: string;
  editedByUser?: boolean;      // Whether user has modified this persona
}

export interface Question {
  id: string;
  text: string;
  personaId: string;
  auditId?: string;
  topicId?: string;
  topicName?: string;
  topicType?: 'unbranded' | 'branded' | 'comparative';
  queryType?: string; // Legacy field, can be removed later
  aiResponses?: AIResponse[];
  editedByUser?: boolean;      // Whether user has modified this question
}

export interface AIResponse {
  modelName: string;
  response: string;
  timestamp: string;
  sentiment?: number;
  topics?: string[];
  hallucinations?: string[];
}
