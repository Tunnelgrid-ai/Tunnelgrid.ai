import { Question } from '@/types/brandTypes';

// ✅ Using Railway backend - https://dazzling-smile-production.up.railway.app
const API_BASE_URL = 'https://dazzling-smile-production.up.railway.app';

export interface QuestionGenerateRequest {
  auditId: string;
  brandName: string;
  brandDescription?: string;
  brandDomain: string;
  productName: string;
  topics: Array<{ id: string; name: string; description: string }>;
  personas: Array<{
    id: string;
    name: string;
    description: string;
    painPoints: string[];
    motivators: string[];
    demographics: {
      ageRange: string;
      gender: string;
      location: string;
      goals: string[];
    };
  }>;
}

export interface QuestionsResponse {
  success: boolean;
  questions: Question[];
  source: string;
  processingTime: number;
  tokenUsage?: number;
  reason?: string;
}

export interface QuestionsStoreRequest {
  auditId: string;
  questions: Question[];
}

export interface QuestionsStoreResponse {
  success: boolean;
  storedCount: number;
  message: string;
  errors?: string[];
}

export interface QuestionsRetrieveResponse {
  success: boolean;
  questions: Question[];
  message: string;
}

export interface QuestionUpdateResponse {
  success: boolean;
  message: string;
  question?: Question;
  errors?: string[];
}

class QuestionService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_BASE_URL}/api/questions`;
  }

  /**
   * Generate questions using AI based on brand, product, topics, and personas
   */
  async generateQuestions(request: QuestionGenerateRequest): Promise<QuestionsResponse> {
    try {
      console.log('🤖 Generating questions for personas:', request.personas.length);
      console.log('🔗 API Base URL:', API_BASE_URL);
      console.log('🔗 Full URL:', `${this.baseUrl}/generate`);
      console.log('🔗 Request payload:', JSON.stringify(request, null, 2));
      
      const response = await fetch(`${this.baseUrl}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response ok:', response.ok);
      console.log('📡 Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('❌ API Error Response:', errorData);
        throw new Error(`API error: ${response.status} - ${errorData.detail || 'Questions generation failed'}`);
      }

      const data: QuestionsResponse = await response.json();
      
      console.log(`✅ Generated ${data.questions.length} questions via ${data.source}`);
      console.log('📊 Full response data:', data);
      if (data.reason) {
        console.log(`ℹ️ Generation note: ${data.reason}`);
      }

      return data;
    } catch (error) {
      console.error('❌ Question generation failed:', error);
      console.error('❌ Error type:', error instanceof Error ? error.constructor.name : typeof error);
      console.error('❌ Error message:', error instanceof Error ? error.message : String(error));
      throw error;
    }
  }

  /**
   * Store generated questions in the database
   */
  async storeQuestions(request: QuestionsStoreRequest): Promise<QuestionsStoreResponse> {
    try {
      console.log('💾 Storing questions in database:', request.questions.length);
      
      const response = await fetch(`${this.baseUrl}/store`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(`API error: ${response.status} - ${errorData.detail || 'Questions storage failed'}`);
      }

      const data: QuestionsStoreResponse = await response.json();
      
      console.log(`✅ Stored ${data.storedCount} questions successfully`);

      return data;
    } catch (error) {
      console.error('❌ Question storage failed:', error);
      throw error;
    }
  }

  /**
   * Retrieve questions for a specific audit
   */
  async getQuestionsByAudit(auditId: string): Promise<QuestionsRetrieveResponse> {
    try {
      console.log('📚 Retrieving questions for audit:', auditId);
      
      const response = await fetch(`${this.baseUrl}/by-audit/${auditId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(`API error: ${response.status} - ${errorData.detail || 'Questions retrieval failed'}`);
      }

      const data: QuestionsRetrieveResponse = await response.json();
      
      console.log(`✅ Retrieved ${data.questions.length} questions for audit`);

      return data;
    } catch (error) {
      console.error('❌ Question retrieval failed:', error);
      throw error;
    }
  }

  /**
   * Update a specific question
   */
  async updateQuestion(questionId: string, updates: Partial<Question>): Promise<QuestionUpdateResponse> {
    try {
      console.log('📝 Updating question:', questionId, updates);
      
      const updateRequest = {
        text: updates.text,
        topicName: updates.topicName,
        queryType: updates.queryType
      };
      
      const response = await fetch(`${this.baseUrl}/${questionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateRequest),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(`API error: ${response.status} - ${errorData.detail || 'Question update failed'}`);
      }

      const data: QuestionUpdateResponse = await response.json();
      
      console.log(`✅ Updated question successfully:`, data.question);

      return data;
    } catch (error) {
      console.error('❌ Question update failed:', error);
      throw error;
    }
  }

  /**
   * Generate and store questions in one operation
   */
  async generateAndStoreQuestions(request: QuestionGenerateRequest): Promise<{
    generateResponse: QuestionsResponse;
    storeResponse: QuestionsStoreResponse;
  }> {
    try {
      console.log('🔄 Starting question generation and storage process...');
      
      // Step 1: Generate questions
      const generateResponse = await this.generateQuestions(request);
      
      if (!generateResponse.success) {
        throw new Error('Question generation failed');
      }

      // Step 2: Store questions
      const storeResponse = await this.storeQuestions({
        auditId: request.auditId,
        questions: generateResponse.questions,
      });

      if (!storeResponse.success) {
        console.warn('⚠️ Questions generated but storage failed');
      }

      console.log('✅ Question generation and storage process completed');

      return {
        generateResponse,
        storeResponse,
      };
    } catch (error) {
      console.error('❌ Question generation and storage process failed:', error);
      throw error;
    }
  }

  /**
   * Health check for questions service
   */
  async healthCheck(): Promise<{ status: string; services: Record<string, string> }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Question service health check failed:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const questionService = new QuestionService();

