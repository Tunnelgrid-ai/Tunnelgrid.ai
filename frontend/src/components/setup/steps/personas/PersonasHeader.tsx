
export const PersonasHeader = () => {
  return (
    <div>
      <h2 className="text-xl font-heading font-semibold mb-2">Personas</h2>
      <p className="text-text-secondary mb-4">
        Answer engines like ChatGPT, Perplexity, and Gemini build rich user profiles from tiny clues. The closer our personas match real people, the better the prompts and recommendations.
      </p>
      <div className="space-y-2">
        <h3 className="text-lg font-medium">What to do</h3>
        <ul className="text-text-secondary space-y-1">
          <li>• Review each persona.</li>
          <li>• Fix anything that feels off.</li>
          <li>• Add clear traits—goals, struggles, interests, context.</li>
        </ul>
        <p className="text-text-secondary mt-3">
        In the next step we will generate questions that these personas will ask. Clearer personas yield better answers.
        </p>
      </div>
    </div>
  );
};
