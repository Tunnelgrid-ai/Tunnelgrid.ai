/**
 * Test Audit Service Flow
 * 
 * Tests the frontend audit service functions:
 * - markSetupComplete()
 * - completeAudit()
 * - Integration with analysis service
 */

import { markSetupComplete, completeAudit } from '../../frontend/src/services/auditService';

// Mock fetch for testing
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('Audit Service Flow', () => {
  const mockAuditId = '123e4567-e89b-12d3-a456-426614174000';
  
  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe('markSetupComplete', () => {
    it('should successfully mark setup as complete', async () => {
      const mockResponse = {
        success: true,
        data: {
          audit_id: mockAuditId,
          status: 'setup_completed'
        },
        message: 'Audit setup marked as complete'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await markSetupComplete(mockAuditId);

      expect(result.success).toBe(true);
      expect(result.data?.status).toBe('setup_completed');
      expect(mockFetch).toHaveBeenCalledWith(
        `/api/audits/${mockAuditId}/mark-setup-complete`,
        expect.objectContaining({
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          }
        })
      );
    });

    it('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        text: async () => 'Audit not found'
      });

      const result = await markSetupComplete(mockAuditId);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Audit not found');
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await markSetupComplete(mockAuditId);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Network error');
    });
  });

  describe('completeAudit', () => {
    it('should successfully complete audit after analysis', async () => {
      const mockResponse = {
        success: true,
        data: {
          audit_id: mockAuditId,
          status: 'completed'
        },
        message: 'Audit completed successfully after analysis'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await completeAudit(mockAuditId);

      expect(result.success).toBe(true);
      expect(result.data?.status).toBe('completed');
      expect(mockFetch).toHaveBeenCalledWith(
        `/api/audits/${mockAuditId}/complete`,
        expect.objectContaining({
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          }
        })
      );
    });
  });
});

// Manual testing function
export async function testAuditServiceFlow(auditId: string) {
  console.log('🧪 Testing Audit Service Flow...');
  
  try {
    // Test markSetupComplete
    console.log('1️⃣ Testing markSetupComplete...');
    const setupResult = await markSetupComplete(auditId);
    console.log('   Result:', setupResult);
    
    if (setupResult.success) {
      console.log('   ✅ Setup marked as complete');
      
      // Test completeAudit (this would normally be called by backend)
      console.log('2️⃣ Testing completeAudit...');
      const completeResult = await completeAudit(auditId);
      console.log('   Result:', completeResult);
      
      if (completeResult.success) {
        console.log('   ✅ Audit marked as completed');
      } else {
        console.log('   ❌ Failed to complete audit:', completeResult.error);
      }
    } else {
      console.log('   ❌ Failed to mark setup complete:', setupResult.error);
    }
    
  } catch (error) {
    console.error('💥 Error testing audit service flow:', error);
  }
}

// Example usage:
// testAuditServiceFlow('your-real-audit-id-here'); 