// Export individual functions for convenience
export const generateQuestions = (request: QuestionGenerateRequest) => questionService.generateQuestions(request);
export const storeQuestions = (request: QuestionsStoreRequest) => questionService.storeQuestions(request);
export const getQuestionsByAudit = (auditId: string) => questionService.getQuestionsByAudit(auditId);
export const generateAndStoreQuestions = (request: QuestionGenerateRequest) => questionService.generateAndStoreQuestions(request);
export const healthCheck = () => questionService.healthCheck();

/**
 * ENHANCED: Retry question generation for personas with insufficient questions
 * This is called automatically when the frontend detects some personas have < 8 questions
 */
export const retryFailedPersonas = async (request: QuestionGenerateRequest): Promise<{
  generateResponse: QuestionsResponse;
  storeResponse: { success: boolean; message: string };
}> => {
  console.log("🔄 Retrying question generation for failed personas...");
  
  try {
    // Call the retry endpoint
    const response = await fetch(`${API_BASE_URL}/api/questions/retry-failed-personas`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Retry API error: ${response.status} ${response.statusText}`);
    }

    const generateResponse: QuestionsResponse = await response.json();
    console.log("✅ Retry API call successful:", generateResponse);

    // The retry endpoint already stores questions, so we just return success
    const storeResponse = { 
      success: true, 
      message: `Retry completed: ${generateResponse.questions.length} total questions` 
    };

    return { generateResponse, storeResponse };

  } catch (error) {
    console.error("❌ Error in retryFailedPersonas:", error);
    throw error;
  }
};

/**
 * ENHANCED: Analyze question distribution and identify failed personas
 */
export const analyzeQuestionDistribution = (
  questions: Question[], 
  personas: Array<{ id: string; name: string }>
): {
  totalQuestions: number;
  questionsPerPersona: Record<string, number>;
  failedPersonas: Array<{ id: string; name: string; count: number }>;
  needsRetry: boolean;
} => {
  // Group questions by persona
  const questionsByPersona: Record<string, Question[]> = {};
  personas.forEach(persona => {
    const personaQuestions = questions.filter(q => q.personaId === persona.id);
    questionsByPersona[persona.id] = personaQuestions;
  });

  // Calculate counts
  const questionsPerPersona: Record<string, number> = {};
  const failedPersonas: Array<{ id: string; name: string; count: number }> = [];

  personas.forEach(persona => {
    const count = questionsByPersona[persona.id]?.length || 0;
    questionsPerPersona[persona.id] = count;
    
    if (count < 8) {  // Threshold for considering a persona "failed"
      failedPersonas.push({
        id: persona.id,
        name: persona.name,
        count
      });
    }
  });

  return {
    totalQuestions: questions.length,
    questionsPerPersona,
    failedPersonas,
    needsRetry: failedPersonas.length > 0
  };
}; 