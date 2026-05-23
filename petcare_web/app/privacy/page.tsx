"use client";

import { useLang } from "@/components/LangProvider";

const PRIVACY = {
  ar: {
    title: "سياسة الخصوصية",
    subtitle: "آخر تحديث: أبريل 2026",
    badge: "نظام حماية البيانات الشخصية — PDPL",
    intro:
      "تلتزم منصة VetiCare (myveticare.com) بحماية خصوصيتك وبياناتك الشخصية وفقاً لنظام حماية البيانات الشخصية في المملكة العربية السعودية وجميع الأنظمة واللوائح المعمول بها.",
    s1_title: "١. جمع البيانات واستخدامها",
    s1_body:
      "نجمع البيانات الشخصية اللازمة لتقديم خدمات الرعاية البيطرية فقط، وتشمل: بيانات الهوية (الاسم، البريد الإلكتروني، رقم الهاتف)، السجلات الصحية للحيوان الأليف، سجلات الاستشارات الطبية، وبيانات الوصفات الطبية والأدوية. لا نجمع أي بيانات تتجاوز الغرض المحدد.",
    s2_title: "٢. الأساس القانوني للمعالجة",
    s2_body:
      "نعالج بياناتك استناداً إلى: الضرورة التعاقدية لتقديم الخدمة، الالتزامات القانونية وفق متطلبات هيئة الغذاء والدواء (SFDA)، أو موافقتك الصريحة حيثما اشترطها النظام.",
    s3_title: "٣. الاحتفاظ بالبيانات",
    s3_items: [
      "السجلات الصحية للحيوان الأليف: طوال حياة الحيوان + 7 سنوات",
      "سجلات التدقيق: 5 سنوات كحد أدنى",
      "سجلات الموافقة: إلى أجل غير مسمى (وفق متطلبات التدقيق)",
      "بيانات الجلسة: تُحذف تلقائياً عند انتهاء الصلاحية",
    ],
    s4_title: "٤. حقوقك",
    s4_items: [
      "الحق في الوصول إلى بياناتك الشخصية",
      "الحق في تصحيح البيانات غير الدقيقة",
      "الحق في حذف البيانات (باستثناء السجلات الطبية المطلوبة نظاماً)",
      "الحق في سحب الموافقة في أي وقت",
      "الحق في تقديم شكوى إلى الهيئة السعودية للبيانات والذكاء الاصطناعي (سدايا)",
    ],
    s5_title: "٥. الأمان",
    s5_body:
      "نطبق ضوابط أمنية صارمة تشمل: التشفير أثناء النقل (TLS 1.3) وفي حالة السكون (AES-256)، التحكم في الوصول القائم على الأدوار (RBAC)، المصادقة متعددة العوامل على العمليات الحساسة، وسجل تدقيق غير قابل للتغيير لجميع الإجراءات.",
    s6_title: "٦. الإفصاح لأطراف ثالثة",
    s6_body:
      "لا نبيع بياناتك ولا نؤجرها. قد نشارك البيانات مع مزودي الخدمات المرخصين (Firebase وGoogle Cloud وUnifonic) وفق اتفاقيات معالجة البيانات المبرمة معهم وبالقدر الضروري فقط لتقديم الخدمة.",
    s7_title: "٧. إقامة البيانات",
    s7_body:
      "تُخزَّن البيانات على منصة Google Cloud Platform في منطقة الشرق الأوسط (me-central2). يجري حالياً تأكيد الامتثال الكامل لمتطلبات الإقامة في المملكة العربية السعودية وفق المادة 29 من نظام PDPL.",
    s8_title: "٨. التواصل معنا",
    s8_body: "لممارسة حقوقك أو للاستفسار عن سياسة الخصوصية، يُرجى التواصل معنا:",
    s8_email: "privacy@myveticare.com",
    s8_dpo: "مسؤول حماية البيانات — VetiCare، المملكة العربية السعودية",
    sdaia:
      "يحق لك أيضاً تقديم شكوى مباشرةً إلى الهيئة السعودية للبيانات والذكاء الاصطناعي (سدايا): sdaia.gov.sa",
    footer: "VetiCare / myveticare.com — سياسة الخصوصية v1.0 — أبريل 2026",
    footer2:
      "هذه الوثيقة محكومة بنظام حماية البيانات الشخصية في المملكة العربية السعودية",
  },
  en: {
    title: "Privacy Notice",
    subtitle: "Last updated: April 2026",
    badge: "Personal Data Protection Law — PDPL",
    intro:
      "VetiCare (myveticare.com) is committed to protecting your privacy and personal data in accordance with the Personal Data Protection Law (PDPL) of the Kingdom of Saudi Arabia and all applicable regulations.",
    s1_title: "1. Data Collection and Use",
    s1_body:
      "We collect only the personal data necessary to deliver veterinary care services, including: identity data (name, email, phone), pet health records, veterinary consultation records, and prescription and medication data. We collect no data beyond the specified purpose.",
    s2_title: "2. Legal Basis for Processing",
    s2_body:
      "We process your data on the basis of: contractual necessity to deliver the service, legal obligations under SFDA requirements, or your explicit consent where required by law.",
    s3_title: "3. Data Retention",
    s3_items: [
      "Pet health records: lifetime of pet + 7 years",
      "Audit logs: 5 years minimum",
      "Consent records: indefinitely (regulatory audit requirement)",
      "Session data: automatically purged on expiry",
    ],
    s4_title: "4. Your Rights",
    s4_items: [
      "Right to access your personal data",
      "Right to correct inaccurate data",
      "Right to deletion (excluding clinically and legally mandated records)",
      "Right to withdraw consent at any time",
      "Right to lodge a complaint with SDAIA",
    ],
    s5_title: "5. Security",
    s5_body:
      "We apply rigorous security controls including: encryption in transit (TLS 1.3) and at rest (AES-256), role-based access control (RBAC), multi-factor authentication on sensitive operations, and an immutable audit log of all platform actions.",
    s6_title: "6. Third-Party Disclosure",
    s6_body:
      "We do not sell or rent your data. We may share data with licensed service providers (Firebase, Google Cloud, Unifonic) under signed data processing agreements and only to the extent necessary to deliver the service.",
    s7_title: "7. Data Residency",
    s7_body:
      "Data is stored on Google Cloud Platform in the Middle East region (me-central2). Full compliance with KSA data residency requirements under PDPL Article 29 is currently being confirmed with our infrastructure team.",
    s8_title: "8. Contact Us",
    s8_body:
      "To exercise your rights or for any privacy enquiry, please contact us:",
    s8_email: "privacy@myveticare.com",
    s8_dpo: "Data Protection Officer — VetiCare, Kingdom of Saudi Arabia",
    sdaia:
      "You also have the right to lodge a complaint directly with the Saudi Data and Artificial Intelligence Authority (SDAIA) at sdaia.gov.sa",
    footer: "VetiCare / myveticare.com — Privacy Notice v1.0 — April 2026",
    footer2:
      "This notice is governed by the Personal Data Protection Law (PDPL) of the Kingdom of Saudi Arabia",
  },
};

