export default function OnboardingPage() {
  return (
    <main className="stack">
      <div className="card">
        <div className="kicker">برنامج التجريب</div>
        <div className="title-lg">تسجيل العيادات</div>
        <p className="subtitle" style={{ maxWidth: 600 }}>
          VetiCare في مرحلة تجريب محكوم. يتم تسجيل العيادات بشكل فردي مع التحقق
          الكامل من الحوكمة قبل منح أي صلاحية وصول إلى النظام.
        </p>
      </div>

      <div className="grid cols2">
        <div className="card stack card-sm">
          <div className="badge badge-blue" style={{ alignSelf: 'flex-start' }}>الخطوة 1</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>التحقق من الأهلية</div>
            <p className="subtitle">
              يُشترط توفر سجل تجاري ساري، وأطباء بيطريون مرخّصون، وموقع عيادة
              موثّق قبل بدء عملية التسجيل.
            </p>
          </div>
        </div>

        <div className="card stack card-sm">
          <div className="badge badge-blue" style={{ alignSelf: 'flex-start' }}>الخطوة 2</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>التحقق من الهوية</div>
            <p className="subtitle">
              يتم التحقق من هوية كل طبيب بيطري عبر سجل التراخيص الوطني.
              لا يُمنح الوصول إلى النظام حتى اكتمال التحقق.
            </p>
          </div>
        </div>

        <div className="card stack card-sm">
          <div className="badge badge-blue" style={{ alignSelf: 'flex-start' }}>الخطوة 3</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>إعداد الحساب</div>
            <p className="subtitle">
              تُسنَد الأدوار عبر بوابة الإدارة. جميع أحداث الإعداد مسجّلة في
              سجل المراجعة ومرتبطة بمعرّف ارتباط.
            </p>
          </div>
        </div>

        <div className="card stack card-sm">
          <div className="badge badge-green" style={{ alignSelf: 'flex-start' }}>الخطوة 4</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>تفعيل التجريب</div>
            <p className="subtitle">
              بعد التفعيل، تصبح لوحة تحكم العيادة وقائمة الاستشارات وسير عمل
              الوصفات متاحةً تحت إطار العمل المحكوم.
            </p>
          </div>
        </div>
      </div>

      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 24, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 240 }}>
          <div className="title" style={{ fontSize: 16 }}>هل أنت مستعد للانضمام للتجريب؟</div>
          <p className="subtitle">تواصل مع فريق التسجيل مع بيانات تسجيل عيادتك.</p>
        </div>
        <a className="button" href="mailto:onboarding@myveticare.com">التقدم للوصول التجريبي</a>
      </div>
    </main>
  )
}
