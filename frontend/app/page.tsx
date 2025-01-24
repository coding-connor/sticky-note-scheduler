"use client";

import React, { useState, useEffect } from "react";
import { EventSchedulerForm } from "@/components/event-scheduler-form";
import { EventStickyNote } from "@/components/event-sticky-note";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";

interface Event {
  id: string;
  name: string;
  startDateTime: string;
  duration: number;
  recurringDays?: string[];
}

// Dummy function to simulate getting events from a backend
async function getEvents(): Promise<Event[]> {
  // Simulating API call delay
  await new Promise((resolve) => setTimeout(resolve, 1000));

  return [
    {
      id: "1",
      name: "Team Meeting",
      startDateTime: "2024-01-24T10:00",
      duration: 60,
      recurringDays: ["mon", "wed", "fri"],
    },
    {
      id: "2",
      name: "Lunch with Client",
      startDateTime: "2024-01-25T12:30",
      duration: 90,
    },
    {
      id: "3",
      name: "Project Deadline",
      startDateTime: "2024-01-26T17:00",
      duration: 120,
    },
    {
      id: "4",
      name: "Weekly Review",
      startDateTime: "2024-01-27T15:00",
      duration: 45,
      recurringDays: ["fri"],
    },
  ];
}

// Dummy function to simulate creating an event on the backend
async function createEvent(eventData: Omit<Event, "id">): Promise<Event> {
  // Simulating API call delay
  await new Promise((resolve) => setTimeout(resolve, 1000));

  return {
    id: Math.random().toString(36).substr(2, 9),
    ...eventData,
  };
}

export default function Page() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [events, setEvents] = useState<Event[]>([]);

  useEffect(() => {
    getEvents().then(setEvents);
  }, []);

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  const handleEventCreated = async (eventData: Omit<Event, "id">) => {
    const newEvent = await createEvent(eventData);
    setEvents((prevEvents) => [...prevEvents, newEvent]);
    closeModal();
  };

  return (
    <div className="min-h-screen bg-white p-8 flex flex-col items-center">
      <h1 className="text-4xl font-bold mb-8 text-center">
        Sticky Note Scheduler
      </h1>
      <Button
        onClick={openModal}
        className="bg-yellow-200 hover:bg-yellow-300 text-black font-semibold py-2 px-4 rounded shadow mb-8"
      >
        New Event
      </Button>
      <div className="w-full max-w-6xl grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {events.map((event) => (
          <EventStickyNote key={event.id} {...event} />
        ))}
      </div>
      <Modal isOpen={isModalOpen} onClose={closeModal}>
        <EventSchedulerForm onSuccess={handleEventCreated} />
      </Modal>
    </div>
  );
}
