"use server";

import { eventSchema, EventResponse } from "@/lib/schema";
import { api, ApiError } from "@/lib/api";
import { z } from "zod";

interface ActionState {
  success: boolean;
  data: EventResponse | null;
  errors: Record<string, string> | null;
}

interface EventInput {
  name: string;
  start_datetime: string;
  end_datetime: string;
  timezone: string;
  days_of_week?: string[];
}

export async function scheduleEventAction(
  prevState: ActionState,
  data: EventInput
): Promise<ActionState> {
  try {
    const validatedData = eventSchema.parse({
      name: data.name,
      start_datetime: data.start_datetime,
      end_datetime: data.end_datetime,
      timezone: data.timezone,
      days_of_week: data.days_of_week,
    });

    const response = await api.events.create(validatedData);

    return {
      success: true,
      data: response,
      errors: null,
    };
  } catch (error: unknown) {
    if (error instanceof z.ZodError) {
      const fieldErrors: Record<string, string> = {};
      Object.entries(error.flatten().fieldErrors).forEach(([key, value]) => {
        if (value) {
          fieldErrors[key] = value.join(", ");
        }
      });

      fieldErrors["form"] = "Something went wrong. Please try again.";

      return {
        success: false,
        data: null,
        errors: fieldErrors,
      };
    }

    // Handle API errors
    if (error instanceof ApiError) {
      // If it's a 409 Conflict error, we show it as a form-level error
      if (error.status === 409) {
        return {
          success: false,
          data: null,
          errors: {
            form: "This time slot conflicts with another event. Please choose a different time.",
          },
        };
      }

      // For validation errors from the backend (400)
      if (error.status === 400) {
        return {
          success: false,
          data: null,
          errors: {
            form: error.message,
          },
        };
      }
    }

    // For any other errors
    return {
      success: false,
      data: null,
      errors: {
        form:
          error instanceof Error
            ? error.message
            : "An unexpected error occurred. Please try again.",
      },
    };
  }
}

export async function getEvents(): Promise<EventResponse[]> {
  try {
    return await api.events.getAll();
  } catch (error) {
    console.error("Failed to fetch events:", error);
    throw error;
  }
}
