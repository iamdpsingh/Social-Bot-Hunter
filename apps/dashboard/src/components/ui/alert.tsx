import React, { forwardRef } from "react";
import { AlertCircle, CheckCircle2, Info, AlertTriangle } from "lucide-react";
import { cn } from "../../lib/utils";

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "destructive" | "warning" | "success";
  title?: string;
}

export const Alert = forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = "default", title, children, ...props }, ref) => {
    const variants = {
      default: "bg-blue-500/10 text-blue-400 border-blue-500/20 [&>svg]:text-blue-400",
      destructive: "bg-red-500/10 text-red-400 border-red-500/20 [&>svg]:text-red-400",
      warning: "bg-amber-500/10 text-amber-400 border-amber-500/20 [&>svg]:text-amber-400",
      success: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 [&>svg]:text-emerald-400",
    };

    const icons = {
      default: Info,
      destructive: AlertCircle,
      warning: AlertTriangle,
      success: CheckCircle2,
    };

    const Icon = icons[variant];

    return (
      <div
        ref={ref}
        role="alert"
        className={cn(
          "relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4",
          variants[variant],
          className
        )}
        {...props}
      >
        <Icon className="h-4 w-4" />
        {title && <h5 className="mb-1 font-semibold leading-none tracking-tight">{title}</h5>}
        <div className="text-sm opacity-90">{children}</div>
      </div>
    );
  }
);

Alert.displayName = "Alert";
