import React from "react";
import { cn, formatEvent, type Event } from "@/lib/utils";

type EventStickyNoteProps = Event;

export function EventStickyNote(props: EventStickyNoteProps) {
  const formattedEvent = formatEvent(props);
  const isRecurring = (props.recurrence_rule?.days_of_week?.length ?? 0) > 0;
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
      <h3 className="text-lg font-semibold mb-2">{formattedEvent.name}</h3>
      <p className="text-sm mb-1">
        Date: {formattedEvent.localStartDate} at {formattedEvent.localStartTime}
      </p>
      <p className="text-sm mb-1">
        Duration: {formattedEvent.duration} minutes
      </p>
      {isRecurring && formattedEvent.formattedDaysOfWeek && (
        <p className="text-sm">
          Recurring: {formattedEvent.formattedDaysOfWeek}
        </p>
      )}
    </div>
  );
}
