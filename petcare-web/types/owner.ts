export interface Pet {
  id: string;
  name: string;
  species: "dog" | "cat" | "bird" | "rabbit" | "other";
  breed: string;
  dateOfBirth: string; // ISO date
  weightKg: number;
  microchipId: string | null;
  photoUrl: string | null;
}

export interface Owner {
  id: string;
  fullName: string;
  email: string;
  phone: string;
  consentGiven: boolean;
  emergencyContact: string | null;
}

export type AppointmentStatus =
  | "scheduled"
  | "completed"
  | "cancelled"
  | "pending";

export interface Appointment {
  id: string;
  petId: string;
  vetName: string;
  clinicName: string;
  dateTime: string; // ISO datetime
  reason: string;
  status: AppointmentStatus;
  notes: string | null;
}

export type TimelineEventType =
  | "checkup"
  | "vaccination"
  | "surgery"
  | "diagnosis"
  | "prescription"
  | "observation";

export interface HealthTimelineEvent {
  id: string;
  petId: string;
  date: string; // ISO date
  type: TimelineEventType;
  title: string;
  description: string;
  vetName: string | null;
}

export type VaccinationStatus = "current" | "due_soon" | "overdue";

export interface Vaccination {
  id: string;
  petId: string;
  name: string;
  administeredDate: string; // ISO date
  nextDueDate: string; // ISO date
  status: VaccinationStatus;
  batchNumber: string | null;
  vetName: string | null;
}

export interface OwnerDashboard {
  owner: Owner;
  pets: Pet[];
  appointments: Appointment[];
  timeline: HealthTimelineEvent[];
  vaccinations: Vaccination[];
}
