"use client";

import * as React from "react";
import { useFormStatus } from "react-dom";
import { useActionState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";
import { scheduleEventAction } from "@/lib/actions";
import { Check } from "lucide-react";

const daysOfWeek = [
  { value: "mon", label: "Mon" },
  { value: "tue", label: "Tue" },
  { value: "wed", label: "Wed" },
  { value: "thu", label: "Thu" },
  { value: "fri", label: "Fri" },
  { value: "sat", label: "Sat" },
  { value: "sun", label: "Sun" },
];

export function EventSchedulerForm({
  className,
  onSuccess,
}: {
  className?: string;
  onSuccess?: (eventData: {
    name: string;
    startDateTime: string;
    duration: number;
    recurringDays: string[];
  }) => void;
}) {
  const [state, formAction] = useActionState(scheduleEventAction, {
    success: false,
    errors: null,
  });

  const { pending } = useFormStatus();

  const handleSubmit = async (formData: FormData) => {
    const result = await scheduleEventAction(state, formData);
    if (result.success && onSuccess) {
      onSuccess({
        name: formData.get("name") as string,
        startDateTime: formData.get("startDateTime") as string,
        duration: Number.parseInt(formData.get("duration") as string, 10),
        recurringDays: formData.getAll("recurringDays") as string[],
      });
    }
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
        <form action={handleSubmit} className="space-y-6">
          <h2 className="text-2xl font-semibold text-black/80 mb-4">
            Schedule Event
          </h2>
          {state.success ? (
            <p className="text-green-600 flex items-center gap-2 text-sm">
              <Check className="size-4" />
              Event scheduled successfully!
            </p>
          ) : null}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label
                htmlFor="name"
                className={cn(
                  "text-black/70",
                  state.errors?.name && "text-destructive"
                )}
              >
                Event Name
              </Label>
              <Input
                id="name"
                name="name"
                placeholder="Enter event name"
                maxLength={100}
                className={cn(
                  "bg-transparent border-black/20 focus-visible:ring-black/30 focus-visible:border-black/30",
                  "placeholder:text-black/40",
                  state.errors?.name &&
                    "border-destructive focus-visible:ring-destructive"
                )}
                disabled={pending}
                aria-invalid={!!state.errors?.name}
              />
              {state.errors?.name && (
                <p className="text-destructive text-sm">{state.errors.name}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label
                htmlFor="startDateTime"
                className={cn(
                  "text-black/70",
                  state.errors?.startDateTime && "text-destructive"
                )}
              >
                Start Date & Time
              </Label>
              <Input
                id="startDateTime"
                name="startDateTime"
                type="datetime-local"
                className={cn(
                  "bg-transparent border-black/20 focus-visible:ring-black/30 focus-visible:border-black/30",
                  state.errors?.startDateTime &&
                    "border-destructive focus-visible:ring-destructive"
                )}
                disabled={pending}
                aria-invalid={!!state.errors?.startDateTime}
              />
              {state.errors?.startDateTime && (
                <p className="text-destructive text-sm">
                  {state.errors.startDateTime}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label
                htmlFor="duration"
                className={cn(
                  "text-black/70",
                  state.errors?.duration && "text-destructive"
                )}
              >
                Duration (minutes)
              </Label>
              <Input
                id="duration"
                name="duration"
                type="number"
                min="1"
                placeholder="Enter duration in minutes"
                className={cn(
                  "bg-transparent border-black/20 focus-visible:ring-black/30 focus-visible:border-black/30",
                  "placeholder:text-black/40",
                  state.errors?.duration &&
                    "border-destructive focus-visible:ring-destructive"
                )}
                disabled={pending}
                aria-invalid={!!state.errors?.duration}
              />
              {state.errors?.duration && (
                <p className="text-destructive text-sm">
                  {state.errors.duration}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label
                className={cn(
                  "text-black/70",
                  state.errors?.recurringDays && "text-destructive"
                )}
              >
                Recurring Days
              </Label>
              <div className="flex flex-wrap gap-2">
                {daysOfWeek.map((day) => (
                  <div key={day.value} className="flex items-center">
                    <Checkbox
                      id={`day-${day.value}`}
                      name="recurringDays"
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
              {state.errors?.recurringDays && (
                <p className="text-destructive text-sm">
                  {state.errors.recurringDays}
                </p>
              )}
            </div>
          </div>

          <Button
            type="submit"
            disabled={pending}
            className="w-full bg-black/70 hover:bg-black text-white"
          >
            {pending ? "Scheduling..." : "Schedule Event"}
          </Button>
        </form>
      </div>
    </div>
  );
}
