import React from "react";
import { cn } from "@/lib/utils";

interface EventStickyNoteProps {
  name: string;
  startDateTime: string;
  duration: number;
  recurringDays?: string[];
}

export function EventStickyNote({
  name,
  startDateTime,
  duration,
  recurringDays = [],
}: EventStickyNoteProps) {
  const isRecurring = recurringDays.length > 0;
  const bgColor = isRecurring ? "bg-green-200" : "bg-blue-200";
  const rotation = Math.random() * 6 - 3; // Random rotation between -3 and 3 degrees

  return (
    <div
      className={cn(
        "w-64 h-64 p-4 rounded shadow-md transform transition-transform hover:scale-105",
        bgColor
      )}
      style={{ transform: `rotate(${rotation}deg)` }}
    >
      <h3 className="text-lg font-semibold mb-2">{name}</h3>
      <p className="text-sm mb-1">
        Start: {new Date(startDateTime).toLocaleString()}
      </p>
      <p className="text-sm mb-1">Duration: {duration} minutes</p>
      {isRecurring && (
        <p className="text-sm">Recurring: {recurringDays.join(", ")}</p>
      )}
    </div>
  );
}
