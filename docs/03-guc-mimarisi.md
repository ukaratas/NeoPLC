# 03 — Güç Mimarisi

## 1. Giriş koruma katı

### 1.1 Gerilim sınıfı zinciri

48V nominal endüstriyel besleme, ±%10 toleransla:

```
Nominal maksimum          48 V × 1.10  =  52.8 V  (sürekli)
TVS standoff seçimi                       58   V  (> 52.8 V olmalı)
TVS clamp gerilimi @ Ipp                  ~93  V  (SMBJ58A sınıfı)
                                          ─────
Downstream parçaların görebileceği en yüksek gerilim
```

Bu zincir, ön kattaki her parçanın gerilim sınıfını belirliyor. Ve burada
maliyeti belirleyen bir çatal var.

### 1.2 Kritik çatal: 100V mı 60V mı?

| Yaklaşım | Sonuç |
|----------|-------|
| **(a)** Tüm ön kat 100V sınıfı | 100V/3A senkron buck gerekir → LCSC'de seçenek az, fiyat yüksek |
| **(b)** Seri koruma FET'i + gate zener clamp (~55V'ta kesiyor) | Downstream **60V sınıfı** yeterli → ucuz ve bol seçenek |

### Karar: (b) · 🟡 D-09

Tek bir seri FET üç işi birden yapıyor:

1. **Ters polarite koruması** — yanlış bağlantıda iletmiyor
2. **Aşırı gerilim kesme** — gate zener clamp'i ~55V üstünü geçirmiyor
3. **Inrush kontrolü** — gate RC'si ile yumuşak başlatma

TVS transient enerjisini yutarken FET downstream'i koruyor. Sonuç: ana
dönüştürücü 60V sınıfında kalıyor — maliyet ve tedarik açısından belirleyici
fark.

### 1.3 Zincir

```
Klemens → Sigorta (2.5A yavaş) → CM choke → TVS 58V → Ters polarite + OV FET
        → Bulk kapasitör → Ana buck
```

| Kademe | Amaç | Aday parça sınıfı |
|--------|------|-------------------|
| Sigorta | Kalıcı arıza izolasyonu | 2.5A yavaş atan, 125V DC kesme |
| CM choke | İletilen emisyon + EFT | Ferrit CM choke, ≥ 1mH, 3A |
| TVS | Transient enerji yutma | SMBJ58A / SMCJ58A (daha yüksek enerji) |
| FET | Ters polarite + OV + inrush | P-kanal ≥ 100V **veya** ideal-diyot kontrolcü + N-kanal |
| Bulk | Giriş rippled ve transient tampon | ≥ 63V elektrolitik / polimer |

> **Açık nokta:** P-kanal 100V FET'ler LCSC'de düşük R_DSon'da pahalılaşıyor.
> Alternatif topolojiler (GND dönüşünde N-kanal — ucuz ama GND sürekliliğini
> bozar; ideal-diyot kontrolcü + N-kanal — temiz ama +$1) şema aşamasında stok
> doğrulamasıyla birlikte kesinleştirilecek.

### 1.4 Ele alınması gereken saha koşulları

