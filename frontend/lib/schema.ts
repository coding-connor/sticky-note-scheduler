import { z } from "zod";

export const weekdayEnum = z.enum([
  "MONDAY",
  "TUESDAY",
  "WEDNESDAY",
  "THURSDAY",
  "FRIDAY",
  "SATURDAY",
  "SUNDAY",
]);

export const eventSchema = z
  .object({
    name: z
      .string()
      .min(1, "Name is required")
      .max(100, "Name must be 100 characters or less")
      .transform((val) => val.trim()),
    start_datetime: z.string().min(1, "Start date and time is required"),
    end_datetime: z.string().min(1, "End date and time is required"),
    timezone: z
      .string()
      .default(() => Intl.DateTimeFormat().resolvedOptions().timeZone),
    days_of_week: z.array(weekdayEnum).optional(),
  })
  .refine(
    (data) => {
      const startDate = new Date(data.start_datetime);
      const endDate = new Date(data.end_datetime);
      return endDate > startDate;
    },
    {
      message: "End time must be after start time",
      path: ["end_datetime"],
    }
  )
  .refine(
    (data) => {
      const endDate = new Date(data.end_datetime);
      const endTimeMinutes = endDate.getHours() * 60 + endDate.getMinutes();
      return endTimeMinutes <= 21 * 60; // 9 PM is 21:00
    },
    {
      message: "Event must end by 9 PM",
      path: ["end_datetime"],
    }
  )
  .refine(
    (data) => {
      const startDate = new Date(data.start_datetime);
      const endDate = new Date(data.end_datetime);
      return startDate.getDate() === endDate.getDate();
    },
    {
      message: "Events cannot cross midnight",
      path: ["end_datetime"],
    }
  );

export type EventFormData = z.infer<typeof eventSchema>;

export interface EventResponse {
  id: string;
  name: string;
  start_datetime: string;
  end_datetime: string;
  timezone: string;
  recurrenceRule?: {
    id: string;
    days_of_week: Array<typeof weekdayEnum._type>;
  };
}
