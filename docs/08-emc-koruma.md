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
| *Ethernet (opsiyonel haberleşme node'u)* | Orta | Magjack entegre manyetik + Bob Smith sonlandırma — **host'ta yok** (D-47) |
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
Node tasarımının en kolay korunan kısmı burası.

### 1.2 Backplane neden düşük riskli

Backplane kapalı metal/plastik kutu içinde, saha kablosuna doğrudan bağlı değil.
Buradaki risk dış EMI değil, **kendi ürettiğimiz gürültü** — node
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
| RF | ESP32 modülünün anten keepout'una uyulur; U.FL hattı kısa |
| Saha klemensleri | TVS'ler klemense mümkün olduğunca yakın — koruma kartın içine girmeden çalışmalı |

### 2.1 Saha klemensi kuralı

**ESD/surge enerjisi kartın hassas bölgesine ulaşmadan önce kesilmelidir.**
TVS klemense yakın değilse, koruma çalışsa bile enerji kartın içinden geçer ve
yakındaki devrelere kuplaj yapar.

Bu, DRC ile yakalanamayan bir yerleşim kuralıdır — yerleşim incelemesinde elle
kontrol edilecek.

---

## 3. Host kartının zorluğu

Aynı kartta üç gürültü rejimi bir arada:

```
┌─────────────────┬──────────────────────────────────────────┐
│ Anahtarlamalı güç│ 12–48V girişten ~8W, yüksek dV/dt        │
│ RF               │ 2.4 GHz Wi-Fi vericisi (talep üzerine)   │
│ Çok noktalı bus  │ 8 slota giden RS-485 + kontrol hatları   │
└─────────────────┴──────────────────────────────────────────┘
```

Ethernet host'tan çıkarıldığı için (D-47) yüksek hızlı diferansiyel rejim
listeden düştü — geriye **üç** rejim kaldı.

Bu kombinasyon §5'teki katman sayısı kararının ana gerekçesi.

---

## 4. Uyumluluk hedefi

### D-06 — Karar: sertifikasyon hedefi yok, seviye A

| Seviye | Kapsam | Tasarım etkisi | Maliyet |
|--------|--------|----------------|---------|
| **A: Temel** | IEC 61000-4-2 (ESD) · 4-4 (EFT) | TVS + CM choke — mevcut tasarımda dahil | Dahil |
| **B: Tam** | + 61000-4-5 (surge, ±1 kV) | **Kademeli ön kat:** GDT/MOV + seri empedans + TVS. Kart alanı ve maliyet artar | +$3–6, +alan |
| **C: Sertifikalı CE** | + akredite test evi | B'nin üstüne test ve dokümantasyon | +$5–15k, +takvim |

**Bu kararın etkisi:**

- Giriş koruma katının fiziksel alanı ve topolojisi
- Host katman sayısı (§5)
- Klemens seçimi (surge için daha geniş creepage gerekebilir)
- Proje takvimi ve bütçesi

**Karar: Seviye A.** Sertifikasyon hedefi yok.

Yine de giriş koruma katının yerleşimi, kademeli ön kat sonradan eklenebilecek
şekilde tasarlanacak (boş footprint veya ayrılmış alan). Kart alanı dışında
maliyeti yok, ileride B gerekirse yeniden tasarım olmaktan çıkarıyor.

> **Bu kararın ikinci etkisi:** EMC, artık §5'teki katman sayısı kararının
> gerekçelerinden biri **değil**. Uyumluluk zorunluluğu ortadan kalktı; geriye
> sadece **kendi kendine girişim** kaygısı kaldı (anahtarlamalı güç + talep
> üzerine açılan Wi-Fi aynı kartta). Bu gerçek bir kaygı ama "sertifikadan
> kalırız" kaygısından çok daha zayıf.

---

## 5. Katman sayısı kararı

### 5.1 Node'lar: 2 katman · D-36

Tüm node, **istisnasız 2 katman.** 4 katman yok. Sığmazsa **2U** (D-61, max
form D-75) veya **modül bölünür** (ör. CAN | Ethernet iki 1U) — katman artmaz.

Sekiz kez üretilir; tasarruf burada. COM magjack: W5500 ≤ 25 mm (lumped
100BASE-TX) 2 katmanda yeter; yetmezse COM 2U veya iki SKU, 4 katman değil.

### 5.2 Host: Ethernet hesabı (tarihsel)

> Ethernet host kartından çıkarıldı (D-47). Bu bölüm, 2 katmanda Ethernet'in
> **mümkün olduğunu** gösteren hesabı kayıt altında tutuyor — Ethernet node'u
> tasarlanırken aynı hesap geçerli olacak
> ([09 §5](09-node-aileleri.md#5-node-ailesi-yol-haritası)).

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
([02 §2](02-host-mimarisi.md#2-ethernet-hosttan-çıkarıldı)'de bağlayıcı kısıt olarak kayıtlı.)

### 5.3 Üç gerekçe yeniden değerlendirildi

İlk taslakta 4 katman için üç gerekçe sıralanmıştı. D-06 ve D-31 kararlarından
sonra ikisi zayıfladı:

| # | Gerekçe | İlk durum | Şimdiki durum |
|---|---------|-----------|---------------|
| 1 | **Termal** | 15W → 2 katmanda 140°C junction ✗ | **2.0 A / 10 W → ~114 °C, 11 °C marj** ✓ |
| 2 | **EMC** | Sertifikasyon riski | **Sertifikasyon yok** (D-06) — düştü |
| 3 | **Ethernet** | 25 mm yerleşim kısıtı | **Ethernet host'tan çıkarıldı** (D-47) — düştü |

**Üç gerekçe de ortadan kalktı.** Termal hesap güncel değerlerle:

```
Ana buck 2.0 A / 10 W  ·  verim ~%86  →  kayıp ≈ 1.36 W

2 katman, geniş döküm  θ_ja ≈ 40 °C/W
    ΔT = 54 °C   →  junction ≈ 114 °C @ 60 °C ortam
    125 °C sınırına  11 °C marj                       ✓

4 katman + termal via  θ_ja ≈ 25 °C/W
    ΔT = 25 °C   →  junction ≈  85 °C                  ✓✓
```

**Maliyet farkı:** JLCPCB'de 4 katman adet bazında ~$2. Host tek kart —
node'lar gibi sekiz kez üretilmiyor.

### Karar: host 2 katman · D-05

Brief'in kuralı: *"Yüksek yoğunluk, sinyal bütünlüğü veya EMC gereksinimi
nedeniyle zorunlu olmadıkça 4 katmana geçilmemelidir."*

**Artık zorlayan bir gerekçe kalmadı.** Üçü de bağımsız kararlarla çözüldü:
sertifikasyon hedefi kalktı (D-06), Ethernet host'tan çıktı (D-47), buck
**2.0 A / 10 W** (D-31) 2 katmanda durur. 3 A / 15 W yakardı.

> İlginç olan, bu sonucun katman tartışmasından değil **enerji bütçesi
> çalışmasından** gelmesi. Tüketimi düşürmek için yapılan her şey aynı zamanda
> ısıyı da düşürdü.

### Karar koşulları — bunlar değişirse yeniden değerlendirilir

| Koşul | Eşik |
|-------|------|
| Ana buck tasarım noktası | **> 2.0 A sürekli** → 2 katman yeniden |
| Ethernet host'a geri eklenirse | 25 mm yerleşim kısıtı geri gelir |
| EMC sertifikasyonu hedeflenirse | Kesintisiz ground plane ihtiyacı doğar |
| Ortam sıcaklığı > 60 °C | Marj tükenir |

Her biri karar kütüğünde bağlı karar olarak izlenmeli.

### 5.4 Önerilen stackup (host, 2 katman)

```
L1  Sinyal + bileşenler + GND dökümü
L2  Ağırlıklı GND dökümü + kaçınılmaz sinyal geçişleri
```

2 katmanda ground plane'in bütünlüğünü korumak en önemli iş. L2'deki her
sinyal geçişi ground'u bölüyor.

**Bağlayıcı yerleşim kuralları:**

| Kural | Gerekçe |
|-------|---------|
| Güç katının altındaki GND dökümü hiçbir sinyalle bölünmemeli | Anahtarlama döngüsünün dönüş yolu kesintisiz olmalı |
| ESP32 anten keepout'una uyulmalı | WROOM datasheet gereksinimi |
| Buck'ın yüksek dI/dt döngüsü (giriş kapasitörü–üst FET–alt FET) en küçük alanda | Radiated emission ve ringing |
| Backplane konnektörüne giden RS-485 çifti birlikte yönlendirilmeli | Diferansiyel bütünlüğü |
| Sinyal geçişleri güç bölgesinin dışına yönlendirilmeli | Yukarıdaki ilk kuralın uygulaması |

**4 katmana geçilirse** (§5'teki karar koşullarından biri tetiklenirse):

```
L1  Sinyal + bileşenler
L2  GND düzlemi          ← kesintisiz, bölünmez
L3  Güç düzlemleri       (+3V3, +5V, VIN bölgeleri)
L4  Sinyal + güç dökümü
```

L2'nin kesintisiz olması 4 katmanın kazancının büyük kısmı — bölünmüş bir
ground plane avantajın çoğunu geri veriyor.
