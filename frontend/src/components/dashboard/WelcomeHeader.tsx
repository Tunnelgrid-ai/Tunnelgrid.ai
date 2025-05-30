
interface WelcomeHeaderProps {
  brandName?: string;
}

export const WelcomeHeader = ({ brandName = "Your Brand" }: WelcomeHeaderProps) => {
  return (
    <div className="mb-8">
      <h1 className="text-4xl font-bold tracking-tight">
        Welcome to <span className="gradient-text">BrandAI Oracle</span>
      </h1>
      <p className="text-lg text-muted-foreground mt-2">
        Monitor and optimize how {brandName} is perceived by AI systems.
      </p>
    </div>
  );
};
