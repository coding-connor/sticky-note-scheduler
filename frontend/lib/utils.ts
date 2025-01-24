import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export interface Event {
  name: string;
  start_datetime: string;
  end_datetime: string;
  timezone: string;
  id: string;
  recurrence_rule?: {
    days_of_week: string[];
    id: string;
  };
}

export interface FormattedEvent extends Event {
  duration: number;
  localStartTime: string;
  localEndTime: string;
  localStartDate: string;
  formattedDaysOfWeek?: string;
}

export function formatEvent(event: Event): FormattedEvent {
  // Parse dates as UTC
  const startUtc = new Date(event.start_datetime + "Z"); // Ensure UTC
  const endUtc = new Date(event.end_datetime + "Z"); // Ensure UTC

  // Calculate duration in minutes (using UTC times)
  const duration = Math.round(
    (endUtc.getTime() - startUtc.getTime()) / (1000 * 60)
  );

  // Format times in event's timezone (12-hour format)
  const timeFormatter = new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
    timeZone: event.timezone,
  });

  const dateFormatter = new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: event.timezone,
  });

  // Format the dates in the event's timezone
  const localStartTime = timeFormatter.format(startUtc);
  const localEndTime = timeFormatter.format(endUtc);
  const localStartDate = dateFormatter.format(startUtc);

  // Format days of week if present
  const formattedDaysOfWeek = event.recurrence_rule?.days_of_week
    .map((day) => day.charAt(0) + day.slice(1).toLowerCase())
    .join(", ");

  return {
    ...event,
    start_datetime: event.start_datetime, // Keep original UTC time
    end_datetime: event.end_datetime, // Keep original UTC time
    duration,
    localStartTime,
    localEndTime,
    localStartDate,
    formattedDaysOfWeek,
  };
}
