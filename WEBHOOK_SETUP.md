# 🔗 WhatsApp Webhook Configuration - Lion Delivery BOT

## 📋 معلومات الـ Webhook

### 1️⃣ Webhook URL (حسب طريقة النشر)

#### إذا نشرت على **Google Cloud Run**:
```
https://YOUR_CLOUD_RUN_URL/webhook
```

#### إذا نشرت على **VM Instance** مع Domain:
```
https://api.yourdomain.com/webhook
```

#### إذا نشرت على **VM Instance** بدون Domain:
```
http://YOUR_VM_EXTERNAL_IP:8080/webhook
```

---

### 2️⃣ Verification Token

يمكنك استخدام أي قيمة ترغب بها، لكن يجب أن تكون **نفس القيمة** في:
- Meta Developer Console (WhatsApp Configuration)
- ملف `.env` الخاص بالـ Backend

**مثال على Verification Token:**
```
LionBot2024SecureToken
```

أو يمكنك توليد واحد عشوائي:
```bash
# على macOS/Linux
openssl rand -hex 32
```

---

## 🛠️ خطوات إعداد الـ Webhook في Meta Developer Console

### الخطوة 1: الدخول إلى Meta for Developers
1. اذهب إلى: https://developers.facebook.com/
2. سجّل دخول بحسابك
3. اختر تطبيقك (أو أنشئ تطبيق جديد)

---

### الخطوة 2: إعداد WhatsApp Business API
1. من القائمة الجانبية، اختر **"WhatsApp"** → **"Getting Started"**
2. احصل على:
   - **Phone Number ID** (معرّف رقم الهاتف)
   - **WhatsApp Business Account ID** (معرّف الحساب)
   - **API Token** (مؤقت - ستحتاج لإنشاء Permanent Token لاحقاً)

---

### الخطوة 3: إعداد Webhook
1. اذهب إلى **"WhatsApp"** → **"Configuration"**
2. في قسم **"Webhook"**، اضغط على **"Edit"**
3. املأ الحقول التالية:

#### Callback URL:
```
https://YOUR_CLOUD_RUN_URL/webhook
```
**أو استخدم رابط السيرفر الخاص بك**

#### Verify Token:
```
LionBot2024SecureToken
```
**⚠️ يجب أن تكون نفس القيمة في ملف `.env`**

4. اضغط على **"Verify and Save"**

---

### الخطوة 4: الاشتراك في Webhook Fields
1. بعد حفظ الـ Webhook، اذهب إلى قسم **"Webhook fields"**
2. اضغط على **"Manage"**
3. فعّل الحقول التالية:
   - ✅ **messages** (إلزامي - لاستقبال الرسائل)
   - ✅ **message_status** (اختياري - لمعرفة حالة الرسائل المرسلة)

4. اضغط **Subscribe**

---

## 📄 إعداد ملف `.env`

أضف هذه المتغيرات في ملف `backend/.env`:

```env
# ===========================================
# WhatsApp Cloud API Configuration
# ===========================================
WHATSAPP_API_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=LionBot2024SecureToken
WHATSAPP_BUSINESS_ACCOUNT_ID=987654321098765

# ===========================================
# OpenAI API (للرد الذكي على العملاء)
# ===========================================
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ===========================================
# Database
# ===========================================
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=lionbot

# ===========================================
# Redis (للـ Cart والـ Session)
# ===========================================
REDIS_HOST=redis
REDIS_PORT=6379

# ===========================================
# Security
# ===========================================
SECRET_KEY=your_very_secure_random_string_here_min_32_chars
```

---

## 🧪 اختبار الـ Webhook

### 1. اختبار محلي باستخدام ngrok (اختياري للتطوير)

```bash
# تثبيت ngrok
brew install ngrok

# تشغيل السيرفر المحلي
cd backend
docker-compose up

# في terminal جديد
ngrok http 8080
```

استخدم الرابط الذي يعطيك إياه ngrok في Meta Console:
```
https://xxxx-xx-xx-xxx-xxx.ngrok-free.app/webhook
```

---

### 2. اختبار الـ Production Webhook

بعد نشر المشروع على Cloud Run أو VM، اختبر الـ webhook:

```bash
# اختبار GET (Verification)
curl "https://YOUR_URL/webhook?hub.mode=subscribe&hub.verify_token=LionBot2024SecureToken&hub.challenge=test123"

# يجب أن يرجّع: test123
```

---

### 3. إرسال رسالة تجريبية من WhatsApp
1. افتح WhatsApp على هاتفك
2. ابحث عن رقم الـ Test Number المعطى من Meta Console
3. أرسل رسالة: **"مرحبا"** أو **"Hello"**
4. يجب أن يرد البوت عليك! 🎉

---

## 🔒 إنشاء Permanent Access Token (مهم جداً!)

**⚠️ الـ Token المؤقت من Meta سينتهي بعد 24 ساعة!**

### كيف تنشئ Permanent Token:

1. اذهب إلى **WhatsApp** → **Configuration**
2. تحت **"Access Tokens"**، اضغط **"Create Permanent Token"**
3. اختر الـ Permissions المطلوبة:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
4. انسخ الـ Token وضعه في `.env`:
   ```env
   WHATSAPP_API_TOKEN=EAAxxxxxx_PERMANENT_TOKEN
   ```

---

## ✅ Checklist قبل التشغيل

- [ ] نشرت Backend على Cloud Run أو VM
- [ ] أضفت Webhook URL في Meta Console  
- [ ] أضفت Verify Token في Meta Console AND `.env`
- [ ] اشتركت في `messages` webhook field
- [ ] أنشأت Permanent Access Token
- [ ] أضفت جميع المتغيرات في `.env`
- [ ] اختبرت الـ webhook بـ curl
- [ ] أرسلت رسالة تجريبية من WhatsApp

---

## 🆘 استكشاف الأخطاء

### ❌ Webhook Verification Failed
**السبب:** Verify Token غير متطابق

**الحل:**
```bash
# تأكد أن القيمة نفسها في:
# 1. Meta Console → Webhook → Verify Token
# 2. backend/.env → WHATSAPP_VERIFY_TOKEN
```

---

### ❌ البوت لا يردّ على الرسائل
**الحل:**
1. تأكد أن الـ Backend شغّال:
   ```bash
   curl https://YOUR_URL/health
   # يجب أن يرجّع: {"status":"healthy"}
   ```

2. شاهد الـ Logs:
   ```bash
   # Cloud Run
   gcloud run logs tail YOUR_SERVICE_NAME
   
   # Docker
   docker logs -f backend
   ```

---

### ❌ Error: Invalid Token
**السبب:** الـ Token منتهي أو خاطئ

**الحل:** أنشئ Permanent Token جديد من Meta Console

---

## 📞 معلومات مهمة

### رقم الاختبار (Test Number)
- Meta تعطيك رقم وهمي للاختبار مجاناً
- يمكنك إضافة **حتى 5 أرقام** للاختبار
- لاستخدام البوت مع **جميع العملاء**، تحتاج:
  1. التحقق من Business (Meta Business Verification)
  2. الموافقة على تطبيقك (App Review)

### التكلفة
- **1000 رسالة مجانية شهرياً**
- بعدها: حوالي $0.005 لكل رسالة (حسب الدولة)

---

**🦁 جاهز! الآن لديك كل المعلومات لإعداد WhatsApp Webhook الخاص بـ Lion Bot!**
