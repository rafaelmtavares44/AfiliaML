import { Card, CardContent } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    positive: boolean;
  };
  variant?: "default" | "primary" | "secondary";
}

export function StatsCard({ 
  title, 
  value, 
  icon: Icon, 
  trend,
  variant = "default" 
}: StatsCardProps) {
  return (
    <Card className={cn(
      "transition-all duration-300 hover:shadow-md",
      variant === "primary" && "border-primary/20 bg-primary/5",
      variant === "secondary" && "border-secondary/20 bg-secondary/5"
    )}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold text-foreground">{value}</p>
            {trend && (
              <p className={cn(
                "text-xs font-medium",
                trend.positive ? "text-success" : "text-destructive"
              )}>
                {trend.positive ? "+" : "-"}{Math.abs(trend.value)}% vs mês anterior
              </p>
            )}
          </div>
          <div className={cn(
            "rounded-lg p-3",
            variant === "primary" ? "bg-primary text-primary-foreground" :
            variant === "secondary" ? "bg-secondary text-secondary-foreground" :
            "bg-muted text-muted-foreground"
          )}>
            <Icon className="h-5 w-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
