import { EventFormData, EventResponse } from "./schema";

const API_BASE_URL = `${
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
}/api`;

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "An error occurred" }));
    throw new ApiError(response.status, error.detail || "An error occurred");
  }
  return response.json();
}

export const api = {
  events: {
    create: async (data: EventFormData): Promise<EventResponse> => {
      const response = await fetch(`${API_BASE_URL}/events`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      return handleResponse<EventResponse>(response);
    },

    getAll: async (): Promise<EventResponse[]> => {
      const response = await fetch(`${API_BASE_URL}/events`);
      return handleResponse<EventResponse[]>(response);
    },
  },
};
