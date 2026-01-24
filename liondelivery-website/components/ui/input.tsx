import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";

const inputVariants = cva(
  "flex w-full rounded-[var(--radius-lg)] text-base text-foreground placeholder:text-muted-foreground transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-secondary-50 border border-secondary-200 focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-400 hover:border-secondary-300",
        outlined:
          "bg-white border border-border focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-400 hover:border-secondary-300",
        ghost:
          "bg-transparent border-none focus:outline-none focus:ring-0 hover:bg-secondary-50",
      },
      inputSize: {
        sm: "h-9 px-3 text-sm",
        default: "h-11 px-4",
        lg: "h-12 px-5 text-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      inputSize: "default",
    },
  }
);

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size">,
    VariantProps<typeof inputVariants> {
  error?: boolean;
  icon?: React.ReactNode;
  iconPosition?: "start" | "end";
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      type,
      error,
      icon,
      iconPosition = "start",
      variant,
      inputSize,
      ...props
    },
    ref
  ) => {
    // Determine RTL-aware icon positioning
    const isRTL = typeof document !== "undefined" && document.dir === "rtl";
    const iconAtStart = iconPosition === "start";

    return (
      <div className="relative w-full">
        {icon && (
          <div
            className={cn(
              "absolute top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none",
              iconAtStart
                ? "start-3 [&>svg]:h-5 [&>svg]:w-5"
                : "end-3 [&>svg]:h-5 [&>svg]:w-5"
            )}
          >
            {icon}
          </div>
        )}
        <input
          type={type}
          className={cn(
            inputVariants({ variant, inputSize }),
            error &&
              "border-error-400 focus:ring-error-500/30 focus:border-error-500 bg-error-50/50",
            icon && iconAtStart && "ps-10",
            icon && !iconAtStart && "pe-10",
            className
          )}
          ref={ref}
          {...props}
        />
      </div>
    );
  }
);
Input.displayName = "Input";

export { Input, inputVariants };
