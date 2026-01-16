# 🔐 معلومات الـ Webhook - Lion Bot

## 📍 Webhook URL

```
https://lionbot-backend-426202982674.me-west1.run.app/webhook
```

**أو يمكنك استخدام:**
```
https://lionbot-backend-na2x2bszha-zf.a.run.app/webhook
```

---

## 🔑 Verification Token

```
lion_verify_2024
```

**⚠️ هذا الـ Token يجب إدخاله في Meta Developer Console**

---

## 📲 خطوات الإعداد في Meta Developer Console

### 1️⃣ الدخول إلى WhatsApp Configuration
1. اذهب إلى: https://developers.facebook.com/
2. سجّل دخول واختر تطبيقك
3. من القائمة الجانبية: **WhatsApp** → **Configuration**

---

### 2️⃣ إعداد الـ Webhook

في قسم **"Webhook"**:

**Callback URL:**
```
https://lionbot-backend-426202982674.me-west1.run.app/webhook
```

**Verify Token:**
```
lion_verify_2024
```

اضغط **"Verify and Save"** ✅

---

### 3️⃣ الاشتراك في Webhook Fields

بعد حفظ الـ Webhook، في قسم **"Webhook fields"**:
- اضغط **"Manage"**
- فعّل ✅ **messages**
- فعّل ✅ **message_status** (اختياري)
- اضغط **Subscribe**

---

## 📋 معلومات إضافية من Cloud Run

### WhatsApp Business Account ID
```
1064117252451978
```

### WhatsApp Phone Number ID
```
954073471112895
```

### WhatsApp Access Token
```
EAAMWnOKUc2kBQHKzN2XupzA5DqmU35ivgFGdIsBKintrnrKZBokTNmDGXXBdbXkFkdq9ZBarsKZCV7ZAILCIV0w1vI36ZB0qd6ynIZBfvpCUj8Dl4FZCdaYlg9ykX8kxMGPOC7jNihQWThE430zCYFR0ZA0SzMtNSiajJ9PA86LTZBR1HzViiwENOqgVlNW05FhoNyQZDZD
```

> [!CAUTION]
> هذا الـ Token حساس جداً! لا تشاركه مع أي شخص ولا ترفعه على GitHub.

### OpenAI Model المستخدم
```
gpt-4-turbo-preview
```

### Cloud Run URLs
- **Primary URL:** https://lionbot-backend-426202982674.me-west1.run.app
- **Alternative URL:** https://lionbot-backend-na2x2bszha-zf.a.run.app
- **Region:** me-west1 (Middle East)

---

## 🧪 اختبار الـ Webhook

### اختبار التحقق (Verification):
```bash
curl "https://lionbot-backend-426202982674.me-west1.run.app/webhook?hub.mode=subscribe&hub.verify_token=lion_verify_2024&hub.challenge=test123"
```

**النتيجة المتوقعة:** `test123`

---

### اختبار الصحة (Health Check):
```bash
curl https://lionbot-backend-426202982674.me-west1.run.app/health
```

**النتيجة المتوقعة:** `{"status":"healthy"}`

---

## 📞 معلومات WhatsApp API

### الحصول على Phone Number ID
1. اذهب إلى: **WhatsApp** → **Getting Started**
2. ستجد **Phone Number ID** تحت قسم "Test number"
3. انسخه وأضفه كمتغير بيئة في Cloud Run:
   ```bash
   gcloud run services update lionbot-backend \
     --region=me-west1 \
     --set-env-vars="WHATSAPP_PHONE_NUMBER_ID=YOUR_PHONE_NUMBER_ID"
   ```

---

## ⚠️ ملاحظات مهمة

### 🔴 OPENAI_API_KEY
تحذير: الـ API Key الموجود حالياً في Cloud Run قد يكون منتهي أو محدود.

**للتحديث:**
```bash
gcloud run services update lionbot-backend \
  --region=me-west1 \
  --set-env-vars="OPENAI_API_KEY=sk-YOUR_NEW_KEY"
```

---

### 🔴 Database Configuration
حالياً الـ Database مضبوط على `localhost` وهذا **لن يعمل في Cloud Run**.

**خيارات للحل:**
1. استخدام **Cloud SQL** (موصى به)
2. استخدام **Neon** أو **Supabase** (مجاني للبداية)
3. تعديل الإعدادات لاستخدام DATABASE_URL:
   ```bash
   gcloud run services update lionbot-backend \
     --region=me-west1 \
     --set-env-vars="DATABASE_URL=postgresql+asyncpg://USER:PASS@HOST/DB"
   ```

---

### 🔴 Redis Configuration
حالياً Redis مضبوط على `localhost` وهذا **لن يعمل في Cloud Run**.

**خيارات للحل:**
1. استخدام **Upstash Redis** (مجاني للبداية)
2. استخدام **Redis Cloud**
3. استخدام **Cloud Memorystore**

---

## ✅ Checklist

- [ ] **Webhook URL** مضاف في Meta Console
- [ ] **Verify Token** مضاف في Meta Console
- [ ] **Webhook Fields** مفعّلة (messages)
- [x] **Phone Number ID** مضاف ✅ `954073471112895`
- [ ] **Database** مضبوط صح (⚠️ حالياً localhost)
- [ ] **Redis** مضبوط صح (⚠️ حالياً localhost)
- [ ] اختبار الـ webhook بـ curl ✅
- [ ] إرسال رسالة تجريبية من WhatsApp

---

## 🔧 أوامر سريعة

### عرض Environment Variables الحالية:
```bash
gcloud run services describe lionbot-backend --region=me-west1 --format="value(spec.template.spec.containers[0].env)"
```

### عرض Logs:
```bash
gcloud run logs tail lionbot-backend --region=me-west1
```

### تحديث متغير بيئة:
```bash
gcloud run services update lionbot-backend \
  --region=me-west1 \
  --set-env-vars="VARIABLE_NAME=value"
```

---

**🦁 الآن جاهز لإعداد الـ Webhook في Meta!**

**التاريخ:** 2025-12-18  
**Cloud Run Region:** me-west1 (Middle East - Tel Aviv)
