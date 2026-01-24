import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "bg-primary-100 text-primary-700 border border-primary-200",
        secondary:
          "bg-secondary-100 text-secondary-700 border border-secondary-200",
        success:
          "bg-success-50 text-success-600 border border-success-500/20",
        warning:
          "bg-warning-50 text-warning-600 border border-warning-500/20",
        error:
          "bg-error-50 text-error-600 border border-error-500/20",
        destructive:
          "bg-error-50 text-error-600 border border-error-500/20",
        info:
          "bg-info-50 text-info-600 border border-info-500/20",
        accent:
          "bg-accent-500/10 text-accent-600 border border-accent-500/20",
        outline:
          "bg-transparent border border-border text-foreground",
        gold:
          "bg-gold-400/10 text-gold-600 border border-gold-400/20",
      },
      size: {
        sm: "px-2 py-0.5 text-[10px]",
        default: "px-3 py-1 text-xs",
        lg: "px-4 py-1.5 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  /** Optional dot indicator */
  dot?: boolean;
}

function Badge({ className, variant, size, dot, children, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props}>
      {dot && (
        <span
          className={cn(
            "w-1.5 h-1.5 rounded-full me-1.5",
            variant === "success" && "bg-success-500",
            variant === "warning" && "bg-warning-500",
            variant === "error" || variant === "destructive" ? "bg-error-500" : "",
            variant === "info" && "bg-info-500",
            variant === "default" && "bg-primary-500",
            variant === "accent" && "bg-accent-500",
            variant === "gold" && "bg-gold-500",
            (!variant || variant === "secondary" || variant === "outline") && "bg-secondary-500"
          )}
        />
      )}
      {children}
    </div>
  );
}

export { Badge, badgeVariants };
