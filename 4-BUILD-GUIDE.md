# 4) بناء النسخة الموقّعة

## أي طريق تختار؟
ملفك صفحة HTML واحدة، وليس مشروع Expo أو React Native. لذلك:

- **الأنسب: Capacitor.** يلفّ ملفك كما هو داخل تطبيق أصلي، ويحمّله من داخل التطبيق (يعمل بلا إنترنت)، ويعطي `localStorage` ثابتاً. الأندرويد يُبنى على أي جهاز، وiOS يحتاج Mac مع Xcode.
- **EAS Build** مصمَّم لمشاريع Expo. يمكن استعماله بتغليف الصفحة في `react-native-webview`، لكن تحميل ملف محلي وحفظ `localStorage` فيه على iOS أقل ثباتاً، وهذا يهدد بيانات المعلمين. استعمله فقط إذا ما عندك Mac وتقبل هذه المخاطرة (اختبر الحفظ جيداً على جهاز حقيقي). البديل بلا Mac: خدمة بناء سحابية تدعم Capacitor مثل Codemagic.

## الحسابات المطلوبة
- Apple Developer Program: رسم سنوي (99$ وقت الإعداد).
- Google Play Console: رسم تسجيل لمرة واحدة (25$). قد تُطلب من الحسابات الشخصية الجديدة فترة اختبار مغلق بعدد مختبرين قبل النشر العام، فتأكد من الشرط الحالي في لوحة Play.

---

## الخطوة 0: تجهيز الملف لنسخة المتجر (إلزامي)
عدّل نسخة منفصلة من `المدارس_الإصدار_7.html` وسمّها `index.html`:
1. حمّل الخطوط والمكتبات إلى مجلد `www/vendor/` وغيّر الروابط إليها: `xlsx.full.min.js` و`mammoth.browser.min.js` و`qrcode.min.js` وخط عربي (مثل Cairo أو Tajawal بصيغة woff2).
2. احذف كتلة eruda وكتلة فحص التحديث (المتغيرات `DEF` و`APVER` ورابط claude.ai). التحديث يتم عبر المتجر.
3. احذف قفل التفعيل وزر واتساب للتفعيل (أو استبدلها بـ In-App Purchase). السبب في ملف 3.
4. عطّل المساعد الصوتي في الإصدار الأول.
5. استبدل `window.open(...).print()` بحفظ/مشاركة ملف عبر إضافتي Share وFilesystem، لأن النوافذ المنبثقة تُحجب في iOS.
6. استبدل `new Notification` بإضافة Local Notifications.
7. اجعل الترويسة الحكومية في القوالب قابلة للتعديل ولا تبدأ بها افتراضياً.

أخبرني وأجهّز لك هذه التعديلات في ملف جاهز.

---

## المسار أ: Capacitor

### 1) إنشاء المشروع
```bash
mkdir al-madaris && cd al-madaris
npm init -y
npm i @capacitor/core @capacitor/android @capacitor/ios \
      @capacitor/local-notifications @capacitor/share @capacitor/filesystem
npm i -D @capacitor/cli @capacitor/assets
npx cap init "المدارس – مساعد المعلم" com.yourname.madaris --web-dir=www
mkdir -p www assets
cp /path/to/index.html www/index.html      # النسخة المعدّلة + مجلد vendor
npx cap add android
npx cap add ios
```
غيّر `com.yourname.madaris` إلى معرّف تملكه. **لا يمكن تغييره بعد النشر.**

### 2) الأيقونات
انسخ الملفات الثلاثة من `icons/` إلى `assets/` بنفس الأسماء: `icon-only.png` و`icon-foreground.png` و`icon-background.png`. ثم:
```bash
npx capacitor-assets generate --iconBackgroundColor '#0a4d41' --splashBackgroundColor '#0a4d41'
```
(أضف `assets/splash.png` بحجم 2732×2732 إذا أردت شاشة بداية مخصصة. بدونها تُولّد الأداة افتراضية.)

### 3) المزامنة
```bash
npx cap sync
```
أعد تنفيذها بعد أي تعديل في `www/`.

---

### أندرويد: ملف AAB موقّع

