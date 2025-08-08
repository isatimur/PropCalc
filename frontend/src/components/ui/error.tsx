import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ErrorProps {
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export function Error({ message = "Something went wrong", onRetry, className }: ErrorProps) {
  return (
    <div className={cn("flex items-center justify-center space-x-2", className)}>
      <AlertTriangle className="h-4 w-4 text-destructive" />
      <span className="text-sm text-destructive">{message}</span>
      {onRetry && (
        <Button variant="ghost" size="sm" onClick={onRetry}>
          <RefreshCw className="h-4 w-4 mr-1" />
          Retry
        </Button>
      )}
    </div>
  );
}

export function ErrorCard({ 
  message = "Failed to load data", 
  onRetry,
  className 
}: ErrorProps) {
  return (
    <div className={cn("flex items-center justify-center p-8", className)}>
      <div className="text-center">
        <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-destructive mb-2">Error</h3>
        <p className="text-sm text-muted-foreground mb-4">{message}</p>
        {onRetry && (
          <Button onClick={onRetry} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        )}
      </div>
    </div>
  );
} 