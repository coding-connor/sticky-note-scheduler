"use client";

import * as React from "react";
import { useFormStatus } from "react-dom";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";
import { scheduleEventAction } from "@/lib/actions";
import { Check } from "lucide-react";
import { EventResponse } from "@/lib/schema";

interface FormState {
  success: boolean;
  data: EventResponse | null;
  errors: Record<string, string> | null;
}

const daysOfWeek = [
  { value: "MONDAY", label: "Mon" },
  { value: "TUESDAY", label: "Tue" },
  { value: "WEDNESDAY", label: "Wed" },
  { value: "THURSDAY", label: "Thu" },
  { value: "FRIDAY", label: "Fri" },
  { value: "SATURDAY", label: "Sat" },
  { value: "SUNDAY", label: "Sun" },
];

export function EventSchedulerForm({
  className,
  onSuccess,
}: {
  className?: string;
  onSuccess?: (eventData: EventResponse) => void;
}) {
  const formRef = React.useRef<HTMLFormElement>(null);
  const [state, setState] = React.useState<FormState>({
    success: false,
    data: null,
    errors: null,
  });
  const [clientErrors, setClientErrors] =
    React.useState<Record<string, string>>();
  const [endTime, setEndTime] = React.useState<string>("");
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  const { pending } = useFormStatus();

  const toLocalISOString = (date: Date): string => {
    const offset = date.getTimezoneOffset() * 60000;
    const localDate = new Date(date.getTime() - offset);
    return localDate.toISOString().slice(0, 19);
  };

  const calculateEndTime = (
    startDateTime: string,
    duration: number
  ): string => {
    if (!startDateTime || !duration) return "";
    const startDate = new Date(startDateTime);
    const endDate = new Date(startDate.getTime() + duration * 60000);
    return toLocalISOString(endDate);
  };

  const validateEndTime = (
    startDateTime: string,
    duration: number
  ): { isValid: boolean; error?: string } => {
    if (!startDateTime || !duration) return { isValid: false };

    const startDate = new Date(startDateTime);
    const endDate = new Date(startDateTime);
    endDate.setMinutes(endDate.getMinutes() + duration);

    // Check if event ends on the same day
    if (startDate.getDate() !== endDate.getDate()) {
      return {
        isValid: false,
        error: "Events cannot cross midnight. You value your sleep.",
      };
    }

    return { isValid: true };
  };

  const handleInputChange = () => {
    const formData = new FormData(formRef.current!);
    const startDateTime = formData.get("startDateTime") as string;
    const duration = Number.parseInt(formData.get("duration") as string, 10);

    if (startDateTime && duration) {
      const newEndTime = calculateEndTime(startDateTime, duration);
      setEndTime(newEndTime);

      const validation = validateEndTime(startDateTime, duration);
      if (!validation.isValid) {
        setClientErrors({
          duration: validation.error!,
        });
      } else {
        setClientErrors(undefined);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setClientErrors(undefined);

    const formData = new FormData(e.currentTarget);
    const startDateTime = formData.get("startDateTime") as string;
    const duration = Number.parseInt(formData.get("duration") as string, 10);
    const selectedDays = formData.getAll("daysOfWeek") as string[];

    const validation = validateEndTime(startDateTime, duration);
    if (!validation.isValid) {
      setClientErrors({
        duration: validation.error!,
      });
      return;
    }

    // Convert to UTC for backend
    const startDate = new Date(startDateTime);
    const endDate = new Date(startDate.getTime() + duration * 60000);

    // Format data for backend
    const data = {
      name: (formData.get("name") as string).trim(),
      start_datetime: startDate.toISOString(),
      end_datetime: endDate.toISOString(),
      timezone,
      days_of_week: selectedDays.length > 0 ? selectedDays : undefined,
    };

    const result = await scheduleEventAction(state, data);
    setState(result);

    if (result.success && result.data && onSuccess) {
      onSuccess(result.data);
      formRef.current?.reset();
      setEndTime("");
    }
  };

  // Combine server and client errors
  const errors = {
    ...state.errors,
    ...clientErrors,
  };

  return (
    <div
      className={cn(
        "w-[400px] p-6 bg-yellow-100 relative",
        "before:absolute before:inset-0 before:bg-yellow-50 before:opacity-50 before:background-noise before:pointer-events-none",
        "shadow-md transform rotate-[-1deg]",
        className
      )}
    >
      <div className="relative z-20">
        <form ref={formRef} onSubmit={handleSubmit} className="space-y-6">
          <h2 className="text-2xl font-semibold text-black/80 mb-4">
            Schedule Event
          </h2>
          {state.success ? (
            <p className="text-green-600 flex items-center gap-2 text-sm">
              <Check className="size-4" />
              Event scheduled successfully!
            </p>
          ) : null}
          {errors?.form ? (
            <p className="text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2 text-sm">
              {errors.form}
            </p>
          ) : null}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label
                htmlFor="name"
                className={cn(
                  "text-black/70",
                  errors?.name && "text-destructive"
                )}
              >
                Event Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="name"
                name="name"
                placeholder="Enter event name"
                maxLength={100}
                required
                className={cn(
                  "bg-transparent border-black/20 focus-visible:ring-black/30 focus-visible:border-black/30",
                  "placeholder:text-black/40",
                  errors?.name &&
                    "border-destructive focus-visible:ring-destructive"
                )}
                disabled={pending}
                aria-invalid={!!errors?.name}
              />
              {errors?.name && (
                <p className="text-destructive text-sm">{errors.name}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label
                htmlFor="startDateTime"
                className={cn(
                  "text-black/70",
                  errors?.startDateTime && "text-destructive"
                )}
              >
                Start Date & Time <span className="text-red-500">*</span>
              </Label>
              <Input
                id="startDateTime"
                name="startDateTime"
                type="datetime-local"
                required
                onChange={handleInputChange}
                className={cn(
                  "bg-transparent border-black/20 focus-visible:ring-black/30 focus-visible:border-black/30",
                  errors?.startDateTime &&
                    "border-destructive focus-visible:ring-destructive"
                )}
                disabled={pending}
                aria-invalid={!!errors?.startDateTime}
              />
              {errors?.startDateTime && (
                <p className="text-destructive text-sm">
                  {errors.startDateTime}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label
                htmlFor="duration"
                className={cn(
                  "text-black/70",
                  errors?.duration && "text-destructive"
                )}
              >
                Duration (minutes) <span className="text-red-500">*</span>
              </Label>
              <Input
                id="duration"
                name="duration"
                type="number"
                min="1"
                required
                onChange={handleInputChange}
                placeholder="Enter duration in minutes"
                className={cn(
                  "bg-transparent border-black/20 focus-visible:ring-black/30 focus-visible:border-black/30",
                  "placeholder:text-black/40",
                  errors?.duration &&
                    "border-destructive focus-visible:ring-destructive"
                )}
                disabled={pending}
                aria-invalid={!!errors?.duration}
              />
              {errors?.duration && (
                <p className="text-destructive text-sm">{errors.duration}</p>
              )}
              {endTime && (
                <p className="text-xs text-black/70">
                  End time:{" "}
                  {new Date(endTime).toLocaleString(undefined, {
                    hour: "numeric",
                    minute: "numeric",
                    hour12: true,
                    timeZone: timezone,
                  })}
                </p>
              )}
              <p className="text-xs text-black/50">
                Note: Sleep is good. Events must end before midnight.
              </p>
            </div>

            <div className="space-y-2">
              <Label
                className={cn(
                  "text-black/70",
                  errors?.daysOfWeek && "text-destructive"
                )}
              >
                Recurring Days (Optional)
              </Label>
              <div className="flex flex-wrap gap-2">
                {daysOfWeek.map((day) => (
                  <div key={day.value} className="flex items-center">
                    <Checkbox
                      id={`day-${day.value}`}
                      name="daysOfWeek"
                      value={day.value}
                      disabled={pending}
                    />
                    <label
                      htmlFor={`day-${day.value}`}
                      className="ml-2 text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      {day.label}
                    </label>
                  </div>
                ))}
              </div>
              {errors?.daysOfWeek && (
                <p className="text-destructive text-sm">{errors.daysOfWeek}</p>
              )}
            </div>
          </div>

          <Button
            type="submit"
            disabled={pending || !!clientErrors}
            className="w-full bg-yellow-200 hover:bg-yellow-300 text-black/70 hover:text-black font-semibold"
          >
            {pending ? "Scheduling..." : "Schedule Event"}
          </Button>
        </form>
      </div>
    </div>
  );
}