| Koşul | Önlem | Doküman |
|-------|-------|---------|
| Ters polarite | Seri FET (§1.2) | bu doküman |
| Aşırı gerilim | Gate zener clamp (§1.2) | bu doküman |
| Surge / transient | TVS + CM choke, tam uyum için kademeli ön kat | [08](08-emc-koruma.md) |
| ESD | TVS + klemens yerleşimi | [08](08-emc-koruma.md) |
| Kısa devre | Sigorta (sistem) + slot load switch (modül) | [06 §7](06-slot-yonetimi.md#7-slot-başına-akım-koruması) |
| Brownout | MCU BOR + modüllerin reset'te tutulması | [06 §6](06-slot-yonetimi.md#6-reset-varsayılan-durumu) |
| Ani yük değişimi | Bulk + slot başına soft-start | §2, [06 §7](06-slot-yonetimi.md#7-slot-başına-akım-koruması) |

---

## 2. Rail topolojisi

### Karşılaştırma

| Seçenek | Modül maliyeti | EMI | Değerlendirme |
|---------|----------------|-----|---------------|
| Backplane'e ham 12–48V, her modülde geniş girişli buck | 8 × ~$1.20 | 8 ayrı yüksek dV/dt kaynağı | Pahalı ve gürültülü. K1'i ihlal ediyor. |
| Sadece +5V dağıt | 8 × ~$0.15 | Tek anahtarlama kaynağı | Röle ve analog çıkış modülleri saha gerilimi bulamaz |
| **İkili rail** | Çoğu modülde ~$0.15 | Tek ana kaynak | **Esnek ve ucuz** |

### Karar: ikili rail · 🟡 D-08

| Rail | Gerilim | Kaynak | Kullanım |
|------|---------|--------|----------|
| **+5V_SYS** | 5V ±%3 | Master'da tek verimli senkron buck | Modül lojiği. Modül 5V→3.3V için ucuz LDO/buck kullanır. |
| **VBUS_RAW** | 12–48V (ham) | Giriş koruma katı çıkışı | Sadece ihtiyacı olan modül: röle bobini, analog çıkış compliance gerilimi, izole DC-DC primeri |

**Neden bu doğru:** Modüllerin ezici çoğunluğu sadece lojik besleme istiyor.
Onlara ham 48V verip her birine geniş girişli buck koydurmak, K1'in tam tersi —
maliyeti sekiz kez ödemek. Tek iyi dönüştürücüyü master'da bir kez yapıyoruz.

VBUS_RAW yine de her slota gidiyor çünkü **pinout geri dönülemez** — ihtiyaç
duyan modül tipi için sonradan eklenemez.

---

## 3. Ana dönüştürücü

| Parametre | Değer |
|-----------|-------|
| Giriş | 12–48V (ön kat sonrası ≤ 55V) |
| Çıkış | 5V |
| Tasarım akımı | **2A (10W)** · 🟡 D-31 — *enerji bütçesi düzeltmesiyle 3A'dan düşürüldü* |
| Topoloji | **Senkron** buck |
| Gerilim sınıfı | 60V |
| Anahtarlama frekansı | 300–500 kHz (verim / boyut dengesi) |

### Neden 3A değil 2A

İlk tahsis (3A), slot başına 200 mA'in **sürekli** çekileceği varsayımına
dayanıyordu. [Wake-on-bus](10-enerji-butcesi.md#3-wake-on-bus-modüllerin-uyuması)
ile bu varsayım geçersiz:

```
Modül lojiği, uyanık            ≈  10 mA @3.3V  ≈  12 mA @5V
Duty cycle (10 Hz)              =  %0.6
Gerçekçi ortalama               ≈  1 mA @5V
Gerçekçi tepe (analog modül)    ≈  40 mA @5V

8 slot tepe    =  320 mA
Master tepe    ≈  380 mA @5V
               ─────────
Toplam tepe    ≈  700 mA     →  2A tasarım noktası %185 headroom bırakıyor
```

200 mA/slot **tavanı** korunuyor (bir modül geçici olarak çekebilmeli), ama
toplam ≤ 1.6 A descriptor güç beyanı ile zorlanıyor
([06 §6](06-slot-yonetimi.md#6-reset-varsayılan-durumu)).

### Senkron neden zorunlu

Non-senkron buck'ta 48V→5V dönüşümde catch diyot çevrimin ~%90'ında iletir:

```
P_diyot = Vf × Iout × (1 − D)
        = 0.5V × 2A × 0.90
        = 0.90 W       ← tek başına, sadece diyotta
```

Senkron alt FET (R_DSon ≈ 20mΩ) ile:

```
P_altFET = I² × R_DSon × (1 − D)
         = 4 × 0.020 × 0.90
         = 0.07 W
```

**~0.8W tasarruf.** §5'teki termal analiz göz önüne alındığında bu fark
belirleyici.

### 3.1 Hafif yük verimi — asıl kriter

**Sistem zamanının %90'ından fazlasını 50–200 mA çekerek geçiriyor**
([10 §5](10-enerji-butcesi.md#5-güç-durumu-bütçeleri)). Sadece CCM çalışan bir
buck bu bölgede %50 verimde olabilir; PFM / pulse-skipping destekleyen bir buck
%85.

**Tam yük verimi neredeyse hiç kullanılmıyor.** Seçim kriteri sıralaması
tersine döndü — ayrıntı [10 §7.2](10-enerji-butcesi.md#72-dönüştürücü-seçim-kriterleri--değişti).

### 3.2 İki dönüştürücülü yapı

Ana buck tek başına yeterli değil: S3 depo modunda 25 µA mertebesinde Iq
gerekiyor ve 2A için optimize edilmiş bir dönüştürücü bunu veremiyor.

```
12–48V ─┬─→ Housekeeping buck  3.3V / 500 mA / Iq ≤ 25 µA   ── sürekli açık
        └─→ Ana buck           5V / 2A / EN pinli, senkron, PFM  ── S3'te kapalı
```

Gerekçe ve hesap: [10 §7.1](10-enerji-butcesi.md#71-i̇ki-dönüştürücülü-yapı--🟡-d-42)

### 3.3 3.3V rail

5V → 3.3V, ESP32 WiFi TX tepe akımı 350mA.

LDO ile: `(5.0 − 3.3) × 0.65A = 1.1W` — 2 katmanda küçük paket için fazla.
**Buck kullanılacak.** ESP32'nin temiz besleme ihtiyacı için LC filtre + yerel
bulk eklenecek.

---

## 4. Güç bütçesi

### 4.1 Slot başına (+5V_SYS)

| Modül tipi | Tipik | Maksimum |
|------------|-------|----------|
| Dijital giriş (8 kanal) | 30 mA | 80 mA |
| Dijital çıkış (8 kanal) | 50 mA | 120 mA |
| Analog giriş (4 kanal, 16-bit) | 60 mA | 150 mA |
| Röle çıkış (bobin VBUS_RAW'dan) | 40 mA | 100 mA |

### Tahsis · 🟡 D-29

| Slot | +5V_SYS | VBUS_RAW |
|------|---------|----------|
| **1U** | **200 mA (1.0 W)** | 500 mA |
| **2U** | **400 mA (2.0 W)** | 500 mA |

2U modül tek konnektörden ([04 §4](04-backplane-mekanik.md#4-2u-modül-stratejisi))
400mA çekiyor. 2 adet +5V_SYS kart kenarı kontağı üzerinden 400mA — 2.54mm
kontak akım kapasitesinin çok altında, sorun yok.

### 4.2 Master kartı

| Blok | Akım | Güç |
|------|------|-----|
| ESP32-S3 — WiFi aktif ortalama | 150 mA @3.3V | 0.50 W |
| ESP32-S3 — WiFi TX tepe | 350 mA @3.3V | 1.16 W |
| W5500 + magjack (100 Mbps) | 150 mA @3.3V | 0.50 W |
| İzole RS-485 (xcvr + izole DC-DC) | 40 mA @5V | 0.20 W |
| PCA9555 + LED'ler + misc | 60 mA @3.3V | 0.20 W |
| **Master toplam (5V'tan)** | | **~2.0 W tipik / 3.0 W tepe** |

### 4.3 Sistem toplamı

```
8 slot × 1.0 W (maksimum)          =   8.0 W
Master (tepe)                      =   3.0 W
                                      ───────
+5V_SYS yükü (en kötü durum)       =  11.0 W   →  5V @ 2.2 A

Tasarım noktası                    =  5V @ 3.0 A (15 W)
Headroom                           =  %36

Giriş gücü @ %88 verim             =  17.0 W
    @ 12 V  →  1.42 A     ← en yüksek giriş akımı, boyutlandırma buradan
    @ 24 V  →  0.71 A
    @ 48 V  →  0.35 A

Giriş sigortası                    =  2.5 A yavaş atan
VBUS_RAW toplam limiti             =  2 A (slot başına 500 mA)
```

**Not:** Gerçekçi karışık konfigürasyonda +5V_SYS yükü ~5–6W olacak. 15W tasarım
noktası, tüm slotların aynı anda maksimum çektiği teorik en kötü durumu
karşılıyor.

### 4.4 Güç bütçesi zorlaması

Bütçe kâğıt üzerinde kalmıyor — **donanımla zorlanıyor.** Modül descriptor'ı
beyan ettiği tüketimi içeriyor; master, bütçe aşılıyorsa modülün reset'ini
bırakmıyor.

Ayrıntı: [06 §6](06-slot-yonetimi.md#6-reset-varsayılan-durumu) ve
[05 §7](05-dahili-bus.md#7-modül-descriptorı).

---

## 5. Termal analiz

**Ortam sıcaklığı: 60 °C** · 🟢 D-04 — karavan, kapalı mekân, güneş altında
50 °C rahat görülür. Zorlamalı hava akımı yok, sadece doğal konveksiyon.

### 5.1 Ana buck kaybı — iki senaryo

```
EN KÖTÜ DURUM (tüm slotlar tepe)
    Çıkış  10 W  ·  verim ~%86  →  kayıp ≈ 1.36 W

GERÇEKÇİ SÜREKLİ (S1/S2)
    Çıkış  0.5–2 W  ·  PFM       →  kayıp ≈ 0.1–0.3 W
```

Enerji bütçesi mimarisi sayesinde **sürekli çalışma noktası en kötü durumun
onda biri.** Termal tasarım en kötü duruma göre yapılır ama gerçek hayatta
oraya nadiren gidilir.

### 5.2 60 °C'de ne oluyor

| Stackup | θ_ja (geniş döküm) | ΔT @1.36W | Junction @60°C | Değerlendirme |
|---------|--------------------|-----------|----------------|---------------|
| 2 katman | ~40 °C/W | 54 °C | **114 °C** | Sınırda — 125 °C sınırına 11 °C marj |
| 4 katman + termal via | ~25 °C/W | 34 °C | **94 °C** | Rahat — 31 °C marj |

### 5.3 Sonuç

**2 katman en kötü durumda çalışır, ama marjı dar.** Bu artık bir zorunluluk
değil, bir marj tercihi — ayrıntı ve karar
[08 §5](08-emc-koruma.md#5-katman-sayısı-kararı).

> **Not:** D-31'in 3A'dan 2A'ya düşmesi bu tabloyu değiştirdi. 3A/15W'ta
> 2 katman 60 °C'de sınır aşıyordu (140 °C junction). Enerji bütçesi çalışması
> termal problemi de çözdü — aynı kök nedenden.
