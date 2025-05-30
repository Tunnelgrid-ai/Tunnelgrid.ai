#!/usr/bin/env typescript
/**
 * Test the frontend filtering logic with the fixed types
 */

// Simulate the fixed types
interface Question {
  id: string;
  text: string;
  personaId: string;
  auditId?: string;
  topicName?: string;
  queryType?: string;
}

interface Persona {
  id: string;
  name: string;
  description: string;
  painPoints: string[];
  motivators: string[];
}

function testFrontendFiltering() {
  console.log("🧪 Testing Frontend Filtering Logic...");
  
  // Sample data that matches the Postman response structure
  const personas: Persona[] = [
    {
      id: "persona-1",
      name: "Daily Commuter",
      description: "Regular commuters who rely on GO Transit for their daily work travel",
      painPoints: ["Long wait times", "Service delays", "Crowded trains"],
      motivators: ["Reliable schedule", "Comfortable journey", "Cost effectiveness"]
    },
    {
      id: "persona-2", 
      name: "Family Traveler",
      description: "Families using GO Transit for weekend trips and special events",
      painPoints: ["Complex ticketing", "Limited family amenities", "Safety concerns"],
      motivators: ["Family-friendly service", "Convenience", "Safety"]
    }
  ];

  const questions: Question[] = [
    {
      id: "298b890a-a0f6-4246-afd0-ae04bf713dff",
      text: "How reliable is the TTC schedule for my daily commute, and are there any plans to improve punctuality?",
      personaId: "persona-1",
      auditId: "test-audit-123",
      topicName: "Service Reliability",
      queryType: "brand_analysis"
    },
    {
      id: "ee6cfa46-8020-4a37-b6c0-64cde86ccc1a",
      text: "What measures is TTC taking to reduce wait times and service delays during peak hours?",
      personaId: "persona-1",
      auditId: "test-audit-123",
      topicName: "Service Reliability",
      queryType: "brand_analysis"
    },
    {
      id: "717d7fec-5cdd-4de2-b397-325bfc53dff5",
      text: "How easy is it to purchase tickets or load funds onto my Presto card for family trips on GO Transit?",
      personaId: "persona-2",
      auditId: "test-audit-123",
      topicName: "Customer Experience",
      queryType: "brand_analysis"
    },
    {
      id: "98de9bf5-fa24-463f-92c7-f084d5a0fef5",
      text: "What family-friendly amenities are available on GO Transit trains and at stations, such as play areas or nursing rooms?",
      personaId: "persona-2",
      auditId: "test-audit-123",
      topicName: "Customer Experience", 
      queryType: "brand_analysis"
    }
  ];

  console.log("📊 Input Data:");
  console.log(`  Personas: ${personas.length}`);
  console.log(`  Questions: ${questions.length}`);
  
  // Test the filtering logic (same as frontend)
  const questionsByPersona: Record<string, Question[]> = {};
  personas.forEach(persona => {
    const personaQuestions = questions.filter(q => q.personaId === persona.id);
    questionsByPersona[persona.id] = personaQuestions.slice(0, 10);
  });

  console.log("\n🎯 Filtering Results:");
  console.log("questionsByPersona:", questionsByPersona);
  
  // Verify each persona has questions
  personas.forEach(persona => {
    const personaQuestions = questionsByPersona[persona.id] || [];
    console.log(`\n📋 ${persona.name} (${persona.id}):`);
    console.log(`  Questions found: ${personaQuestions.length}`);
    
    if (personaQuestions.length > 0) {
      console.log("  First question:", personaQuestions[0].text.substring(0, 60) + "...");
      console.log("  ✅ SUCCESS: Questions found for this persona");
    } else {
      console.log("  ❌ FAILED: No questions found for this persona");
    }
  });

  // Check for orphaned questions
  const allPersonaIds = new Set(personas.map(p => p.id));
  const questionPersonaIds = new Set(questions.map(q => q.personaId));
  const orphanedQuestions = questions.filter(q => !allPersonaIds.has(q.personaId));
  
  if (orphanedQuestions.length > 0) {
    console.log("\n⚠️ ORPHANED QUESTIONS (questions with invalid persona IDs):");
    orphanedQuestions.forEach(q => {
      console.log(`  - ${q.id}: "${q.text.substring(0, 40)}..." (personaId: ${q.personaId})`);
    });
  } else {
    console.log("\n✅ No orphaned questions found");
  }

  // Summary
  const totalGroupedQuestions = Object.values(questionsByPersona).reduce((sum, arr) => sum + arr.length, 0);
  console.log("\n📊 SUMMARY:");
  console.log(`  Total input questions: ${questions.length}`);
  console.log(`  Total grouped questions: ${totalGroupedQuestions}`);
  console.log(`  Personas with questions: ${Object.keys(questionsByPersona).filter(id => questionsByPersona[id].length > 0).length}/${personas.length}`);
  
  if (totalGroupedQuestions === questions.length) {
    console.log("✅ ALL TESTS PASSED: All questions properly grouped by persona");
    return true;
  } else {
    console.log("❌ TESTS FAILED: Question count mismatch");
    return false;
  }
}

// Run the test
testFrontendFiltering(); 