1. افتح `android/variables.gradle` وتأكد أن `targetSdkVersion = 36` أو أعلى. Google Play يشترط ابتداءً من 31 أغسطس 2026 أن تستهدف التطبيقات الجديدة والتحديثات Android 16 (API 36) أو أعلى.
2. حدّث `android/app/build.gradle`: `versionCode 1` و`versionName "1.0.0"`، وارفع `versionCode` مع كل رفع.
3. أنشئ مفتاح التوقيع (مرة واحدة، واحفظه ونسخته الاحتياطية في مكانين آمنين):
```bash
keytool -genkeypair -v -keystore madaris-upload.jks -alias upload \
  -keyalg RSA -keysize 2048 -validity 10000
```
4. أضف التوقيع في `android/app/build.gradle` (داخل `android {}`):
```gradle
signingConfigs { release {
  storeFile file("../../madaris-upload.jks")
  storePassword System.getenv("KS_PASS")
  keyAlias "upload"
  keyPassword System.getenv("KS_PASS")
}}
buildTypes { release { signingConfig signingConfigs.release
  minifyEnabled false } }
```
5. ابنِ الحزمة:
```bash
cd android && KS_PASS='كلمة_السر' ./gradlew bundleRelease
```
الناتج: `android/app/build/outputs/bundle/release/app-release.aab`
6. في Play Console: أنشئ التطبيق ← فعّل **Play App Signing** عند أول رفع ← ارفع الـ AAB في **Internal testing** أولاً ← اختبر على جهاز حقيقي ← ثم Production.
7. أكمل: Store listing، Data safety، Content rating، Target audience، Privacy policy.

**تحذير:** ضياع مفتاح الرفع يعقّد التحديثات. مع Play App Signing يمكنك طلب إعادة تعيينه من Google، لكن احفظ نسخة.

---

### iOS: Archive وTestFlight

يتطلب Mac وXcode.
```bash
npx cap open ios
```
في Xcode (الهدف App):
1. **Signing & Capabilities:** اختر Team حسابك وفعّل Automatically manage signing. تأكد من Bundle Identifier.
2. **General:** Version `1.0.0` وBuild `1`، وارفع Build مع كل رفع. أزل iPad من Supported Destinations إن لم تجهّز لقطات iPad.
3. **Info:** أضف مفتاح `ITSAppUsesNonExemptEncryption` = `NO` لتجنب سؤال التصدير. أضف وصف الإذن فقط للأذونات التي تستعملها فعلاً.
4. اختر الجهاز **Any iOS Device (arm64)** ← **Product ▸ Archive**.
5. في Organizer: **Distribute App ▸ App Store Connect ▸ Upload**.
6. في App Store Connect: أنشئ سجل التطبيق بنفس Bundle ID، واختر البناء المرفوع، واملأ النصوص والصور (ملف 1) وApp Privacy (ملف 3).
7. اختبر عبر **TestFlight** على iPhone حقيقي، ثم **Submit for Review**.

---

## المسار ب: EAS Build (فقط إذا اخترته)
```bash
npm i -g eas-cli && eas login
npx create-expo-app madaris && cd madaris
npx expo install react-native-webview expo-asset expo-file-system
# ضع index.html في assets/ وحمّله في WebView، ثم:
eas build:configure
eas build -p android --profile production   # ينتج AAB
eas build -p ios --profile production       # يبني في السحابة بلا Mac، وEAS يدير الشهادات
eas submit -p android   # يحتاج Service Account من Play Console (لا ترفعه إلى Git)
eas submit -p ios
```
قبل اعتماده: اختبر أن بيانات `localStorage` تبقى بعد إغلاق التطبيق وإعادة تشغيل الجهاز على iPhone وAndroid.

---

## قائمة ما قبل الإرسال
- [ ] اختبرت على iPhone وAndroid حقيقيين (القائمة السابقة).
- [ ] لا طلبات شبكة خارجية عند فتح التطبيق (راقبها بوضع الطيران).
- [ ] رابط السياسة يعمل ويفتح بلا تسجيل دخول.
- [ ] لقطات الشاشة بالمقاسات الصحيحة وبلا بيانات حقيقية لطلاب.
- [ ] الوصف لا يدّعي أي صلة بوزارة أو جهة رسمية.
- [ ] نموذجا الخصوصية يطابقان النسخة المرفوعة فعلاً.
- [ ] النسخة الاحتياطية والاستعادة تعملان من التطبيق المثبّت.
