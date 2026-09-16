# 06 — Slot Yönetimi

Adresleme, discovery, presence/fault/reset mantığı ve güç bütçesi zorlaması.

---

## 1. Slot adresleme

| Yöntem | Pin | Değerlendirme |
|--------|-----|---------------|
| **4-bit coğrafi (backplane'de sabit)** | 4 | **Slot no = fiziksel konum.** Teknisyenin gördüğü şeyle aynı. Yazılımsız, gürültüye bağışık, modül değişiminde korunur. VME / CompactPCI / PXI'nin yaptığı. |
| Analog: slot başına direnç + modülde ADC | 1 | 3 pin tasarruf, ama %1 direnç toleransı + ADC doğruluğu + gürültü riski |
| Enumerasyon (unique ID ile) | 0 | **Fiziksel konum bilgisi yok.** "3 numaralı slottaki modül arızalı" denemez. Saha servisi için kabul edilemez. |

### Karar: 4-bit coğrafi adresleme · 🟡 D-17

```
Slot 0 :  ADDR3=açık  ADDR2=açık  ADDR1=açık  ADDR0=açık    → 0000
Slot 1 :  ADDR3=açık  ADDR2=açık  ADDR1=açık  ADDR0=GND     → 0001
Slot 2 :  ADDR3=açık  ADDR2=açık  ADDR1=GND   ADDR0=açık    → 0010
  ...
Slot 7 :  ADDR3=açık  ADDR2=GND   ADDR1=GND   ADDR0=GND     → 0111

Modül tarafı: her ADDR hattında 10k pull-up → açık = 1, GND = 0
```

**Neden 4 bit, 3 değil:** 8U için 3 bit yeterli olurdu. 4. bit, 16 slota kadar
genişleme başlığı bırakıyor. Maliyeti 1 backplane pini + 1 direnç — pinout geri
dönülemez olduğu için şimdi alınması gereken bir sigorta.

**Analog yöntemin elenme sebebi:** Kart kenarı konnektöründe pin bol. Dijital ve
gürültüye bağışık olmak, 3 pin tasarrufundan kat kat değerli.

---

## 2. Naif tasarımın problemi

8 slotu doğrudan MCU'ya bağlamak:

```
8 × PRESENT#  +  8 × FAULT#  +  8 × RESET#  +  8 × BOOT#  =  32 GPIO
```

ESP32-S3-WROOM'da ~30 kullanılabilir GPIO var — sadece slot yönetimi tüm bütçeyi
yiyor, Ethernet ve bus'a yer kalmıyor.

---

## 3. Master tarafı I/O genişletme

### Karar: üç katmanlı çözüm — 32 sinyal → 4 GPIO · 🟡 D-18

#### Katman 1 — PRESENT# ve MOD_RST# → tek PCA9555

```
PCA9555 (I²C, 16-bit)
  Port 0 (giriş)   :  8 × PRESENT#
  Port 1 (çıkış)   :  8 × MOD_RST#
  INT# pini        :  presence değişiminde tetiklenir
```

**INT# pini kritik:** Hot-plug algılaması polling'siz, kesme ile geliyor. Modül
takıldığı anda master haberdar oluyor.

Maliyet: 2 GPIO (I²C) + 1 GPIO (INT#) = **3 GPIO, 16 sinyal.**

#### Katman 2 — FAULT# → ortak wired-OR

8 ayrı fault hattı yerine **tek ortak open-drain hat.** Ayrıntı §4.

Maliyet: **1 GPIO, 8 slotun arıza bildirimi.**

#### Katman 3 — BOOT# → ortak hat + reset zamanlaması

8 ayrı boot hattı yerine **tek ortak hat.** Ayrıntı §5.

Maliyet: **0 ek GPIO** (PCA9555'in yedek pininden sürülür), 7 backplane hattı
tasarrufu.

### Sonuç

| | Naif | Üç katmanlı |
|---|---|---|
| MCU GPIO | 32 | **4** |
| Backplane hattı / slot | 4 | **2** (PRESENT#, MOD_RST#) |
| Ortak backplane hattı | 0 | 2 (FAULT#, BOOT#) |

---

## 4. FAULT# hattı

### Karar: ortak open-drain wired-OR + protokolle sorgu · 🟡 D-20

```
Modül 0 ──┐
Modül 1 ──┤
   ...    ├── FAULT#  ──10k pull-up──  +3V3
Modül 7 ──┘      │
                 └──→ Master GPIO (kesme, düşen kenar)
```

**Akış:**

1. Herhangi bir modül arıza tespit eder → FAULT#'u GND'ye çeker
2. Master kesme alır — **polling gecikmesi yok**
3. Master tarama döngüsü sonunda `GET_DIAG` ile kaynağı arar
4. Arıza giderilince modül hattı bırakır

**Neden bu tasarım doğru:** Katı master-slave polling'in tek zayıflığı olay
gecikmesidir ([05 §5](05-dahili-bus.md#5-trafik-modeli)). Bir donanım hattı bunu
çözüyor — multi-master bus'ın karmaşıklığına girmeden event-driven davranış elde
ediliyor.

8 pin yerine 1 pin, üstelik daha hızlı.

---

## 5. BOOT# stratejisi

### Karar: ortak BOOT# + hedef slotun RST# bırakılması · 🟡 D-19

Naif yaklaşım slot başına BOOT# hattı ister (8 pin). Bunun yerine:

```
1. Master BOOT#'u düşürür                    (ortak hat, tüm slotlara gider)
2. Master SADECE hedef slotun MOD_RST#'ini bırakır
3. O modül reset'ten çıkarken BOOT#'u örnekler → bootloader'a girer
4. Diğer modüller etkilenmez — reset'lerine dokunulmadı
5. Master BOOT#'u bırakır
```

**7 pin ve 7 backplane hattı tasarrufu.** Seçicilik BOOT# hattından değil,
reset zamanlamasından geliyor.

### 5.1 Neden donanım kaçışı gerekli

Bootloader'a girmenin normal yolu protokol komutudur (`0x7F RESET` + bayrak).
Ama app tamamen kilitlenip bus'ı meşgul ederse protokol çalışmaz.

BOOT# hattı bu durumda **tek kurtarma yolu.** Modülü sökmeden, cihazı açmadan,
SWD gerektirmeden kurtarma sağlıyor. Ayrıntı: [07 §4](07-firmware-update.md#4-kurtarma).

---

## 6. Reset varsayılan durumu

### Karar: modülde 10k pull-**down** → varsayılan reset'te · 🟡 D-22

```
MOD_RST#  ──10k──  GND        (modül üzerinde)
    │
    └── Master PCA9555 Port1 çıkışı
```

**PCA9555 güç açılışında tüm pinleri giriş (yüksek-Z) yapar.** Pull-down
sayesinde bu durumda modül **reset'te tutulur.**

### 6.1 Bunun sağladığı güvenlik özelliği

```
Modül takılır
   ↓
MCU reset'te — µA mertebesinde çekiyor
   ↓
Master PRESENT# görür → IDENTIFY gönderir
   ↓
Descriptor'daki "beyan edilen güç tüketimi" okunur
   ↓
┌─────────────────────────────┬──────────────────────────────┐
│ Bütçe yeterli               │ Bütçe aşılıyor               │
│   → MOD_RST# bırakılır      │   → MOD_RST# bırakılmaz      │
│   → modül çalışır           │   → modül reset'te kalır     │
│                             │   → Modbus'ta hata bildirilir│
└─────────────────────────────┴──────────────────────────────┘
```

**Güç bütçesi donanımla zorlanıyor.** Bir kullanıcı rafı aşırı doldurursa sistem
çökmüyor — fazla modül basitçe devreye alınmıyor ve durum raporlanıyor.

Pull-**up** seçseydik modüller master hazır olmadan çalışmaya başlardı ve bu
koruma mümkün olmazdı. Tek direncin yönü, bir sistem özelliğini belirliyor.

### 6.2 İkinci işlev: S3 depo modu

Bu mekanizma sonradan ikinci bir amaca hizmet etti: **S3 depo modunda tüm
modüller reset'te tutularak µA seviyesine indiriliyor**
([10 §4.1](10-enerji-butcesi.md#41-s3--mevcut-kararların-beklenmedik-yakınsaması)).

Güç bütçesi zorlaması için tasarlanan pull-down, batarya ömrünün de mekanizması
oldu. Ek donanım gerekmedi.

> **Not:** Modülün reset'te µA çekmesi, MCU reset pininin gerçekten MCU'yu
> reset'te tutmasına bağlı. Modül tasarımında MOD_RST#'in doğrudan MCU NRST'ye
> (veya bir enable hattına) gitmesi gerekiyor.

---

## 7. Slot başına akım koruması

### Karar: akım sınırlı load switch (+5V_SYS üzerinde) · 🟡 D-23

Maliyet: ~$0.20 × 8 = **$1.60** master başına.

Üç işi birden yapıyor:

| İşlev | Kazanç |
|-------|--------|
| **Arıza izolasyonu** | Kısa devre yapan bir modül tüm rafı düşürmüyor |
| **Soft-start** | Hot-plug inrush'ı sınırlıyor — komşu slotların rail'i çökmüyor |
| **Arıza tespiti** | Aşırı akım durumu master'a bildiriliyor |
| **S3 depo modu** | Modülleri **tamamen** beslemeden keser — µA değil, sıfır ([10 §4.1](10-enerji-butcesi.md#41-s3--mevcut-kararların-beklenmedik-yakınsaması)) |

**Ucuz alternatif:** slot başına polyfuse (~$0.05). Ama yavaş, soft-start
vermiyor ve arıza bildirimi yok. $1.15 fark için üç işlevi birden kaybetmek
mantıklı değil.

Bu karar [04 §5](04-backplane-mekanik.md#5-hot-plug-değerlendirmesi)'teki
hot-plug maliyetini de karşılıyor — load switch zaten gerekliydi.

---

## 8. Discovery akışı

### Karar · 🟡 D-34

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PCA9555 INT#  →  presence bitmap değişti                 │
├─────────────────────────────────────────────────────────────┤
│ 2. IDENTIFY(slot N)  →  32 byte descriptor                  │
├─────────────────────────────────────────────────────────────┤
│ 3. Doğrulama:                                               │
│      · CRC                                                  │
│      · Protokol versiyonu tanınıyor mu?                     │
│      · Güç bütçesi yeterli mi?                              │
│      · 2U ise N+1 boş mu?                                   │
├─────────────────────────────────────────────────────────────┤
│ 4. WRITE_CONFIG  →  kanal konfigürasyonu                    │
├─────────────────────────────────────────────────────────────┤
│ 5. ENABLE  →  modül tarama döngüsüne alınır                 │
└─────────────────────────────────────────────────────────────┘
```

### 8.1 Doğrulama başarısız olursa

| Durum | Davranış |
|-------|----------|
| CRC hatası | 3 kez tekrar, sonra "hatalı modül" işaretle |
| Bilinmeyen protokol versiyonu | Modül devre dışı, **raf çalışmaya devam eder** |
| Güç bütçesi aşımı | Reset bırakılmaz, Modbus'ta bildirilir |
| 2U ama N+1 dolu | Konfigürasyon hatası olarak bildirilir |

**Hiçbir başarısızlık durumu rafı düşürmüyor.** Tek bir arızalı veya uyumsuz
modül, çalışan sistemi etkilemiyor — bir platform ürünü için temel gereksinim.

### 8.2 Modülün kaybolması

```
PRESENT# yükseldi  →  modül çıkarıldı
   ↓
Master modülü tarama döngüsünden çıkarır
Güç bütçesi tahsisi serbest bırakılır
Modbus slot doluluk haritası güncellenir
Slot'un MOD_RST#'i tekrar aktif edilir (bir sonraki modül için hazır)
```

---

## 9. Slot durum makinesi

```
        ┌──────────┐
        │  EMPTY   │ ←──────────────────────┐
        └────┬─────┘                        │
             │ PRESENT# düştü               │ PRESENT# yükseldi
             ▼                              │ (her durumdan)
        ┌──────────┐                        │
        │ DETECTED │ ── reset'te tutuluyor  │
        └────┬─────┘                        │
             │ IDENTIFY başarılı            │
             ▼                              │
        ┌──────────┐                        │
        │IDENTIFIED│                        │
        └────┬─────┘                        │
             │ bütçe + versiyon OK          │
             ▼                              │
        ┌──────────┐                        │
        │CONFIGURED│                        │
        └────┬─────┘                        │
             │ ENABLE                       │
             ▼                              │
        ┌──────────┐    FAULT# / timeout    │
        │  ACTIVE  │ ──────────────┐        │
        └──────────┘               ▼        │
                              ┌────────┐    │
                              │ FAULTED│ ───┘
                              └────────┘
```

| Durum | Anlam | MOD_RST# |
|-------|-------|----------|
| EMPTY | Slot boş veya 2U tarafından kapatılmış | aktif (düşük) |
| DETECTED | Fiziksel olarak takılı, henüz tanınmadı | aktif |
| IDENTIFIED | Descriptor okundu, doğrulanıyor | aktif |
| CONFIGURED | Doğrulandı, konfigüre edildi | bırakıldı |
| ACTIVE | Tarama döngüsünde | bırakıldı |
| FAULTED | Arıza bildirdi veya yanıt vermiyor | duruma göre |