export default function PrivacyPage() {
  const { lang } = useLang();
  const t = PRIVACY[lang];
  const isAr = lang === "ar";

  return (
    <main
      className="min-h-screen bg-background py-16 px-4"
      dir={isAr ? "rtl" : "ltr"}
    >
      <div className="max-w-3xl mx-auto">

        <div className="mb-10">
          <div className="inline-block bg-secondary/20 text-primary text-sm font-medium px-4 py-1.5 rounded-full mb-4">
            {t.badge}
          </div>
          <h1
            className="text-4xl font-bold text-primary mb-3"
            style={{ fontFamily: "var(--font-heading)" }}
          >
            {t.title}
          </h1>
          <p className="text-text-secondary text-sm">{t.subtitle}</p>
        </div>

        <p className="text-text-primary text-base leading-relaxed mb-10 pb-10 border-b border-secondary/30">
          {t.intro}
        </p>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-primary mb-3" style={{ fontFamily: "var(--font-heading)" }}>
            {t.s1_title}
          </h2>
          <p className="text-text-primary leading-relaxed">{t.s1_body}</p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-primary mb-3" style={{ fontFamily: "var(--font-heading)" }}>
            {t.s2_title}
          </h2>
          <p className="text-text-primary leading-relaxed">{t.s2_body}</p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-primary mb-3" style={{ fontFamily: "var(--font-heading)" }}>
            {t.s3_title}
          </h2>
          <ul className="space-y-2">
            {t.s3_items.map((item) => (
              <li key={item} className="flex gap-3 text-text-primary">
                <span className="text-secondary mt-1 shrink-0">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-primary mb-3" style={{ fontFamily: "var(--font-heading)" }}>
            {t.s4_title}
          </h2>
          <ul className="space-y-2">
            {t.s4_items.map((item) => (
              <li key={item} className="flex gap-3 text-text-primary">
                <span className="text-secondary mt-1 shrink-0">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-primary mb-3" style={{ fontFamily: "var(--font-heading)" }}>
            {t.s5_title}
          </h2>
          <p className="text-text-primary leading-relaxed">{t.s5_body}</p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-primary mb-3" style={{ fontFamily: "var(--font-heading)" }}>
            {t.s6_title}
          </h2>
          <p className="text-text-primary leading-relaxed">{t.s6_body}</p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-primary mb-3" style={{ fontFamily: "var(--font-heading)" }}>
            {t.s7_title}
          </h2>
          <p className="text-text-primary leading-relaxed">{t.s7_body}</p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-primary mb-3" style={{ fontFamily: "var(--font-heading)" }}>
            {t.s8_title}
          </h2>
          <p className="text-text-primary mb-4">{t.s8_body}</p>
          <div className="bg-secondary/10 border border-secondary/30 rounded-xl p-5 space-y-1">
            <a
              href={`mailto:${t.s8_email}`}
              className="block font-medium text-primary hover:underline"
            >
              {t.s8_email}
            </a>
            <p className="text-text-secondary text-sm">{t.s8_dpo}</p>
          </div>
        </section>

        <div className="bg-primary/5 border border-primary/20 rounded-xl p-5 mb-12">
          <p className="text-text-primary text-sm leading-relaxed">{t.sdaia}</p>
        </div>

        <div className="border-t border-secondary/30 pt-8 space-y-1">
          <p className="text-text-secondary text-xs">{t.footer}</p>
          <p className="text-text-secondary text-xs">{t.footer2}</p>
        </div>

      </div>
    </main>
  );
}
