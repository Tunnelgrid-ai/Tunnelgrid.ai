/**
 * Test Wizard State Flow
 * 
 * Tests the useWizardState hook's submitSetup function:
 * - Validation logic
 * - markSetupComplete call
 * - runCompleteAnalysis call
 * - Error handling
 */

import { renderHook, act } from '@testing-library/react';
import { useWizardState } from '../../frontend/src/components/setup/hooks/useWizardState';

// Mock the services
jest.mock('../../frontend/src/services/auditService', () => ({
  markSetupComplete: jest.fn(),
  completeAudit: jest.fn()
}));

jest.mock('../../frontend/src/services/analysisService', () => ({
  runCompleteAnalysis: jest.fn()
}));

import { markSetupComplete } from '../../frontend/src/services/auditService';
import { runCompleteAnalysis } from '../../frontend/src/services/analysisService';

const mockMarkSetupComplete = markSetupComplete as jest.MockedFunction<typeof markSetupComplete>;
const mockRunCompleteAnalysis = runCompleteAnalysis as jest.MockedFunction<typeof runCompleteAnalysis>;

describe('Wizard State Submit Flow', () => {
  const mockAuditId = '123e4567-e89b-12d3-a456-426614174000';
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should successfully complete the setup flow', async () => {
    // Mock successful responses
    mockMarkSetupComplete.mockResolvedValue({
      success: true,
      data: { audit_id: mockAuditId, status: 'setup_completed' }
    });

    mockRunCompleteAnalysis.mockResolvedValue({
      success: true,
      data: { /* analysis results */ }
    });

    const { result } = renderHook(() => useWizardState());

    // Set up the required state
    act(() => {
      result.current.setAuditId(mockAuditId);
      result.current.setBrandInfo({
        name: 'Test Brand',
        website: 'test.com',
        aliases: [],
        socialLinks: []
      });
      result.current.setProducts([{ id: '1', name: 'Test Product', valueProps: [] }]);
      result.current.setTopics([{ id: '1', name: 'Test Topic', category: 'unbranded' }]);
      result.current.setPersonas([{ id: '1', name: 'Test Persona', description: 'Test' }]);
      result.current.setQuestions([{ id: '1', text: 'Test Question', personaId: '1', topicName: 'Test Topic' }]);
    });

    // Call submitSetup
    await act(async () => {
      await result.current.submitSetup();
    });

    // Verify markSetupComplete was called
    expect(mockMarkSetupComplete).toHaveBeenCalledWith(mockAuditId);
    
    // Verify runCompleteAnalysis was called
    expect(mockRunCompleteAnalysis).toHaveBeenCalledWith(mockAuditId, expect.any(Function));
  });

  it('should fail when audit ID is missing', async () => {
    const { result } = renderHook(() => useWizardState());

    // Don't set audit ID
    act(() => {
      result.current.setBrandInfo({
        name: 'Test Brand',
        website: 'test.com',
        aliases: [],
        socialLinks: []
      });
      // ... set other required data
    });

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    await act(async () => {
      await result.current.submitSetup();
    });

    expect(consoleSpy).toHaveBeenCalledWith('❌ No audit ID available for completion');
    expect(mockMarkSetupComplete).not.toHaveBeenCalled();
    expect(mockRunCompleteAnalysis).not.toHaveBeenCalled();

    consoleSpy.mockRestore();
  });

  it('should fail when required data is missing', async () => {
    const { result } = renderHook(() => useWizardState());

    // Set audit ID but no other data
    act(() => {
      result.current.setAuditId(mockAuditId);
    });

    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

    await act(async () => {
      await result.current.submitSetup();
    });

    expect(consoleSpy).toHaveBeenCalledWith('❌ Validation failed:', expect.any(Object));
    expect(mockMarkSetupComplete).not.toHaveBeenCalled();
    expect(mockRunCompleteAnalysis).not.toHaveBeenCalled();

    consoleSpy.mockRestore();
  });

  it('should handle markSetupComplete failure', async () => {
    mockMarkSetupComplete.mockResolvedValue({
      success: false,
      error: 'Database error'
    });

    const { result } = renderHook(() => useWizardState());

    // Set up required state
    act(() => {
      result.current.setAuditId(mockAuditId);
      result.current.setBrandInfo({
        name: 'Test Brand',
        website: 'test.com',
        aliases: [],
        socialLinks: []
      });
      result.current.setProducts([{ id: '1', name: 'Test Product', valueProps: [] }]);
      result.current.setTopics([{ id: '1', name: 'Test Topic', category: 'unbranded' }]);
      result.current.setPersonas([{ id: '1', name: 'Test Persona', description: 'Test' }]);
      result.current.setQuestions([{ id: '1', text: 'Test Question', personaId: '1', topicName: 'Test Topic' }]);
    });

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    await act(async () => {
      await result.current.submitSetup();
    });

    expect(consoleSpy).toHaveBeenCalledWith('❌ Setup completion failed:', 'Database error');
    expect(mockRunCompleteAnalysis).not.toHaveBeenCalled();

    consoleSpy.mockRestore();
  });
});

// Manual testing function
export async function testWizardStateFlow(auditId: string) {
  console.log('🧪 Testing Wizard State Flow...');
  
  const { result } = renderHook(() => useWizardState());
  
  try {
    // Set up mock data
    act(() => {
      result.current.setAuditId(auditId);
      result.current.setBrandInfo({
        name: 'Test Brand',
        website: 'test.com',
        aliases: [],
        socialLinks: []
      });
      result.current.setProducts([{ id: '1', name: 'Test Product', valueProps: [] }]);
      result.current.setTopics([{ id: '1', name: 'Test Topic', category: 'unbranded' }]);
      result.current.setPersonas([{ id: '1', name: 'Test Persona', description: 'Test' }]);
      result.current.setQuestions([{ id: '1', text: 'Test Question', personaId: '1', topicName: 'Test Topic' }]);
    });

    console.log('📋 Mock data set up, calling submitSetup...');
    
    await act(async () => {
      await result.current.submitSetup();
    });
    
    console.log('✅ submitSetup completed');
    
  } catch (error) {
    console.error('💥 Error testing wizard state flow:', error);
  }
}

// Example usage:
// testWizardStateFlow('your-real-audit-id-here'); 