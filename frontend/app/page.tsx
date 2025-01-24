"use client";

import React, { useState, useEffect } from "react";
import { EventSchedulerForm } from "@/components/event-scheduler-form";
import { EventStickyNote } from "@/components/event-sticky-note";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { getEvents } from "@/lib/actions";
import { EventResponse } from "@/lib/schema";
import { Plus } from "lucide-react";

export default function Page() {
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const fetchedEvents = await getEvents();
      setEvents(fetchedEvents);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load events");
    } finally {
      setIsLoading(false);
    }
  };

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  const handleEventCreated = (event: EventResponse) => {
    setEvents((prev) => [...prev, event]);
    closeModal();
  };

  return (
    <main className="container mx-auto p-4">
      <div className="flex flex-col items-center mb-8">
        <h1 className="text-4xl font-bold mb-4 text-center">
          Sticky Note Scheduler
        </h1>
        <Button
          onClick={openModal}
          className="bg-yellow-200 hover:bg-yellow-300 text-black/70 hover:text-black font-semibold shadow-sm"
        >
          <Plus className="size-4 mr-2" />
          New Event
        </Button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center items-center min-h-[200px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 justify-items-center max-w-[1600px] mx-auto">
          {events.map((event) => (
            <EventStickyNote key={event.id} {...event} />
          ))}
          {events.length === 0 && !error && (
            <div className="col-span-full text-center text-gray-500 py-8">
              No events scheduled yet. Click &quot;New Event&quot; to create
              one!
            </div>
          )}
        </div>
      )}

      <Modal isOpen={isModalOpen} onClose={closeModal}>
        <EventSchedulerForm
          onSuccess={handleEventCreated}
          className="w-full max-w-lg mx-auto"
        />
      </Modal>
    </main>
  );
}
