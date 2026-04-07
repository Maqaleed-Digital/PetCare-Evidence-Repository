import type { Pet, Owner } from "@/types/owner";

interface PetProfileCardProps {
  pet: Pet;
  owner: Owner;
}

const SPECIES_LABEL: Record<Pet["species"], string> = {
  dog: "كلب",
  cat: "قطة",
  bird: "طائر",
  rabbit: "أرنب",
  other: "أخرى",
};

function ageFromDob(dob: string): string {
  const born = new Date(dob);
  const now = new Date();
  const years = now.getFullYear() - born.getFullYear();
  const months = now.getMonth() - born.getMonth();
  const totalMonths = years * 12 + months;
  if (totalMonths < 12) return `${totalMonths}mo`;
  return `${Math.floor(totalMonths / 12)}y ${totalMonths % 12}mo`;
}

export function PetProfileCard({ pet, owner }: PetProfileCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-3">
      <div className="flex items-center gap-4">
        <div className="h-14 w-14 rounded-full bg-blue-100 flex items-center justify-center text-2xl select-none">
          {pet.species === "dog"
            ? "🐕"
            : pet.species === "cat"
            ? "🐈"
            : pet.species === "bird"
            ? "🐦"
            : pet.species === "rabbit"
            ? "🐇"
            : "🐾"}
        </div>
        <div>
          <h3 className="text-base font-semibold text-gray-900">{pet.name}</h3>
          <p className="text-sm text-gray-500">
            {SPECIES_LABEL[pet.species]} · {pet.breed}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-y-1 gap-x-4 text-sm">
        <span className="text-gray-500">العمر</span>
        <span className="text-gray-900 font-medium">{ageFromDob(pet.dateOfBirth)}</span>

        <span className="text-gray-500">الوزن</span>
        <span className="text-gray-900 font-medium">{pet.weightKg} كجم</span>

        <span className="text-gray-500">الرقم الإلكتروني</span>
        <span className="text-gray-900 font-medium truncate">
          {pet.microchipId ?? "غير مسجل"}
        </span>

        <span className="text-gray-500">المالك</span>
        <span className="text-gray-900 font-medium">{owner.fullName}</span>

        <span className="text-gray-500">الموافقة</span>
        <span
          className={`font-medium ${
            owner.consentGiven ? "text-green-700" : "text-red-600"
          }`}
        >
          {owner.consentGiven ? "ممنوحة" : "غير ممنوحة"}
        </span>
      </div>
    </div>
  );
}
