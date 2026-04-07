import type { OwnerDashboard } from "@/types/owner";
import {
  PetProfileCard,
  AppointmentCard,
  HealthTimeline,
  VaccinationSummary,
  QuickActions,
} from "@/components/owner";

// ---------------------------------------------------------------------------
// Placeholder data — no real backend calls. PH-UI-2 read-only shell.
// ---------------------------------------------------------------------------
const MOCK: OwnerDashboard = {
  owner: {
    id: "owner-001",
    fullName: "سارة الراشدي",
    email: "sara@example.com",
    phone: "+966 50 000 0001",
    consentGiven: true,
    emergencyContact: "+966 50 000 0002",
  },
  pets: [
    {
      id: "pet-001",
      name: "لونا",
      species: "cat",
      breed: "المو العربي",
      dateOfBirth: "2021-04-15",
      weightKg: 4.2,
      microchipId: "982000123456789",
      photoUrl: null,
    },
  ],
  appointments: [
    {
      id: "appt-001",
      petId: "pet-001",
      vetName: "د. خالد العتيبي",
      clinicName: "عيادة الرياض البيطرية",
      dateTime: "2026-03-20T10:00:00Z",
      reason: "فحص العافية السنوي",
      status: "scheduled",
      notes: null,
    },
    {
      id: "appt-002",
      petId: "pet-001",
      vetName: "د. خالد العتيبي",
      clinicName: "عيادة الرياض البيطرية",
      dateTime: "2025-09-10T09:30:00Z",
      reason: "جرعة تطعيم معززة",
      status: "completed",
      notes: "جميع العلامات الحيوية طبيعية. الوزن مستقر.",
    },
  ],
  timeline: [
    {
      id: "evt-001",
      petId: "pet-001",
      date: "2025-09-10",
      type: "vaccination",
      title: "جرعة معززة للسعار + FVRCP",
      description: "تم تطبيق الجرعة المعززة السنوية دون مضاعفات.",
      vetName: "د. خالد العتيبي",
    },
    {
      id: "evt-002",
      petId: "pet-001",
      date: "2025-04-01",
      type: "checkup",
      title: "فحص العافية السنوي",
      description: "الوزن 4.1 كجم. الفراء والأسنان في حالة جيدة.",
      vetName: "د. خالد العتيبي",
    },
    {
      id: "evt-003",
      petId: "pet-001",
      date: "2024-11-15",
      type: "prescription",
      title: "علاج مضاد للطفيليات",
      description: "تم وصف علاج شهري للوقاية من البراغيث والقراد.",
      vetName: null,
    },
  ],
  vaccinations: [
    {
      id: "vac-001",
      petId: "pet-001",
      name: "Rabies",
      administeredDate: "2025-09-10",
      nextDueDate: "2026-09-10",
      status: "current",
      batchNumber: "RB-20250910",
      vetName: "د. خالد العتيبي",
    },
    {
      id: "vac-002",
      petId: "pet-001",
      name: "FVRCP",
      administeredDate: "2025-09-10",
      nextDueDate: "2026-03-30",
      status: "due_soon",
      batchNumber: "FV-20250910",
      vetName: "د. خالد العتيبي",
    },
    {
      id: "vac-003",
      petId: "pet-001",
      name: "FeLV",
      administeredDate: "2024-09-01",
      nextDueDate: "2025-09-01",
      status: "overdue",
      batchNumber: null,
      vetName: null,
    },
  ],
};

export default function OwnerPage() {
  const { owner, pets, appointments, timeline, vaccinations } = MOCK;
  const pet = pets[0];

  return (
    <div className="space-y-8 max-w-3xl">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-gray-900">بوابة المالك</h1>
        <p className="mt-1 text-sm text-gray-500">
          قراءة فقط · بيانات تجريبية · PH-UI-2
        </p>
      </div>

      {/* Quick Actions */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          الإجراءات السريعة
        </h2>
        <QuickActions />
      </section>

      {/* Pet Profile */}
      {pet && (
        <section className="space-y-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            ملف الحيوان الأليف
          </h2>
          <PetProfileCard pet={pet} owner={owner} />
        </section>
      )}

      {/* Upcoming Appointments */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          المواعيد
        </h2>
        {appointments.length === 0 ? (
          <p className="text-sm text-gray-400 italic">لا توجد مواعيد.</p>
        ) : (
          <div className="space-y-2">
            {appointments.map((appt) => (
              <AppointmentCard key={appt.id} appointment={appt} />
            ))}
          </div>
        )}
      </section>

      {/* Vaccinations */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          التطعيمات
        </h2>
        <VaccinationSummary
          vaccinations={vaccinations.filter((v) => v.petId === pet?.id)}
        />
      </section>

      {/* Health Timeline */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          السجل الصحي
        </h2>
        <HealthTimeline
          events={timeline.filter((e) => e.petId === pet?.id)}
        />
      </section>
    </div>
  );
}
