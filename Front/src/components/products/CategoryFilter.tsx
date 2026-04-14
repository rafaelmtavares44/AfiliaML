import { Button } from "@/components/ui/button";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

interface CategoryFilterProps {
  categories: string[];
  selected: string;
  onSelect: (category: string) => void;
}

export function CategoryFilter({ categories, selected, onSelect }: CategoryFilterProps) {
  return (
    <ScrollArea className="w-full whitespace-nowrap">
      <div className="flex gap-2 pb-3">
        {categories.map((category) => (
          <Button
            key={category}
            variant={selected === category ? "default" : "outline"}
            size="sm"
            onClick={() => onSelect(category)}
            className={cn(
              "shrink-0 transition-all duration-200",
              selected === category && "shadow-sm"
            )}
          >
            {category}
          </Button>
        ))}
      </div>
      <ScrollBar orientation="horizontal" />
    </ScrollArea>
  );
}
