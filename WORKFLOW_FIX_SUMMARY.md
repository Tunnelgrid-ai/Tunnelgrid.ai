# Workflow Fix Summary: Brand Search to Setup Flow

## Issue Description

The workflow was jumping directly to the analysis status screen instead of going through the proper brand setup wizard flow when a user selected a brand from the search page.

## Root Cause

The issue was caused by session storage persistence logic in `useWizardState.ts`. When a user navigated to the setup page, the application was automatically restoring a previous analysis state from session storage, which immediately showed the analysis loading screen instead of the brand setup wizard.

### Problematic Code Location

```typescript
// In frontend/src/components/setup/hooks/useWizardState.ts (lines 78-85)
useEffect(() => {
  const savedJobId = sessionStorage.getItem('analysisJobId');
  const savedLoading = sessionStorage.getItem('analysisLoading');
  
  if (savedJobId && savedLoading === 'true') {
    setAnalysisJobId(savedJobId);
    setAnalysisLoading(true);
    console.log('🔄 Restored analysis state from session storage');
  }
}, []);
```

This code was automatically restoring any previous analysis state when the component mounted, regardless of whether the user was starting a new brand setup.

## Solution

Added a new `useEffect` hook that clears the analysis state when starting a new brand setup:

```typescript
// Clear analysis state when starting a new brand setup or when no brand is selected
useEffect(() => {
  if (location.state?.selectedBrand) {
    // Clear any existing analysis state when starting a new brand setup
    sessionStorage.removeItem('analysisLoading');
    sessionStorage.removeItem('analysisJobId');
    setAnalysisLoading(false);
    setAnalysisJobId('');
    console.log('🧹 Cleared previous analysis state for new brand setup');
  } else if (!location.state?.selectedBrand && !location.state?.manualSetup) {
    // Also clear analysis state when no brand is selected (prevents lingering state)
    sessionStorage.removeItem('analysisLoading');
    sessionStorage.removeItem('analysisJobId');
    setAnalysisLoading(false);
    setAnalysisJobId('');
    console.log('🧹 Cleared analysis state - no brand selected');
  }
}, [location.state?.selectedBrand, location.state?.manualSetup]);
```

## Changes Made

1. **Added session storage clearing logic** when a new brand is selected for setup
2. **Moved location declaration** to the top of the hook to avoid linter errors
3. **Added fallback clearing** when no brand is selected to prevent lingering state

## Files Modified

- `frontend/src/components/setup/hooks/useWizardState.ts`

## Testing

The fix was verified by:

1. **Backend API testing**: Confirmed all brand search, creation, analysis, and update APIs work correctly
2. **Session storage clearing**: Verified that previous analysis state is properly cleared
3. **Workflow validation**: Ensured the proper flow from brand search → setup wizard → analysis

## Expected Behavior After Fix

1. User searches for a brand on the search page
2. User selects a brand and clicks "Go"
3. User is taken to the brand setup wizard (Brand Info step)
4. User can complete the setup flow normally
5. Only after completing setup and clicking "Submit" does the analysis screen appear

## Prevention

To prevent similar issues in the future:

1. **Always clear session storage** when starting new workflows
2. **Add proper state validation** before restoring persisted state
3. **Use conditional restoration** based on current workflow context
4. **Add logging** to track state transitions for debugging 