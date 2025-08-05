/**
 * Browser Console Testing Script for Audit Flow
 * 
 * Copy and paste this into your browser console to test the frontend audit flow
 * without going through the entire wizard process.
 * 
 * Usage:
 * 1. Open your app in the browser
 * 2. Open browser console (F12)
 * 3. Copy and paste this script
 * 4. Call the test functions
 */

// Test configuration
const TEST_AUDIT_ID = 'your-audit-id-here'; // Replace with real audit ID

/**
 * Test the markSetupComplete function
 */
async function testMarkSetupComplete(auditId = TEST_AUDIT_ID) {
    console.log('🧪 Testing markSetupComplete...');
    
    try {
        // Import the function dynamically
        const { markSetupComplete } = await import('/src/services/auditService.js');
        
        const result = await markSetupComplete(auditId);
        
        console.log('📋 Result:', result);
        
        if (result.success) {
            console.log('✅ Setup marked as complete successfully');
            console.log('📊 Status:', result.data?.status);
        } else {
            console.log('❌ Failed to mark setup complete:', result.error);
        }
        
        return result;
        
    } catch (error) {
        console.error('💥 Error testing markSetupComplete:', error);
        return null;
    }
}

/**
 * Test the completeAudit function
 */
async function testCompleteAudit(auditId = TEST_AUDIT_ID) {
    console.log('🧪 Testing completeAudit...');
    
    try {
        // Import the function dynamically
        const { completeAudit } = await import('/src/services/auditService.js');
        
        const result = await completeAudit(auditId);
        
        console.log('📋 Result:', result);
        
        if (result.success) {
            console.log('✅ Audit completed successfully');
            console.log('📊 Status:', result.data?.status);
        } else {
            console.log('❌ Failed to complete audit:', result.error);
        }
        
        return result;
        
    } catch (error) {
        console.error('💥 Error testing completeAudit:', error);
        return null;
    }
}

/**
 * Test the runCompleteAnalysis function
 */
async function testRunCompleteAnalysis(auditId = TEST_AUDIT_ID) {
    console.log('🧪 Testing runCompleteAnalysis...');
    
    try {
        // Import the function dynamically
        const { runCompleteAnalysis } = await import('/src/services/analysisService.js');
        
        const result = await runCompleteAnalysis(auditId, (status) => {
            console.log('📊 Progress:', status.progress_percentage + '%');
        });
        
        console.log('📋 Result:', result);
        
        if (result.success) {
            console.log('✅ Analysis completed successfully');
            console.log('📊 Total responses:', result.data?.total_responses);
        } else {
            console.log('❌ Failed to run analysis:', result.error);
        }
        
        return result;
        
    } catch (error) {
        console.error('💥 Error testing runCompleteAnalysis:', error);
        return null;
    }
}

/**
 * Test the complete audit flow
 */
async function testCompleteAuditFlow(auditId = TEST_AUDIT_ID) {
    console.log('🧪 Testing Complete Audit Flow...');
    console.log('=' .repeat(50));
    
    try {
        // Step 1: Mark setup as complete
        console.log('1️⃣ Step 1: Mark setup as complete');
        const setupResult = await testMarkSetupComplete(auditId);
        
        if (!setupResult?.success) {
            console.log('❌ Setup failed, stopping test');
            return;
        }
        
        console.log();
        
        // Step 2: Run complete analysis
        console.log('2️⃣ Step 2: Run complete analysis');
        const analysisResult = await testRunCompleteAnalysis(auditId);
        
        if (!analysisResult?.success) {
            console.log('❌ Analysis failed');
            return;
        }
        
        console.log();
        console.log('✅ Complete audit flow test finished!');
        
    } catch (error) {
        console.error('💥 Error in complete flow test:', error);
    }
}

/**
 * Test the wizard state submitSetup function
 */
async function testWizardStateSubmitSetup(auditId = TEST_AUDIT_ID) {
    console.log('🧪 Testing Wizard State submitSetup...');
    
    try {
        // This would require setting up the wizard state properly
        // For now, we'll test the individual functions
        
        console.log('📝 Note: Testing individual functions instead of full wizard state');
        console.log('💡 Use testCompleteAuditFlow() for a more complete test');
        
        return await testCompleteAuditFlow(auditId);
        
    } catch (error) {
        console.error('💥 Error testing wizard state:', error);
        return null;
    }
}

/**
 * Test API endpoints directly
 */
async function testAPIEndpoints(auditId = TEST_AUDIT_ID) {
    console.log('🧪 Testing API Endpoints Directly...');
    
    try {
        // Test mark-setup-complete endpoint
        console.log('1️⃣ Testing PUT /api/audits/{id}/mark-setup-complete');
        const setupResponse = await fetch(`/api/audits/${auditId}/mark-setup-complete`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' }
        });
        
        console.log('   Status:', setupResponse.status);
        if (setupResponse.ok) {
            const setupData = await setupResponse.json();
            console.log('   Response:', setupData);
        } else {
            console.log('   Error:', await setupResponse.text());
        }
        
        console.log();
        
        // Test analysis start endpoint
        console.log('2️⃣ Testing POST /api/analysis/start');
        const analysisResponse = await fetch('/api/analysis/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ audit_id: auditId })
        });
        
        console.log('   Status:', analysisResponse.status);
        if (analysisResponse.ok) {
            const analysisData = await analysisResponse.json();
            console.log('   Response:', analysisData);
        } else {
            console.log('   Error:', await analysisResponse.text());
        }
        
        console.log();
        
        // Test complete endpoint
        console.log('3️⃣ Testing PUT /api/audits/{id}/complete');
        const completeResponse = await fetch(`/api/audits/${auditId}/complete`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' }
        });
        
        console.log('   Status:', completeResponse.status);
        if (completeResponse.ok) {
            const completeData = await completeResponse.json();
            console.log('   Response:', completeData);
        } else {
            console.log('   Error:', await completeResponse.text());
        }
        
    } catch (error) {
        console.error('💥 Error testing API endpoints:', error);
    }
}

// Helper function to set a test audit ID
function setTestAuditId(auditId) {
    console.log(`🔧 Setting test audit ID to: ${auditId}`);
    TEST_AUDIT_ID = auditId;
    console.log('💡 Now you can run the test functions without parameters');
}

// Export functions for easy access
window.testAuditFlow = {
    testMarkSetupComplete,
    testCompleteAudit,
    testRunCompleteAnalysis,
    testCompleteAuditFlow,
    testWizardStateSubmitSetup,
    testAPIEndpoints,
    setTestAuditId
};

console.log('🎉 Audit Flow Testing Script Loaded!');
console.log('📋 Available functions:');
console.log('  - testMarkSetupComplete(auditId)');
console.log('  - testCompleteAudit(auditId)');
console.log('  - testRunCompleteAnalysis(auditId)');
console.log('  - testCompleteAuditFlow(auditId)');
console.log('  - testWizardStateSubmitSetup(auditId)');
console.log('  - testAPIEndpoints(auditId)');
console.log('  - setTestAuditId(auditId)');
console.log('');
console.log('💡 Example usage:');
console.log('  setTestAuditId("your-audit-id-here")');
console.log('  testCompleteAuditFlow()'); 