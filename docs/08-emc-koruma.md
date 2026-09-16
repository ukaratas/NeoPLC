# 08 — EMC ve Koruma

---

## 1. Arayüz bazlı koruma matrisi

| Arayüz | Maruziyet | Koruma |
|--------|-----------|--------|
| Güç girişi (12–48V) | Yüksek — saha kablosu | Sigorta → CM choke → TVS 58V → ters polarite/OV FET → bulk ([03 §1](03-guc-mimarisi.md#1-giriş-koruma-katı)) |
| Saha dijital giriş | Yüksek | Seri akım sınırlama direnci + optocoupler (24V, ~4 mA) |
| Saha dijital çıkış | Yüksek | Freewheel diyot + TVS + akım sınırı |
| Saha analog giriş | Yüksek | Seri direnç + diferansiyel filtre + clamp diyotlar |
| RS-485 saha portu | Yüksek | **İzolasyon** + ±15 kV ESD dereceli transceiver + TVS |
| Ethernet | Orta | Magjack entegre manyetik + Bob Smith sonlandırma |
| Backplane | **Düşük — kapalı hacim** | RS-485 common-mode reddi yeterli |

### 1.1 Dijital girişin doğal sağlamlığı

Optocoupler tabanlı dijital giriş, seri direnci sayesinde **kendiliğinden
korumalıdır**:

```
24V saha  ──[ 2.7k ]──  opto LED  ──  saha GND
                 ↓
         akım sınırı ≈ 8 mA
         ESD/surge enerjisi direnç üzerinde düşer
         galvanik izolasyon zaten var
```

Ek TVS gerekiyor ama korumanın ana yükünü seri direnç ve izolasyon taşıyor.
Modül tasarımının en kolay korunan kısmı burası.

### 1.2 Backplane neden düşük riskli

Backplane kapalı metal/plastik kutu içinde, saha kablosuna doğrudan bağlı değil.
Buradaki risk dış EMI değil, **kendi ürettiğimiz gürültü** — modül
regülatörlerinin ground bounce'ı. Bu da RS-485'in common-mode reddi ile
çözülüyor ([05 §1.2](05-dahili-bus.md#12-rs-485-ne-getiriyor)).

---

## 2. Yerleşim prensipleri

| Prensip | Uygulama |
|---------|----------|
| Bölgeleme | Anahtarlamalı güç · haberleşme · hassas analog fiziksel olarak ayrılır |
| Dönüş yolu | Her yüksek hızlı sinyalin altında kesintisiz referans düzlemi |
| Anahtarlama döngüsü | Buck'ın yüksek dI/dt döngüsü (giriş kapasitörü–üst FET–alt FET) mümkün olan en küçük alanda |
| Kristal/osilatör | Anahtarlamalı güçten uzak, altında kesintisiz GND |
| RF | ESP32 modülü anten keepout'una uyulur; U.FL hattı kısa |
| Saha klemensleri | TVS'ler klemense mümkün olduğunca yakın — koruma kartın içine girmeden çalışmalı |

### 2.1 Saha klemensi kuralı

**ESD/surge enerjisi kartın hassas bölgesine ulaşmadan önce kesilmelidir.**
TVS klemense yakın değilse, koruma çalışsa bile enerji kartın içinden geçer ve
yakındaki devrelere kuplaj yapar.

Bu, DRC ile yakalanamayan bir yerleşim kuralıdır — yerleşim incelemesinde elle
kontrol edilecek.

---

## 3. Master kartının zorluğu

Aynı kartta dört gürültü rejimi bir arada:

```
┌─────────────────┬──────────────────────────────────────────┐
│ Anahtarlamalı güç│ 12–48V girişten 15W, yüksek dV/dt        │
│ RF               │ 2.4 GHz WiFi vericisi                    │
│ Yüksek hızlı dij.│ Ethernet 100BASE-TX + SPI ~30 MHz        │
│ Çok noktalı bus  │ 8 slota giden RS-485 + kontrol hatları   │
└─────────────────┴──────────────────────────────────────────┘
```

Bu kombinasyon §5'teki katman sayısı kararının ana gerekçesi.

---

## 4. Uyumluluk hedefi

### 🟢 D-06 — Karar: sertifikasyon hedefi yok, seviye A

| Seviye | Kapsam | Tasarım etkisi | Maliyet |
|--------|--------|----------------|---------|
| **A: Temel** | IEC 61000-4-2 (ESD) · 4-4 (EFT) | TVS + CM choke — mevcut tasarımda dahil | Dahil |
| **B: Tam** | + 61000-4-5 (surge, ±1 kV) | **Kademeli ön kat:** GDT/MOV + seri empedans + TVS. Kart alanı ve maliyet artar | +$3–6, +alan |
| **C: Sertifikalı CE** | + akredite test evi | B'nin üstüne test ve dokümantasyon | +$5–15k, +takvim |

**Bu kararın etkisi:**

- Giriş koruma katının fiziksel alanı ve topolojisi
- Master katman sayısı (§5)
- Klemens seçimi (surge için daha geniş creepage gerekebilir)
- Proje takvimi ve bütçesi

**Karar: Seviye A.** Sertifikasyon hedefi yok.

Yine de giriş koruma katının yerleşimi, kademeli ön kat sonradan eklenebilecek
şekilde tasarlanacak (boş footprint veya ayrılmış alan). Kart alanı dışında
maliyeti yok, ileride B gerekirse yeniden tasarım olmaktan çıkarıyor.

> **Bu kararın ikinci etkisi:** EMC, artık §5'teki katman sayısı kararının
> gerekçelerinden biri **değil**. Uyumluluk zorunluluğu ortadan kalktı; geriye
> sadece **kendi kendine girişim** kaygısı kaldı (WiFi + anahtarlamalı güç +
> Ethernet aynı kartta). Bu gerçek bir kaygı ama "sertifikadan kalırız"
> kaygısından çok daha zayıf.

---

## 5. Katman sayısı kararı

### 5.1 Modüller: 2 katman · 🟡 D-36

Tereddütsüz. Düşük hızlı, düşük güçlü, basit kartlar. Kısıt K3 tam olarak burada
karşılanıyor — **ve modüller sekiz kez üretileceği için tasarrufun asıl etkili
olduğu yer de burası.**

### 5.2 Master: Ethernet hesabı

2 katman 1.6 mm FR4'te kontrollü empedans mümkün mü?

```
2 katman, h = 1.575 mm, εr ≈ 4.3

50Ω tek uçlu microstrip için gereken iz genişliği  ≈  2.9 mm
100Ω diferansiyel çift için gereken geometri        →  pratik değil
```

**Sonuç: 2 katmanda kontrollü empedans mümkün değil.**

Ama kurtaran bir hesap var:

```
100BASE-TX  :  MLT-3, 125 Mbaud, t_r ≈ 4 ns
25 mm iz    :  t_prop = 0.025 / 0.15 = 0.17 ns

Lumped kriteri:  t_prop < t_r / 6
                 0.17 ns  <  0.67 ns    ✓  4× marj
```

**W5500 magjack'e 25 mm içinde yerleştirilirse, 2 katmanda 100BASE-TX çalışır** —
empedans kontrolsüz ama elektriksel olarak toplu devre, yansıma oluşmuyor.

Bu bir **yerleşim kısıtıdır, imkânsızlık değil.**
([02 §2](02-master-mimarisi.md#2-ethernet)'de bağlayıcı kısıt olarak kayıtlı.)

### 5.3 Üç gerekçe yeniden değerlendirildi

İlk taslakta 4 katman için üç gerekçe sıralanmıştı. D-06 ve D-31 kararlarından
sonra ikisi zayıfladı:

| # | Gerekçe | İlk durum | Şimdiki durum |
|---|---------|-----------|---------------|
| 1 | **Termal** | 15W → 2 katmanda 140°C junction ✗ | **2A/10W → 114°C, 11°C marj.** Çalışıyor ama dar |
| 2 | **EMC** | Sertifikasyon riski | **Sertifikasyon yok** (D-06). Sadece kendi kendine girişim kaldı — zayıfladı |
| 3 | **Ethernet** | 25 mm yerleşim kısıtı | Geçerli, ama D-47 (Ethernet gerekli mi?) açıksa tamamen düşebilir |

**Maliyet farkı:** JLCPCB'de 4 katman adet bazında ~$2. Master tek kart —
modüller gibi sekiz kez üretilmiyor.

### Karar: 🟡 D-05 — artık zorunlu değil, marj tercihi

**Öneri: 4 katman.** Gerekçe artık "2 katman çalışmaz" değil,
**"60 °C ortamda 11 °C termal marj yetersiz"**:

- Karavan kapalı hacminde zorlamalı hava akımı yok
- 60 °C zaten iyimser olabilir (park halinde kara kutu içinde daha yüksek)
- Titreşim + termal döngü birlikte yaşlanmayı hızlandırıyor (K5)
- Master tek kart — $2 birim maliyet farkı önemsiz

**2 katman seçilirse** çalışır, ama:
- Termal marj 11 °C — parça seçiminde 150 °C sınıfı tercih edilmeli
- Ethernet 25 mm kısıtı bağlayıcı hale gelir
- D-31 (2A) yukarı revize edilemez

**Bu senin marj tercihin.** Teknik olarak iki seçenek de savunulabilir.

### 5.4 Önerilen stackup (master, 4 katman)

```
L1  Sinyal + bileşenler
L2  GND düzlemi          ← kesintisiz, bölünmez
L3  Güç düzlemleri       (+3V3, +5V_SYS, VBUS_RAW bölgeleri)
L4  Sinyal + güç dökümü
```

L2'nin kesintisiz olması 4 katmanın kazancının büyük kısmı — bölünmüş bir ground
plane, avantajın çoğunu geri veriyor.

**2 katman seçilirse stackup:**

```
L1  Sinyal + bileşenler + GND dökümü
L2  Ağırlıklı GND dökümü + kaçınılmaz sinyal geçişleri
```

L2'deki her sinyal geçişi ground'u böler. Kritik kural: **güç katının ve
Ethernet bölgesinin altındaki GND dökümü hiçbir sinyalle bölünmemeli** — sinyal
geçişleri bu bölgelerin dışına yönlendirilmeli.
