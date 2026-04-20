import { create } from "zustand";

export type QueueState = {
  ticket?: string;
  position: number;
  eta: number;
  status: string;
  setQueue: (data: Partial<QueueState>) => void;
};

export const useQueueStore = create<QueueState>((set) => ({
  position: 0,
  eta: 0,
  status: "idle",
  setQueue: (data) => set((state) => ({ ...state, ...data }))
}));
