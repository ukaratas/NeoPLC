# 02 — Host Mimarisi

## 1. MCU seçimi

### Karşılaştırma

| | **ESP32-S3 + W5500** | STM32G0/G4 + ESP32-C6 + W5500 | ESP32 + LAN8720 (RMII) | STM32H563 + PHY |
|---|---|---|---|---|
| WiFi | Dahili, node sertifikalı | Ayrı node, sertifikalı | Dahili | Yok — ek node |
| Ethernet | SPI, donanım TCP/IP | SPI, donanım TCP/IP | RMII 50MHz + yazılım yığını | Dahili MAC + harici PHY |
| 2 katman uyumu | **İyi** | İyi | **Kötü** | Kötü |
| RT determinizmi | Orta → core pinning ile iyi | **Çok iyi** | Orta | Çok iyi |
| Firmware | **Tek image, tek toolchain** | İki image, iki toolchain | Tek | Tek |
| Lojik BOM (yaklaşık) | **~$7** | ~$10 | ~$6 | ~$14 |
| LCSC bulunabilirlik | **Çok yüksek** | Yüksek | Yüksek | Orta |
| Sertifikasyon riski | **Düşük** (hazır node) | Düşük | Düşük | — |

### Karar: ESP32-S3-WROOM-1U-N16R8

**Gerekçe 1 — W5500 kısıt K3'ü çözüyor.** RMII, 50MHz saat + 4 sinyalin
kontrollü empedansla taşınmasını ister. 2 katman 1.6mm FR4'te bu pratik değil
(bkz. [08 §5](08-emc-koruma.md#5-katman-sayısı-kararı)). W5500 aynı işi SPI
üzerinden yapar ve TCP/IP yığınını donanımda taşır — Modbus TCP sunucusu 8
eşzamanlı sokete kadar neredeyse bedava gelir.

**Gerekçe 2 — çift çekirdek determinizm sorununu yönetilebilir kılıyor.**

```
Core 0 : WiFi yığını · lwIP · web UI · OTA        (best effort)
Core 1 : Backplane bus yöneticisi · Modbus RTU        (deterministik, pinned)
```

Backplane taraması ağ trafiğinden izole edilir. Bu, ESP32'ye yöneltilen "RT için
uygun değil" itirazının pratikteki cevabıdır — ama tamamen ortadan kaldırmaz
(aşağıya bakınız).

**Gerekçe 3 — hazır node sertifikasyon riskini alıyor.** WROOM node'u FCC/CE
ön sertifikalı. Kendi RF ön katımızı 2 katmanda tasarlamıyoruz.

**Gerekçe 4 — 16MB flash / 8MB PSRAM.** Web UI + OTA çift partisyon + **node
firmware imajlarının host'ta saklanması** için yeterli. Sonuncusu önemli:
[07](07-firmware-update.md)'deki merkezi güncelleme modelini mümkün kılıyor.

### Dürüst karşı argümanlar

| Risk | Değerlendirme |
|------|---------------|
| Lockstep / ECC RAM yok | NeoPLC SIL iddiası taşımıyor ([01 §6](01-sistem-genel-bakis.md#6-kapsam-dışı-şimdilik)). Kabul edilebilir. |
| WiFi yığını jitter üretir | Core pinning azaltır, sıfırlamaz. Tarama süresinde 40× marj var ([05 §4](05-dahili-bus.md#4-hız-ve-tarama-süresi)) — bu marj jitter için tampon. |
| Ağ + kontrol tek noktada | Host arızası tüm rafı düşürür. Redundancy kapsam dışı. |
| Endüstriyel sıcaklık | WROOM-1 SKU'sunun -40..+85°C derecelendirmesi sipariş öncesi doğrulanmalı. |

### Geçiş yolu (v2)

Gerçek hard-real-time veya SIL hedefi doğarsa: **STM32G0B1 + ESP32-C6-MINI.**

Backplane protokolü MCU'dan bağımsız tasarlandığı için **bu geçiş node'ları
etkilemez** — sahadaki node'lar aynen çalışmaya devam eder. Platform
mimarisinin asıl kazancı burada görünüyor.

---

## 2. Ethernet — host'tan çıkarıldı

### Karar: W5500 host kartında yok · D-47

Ethernet, host'un **en büyük tek sürekli yüküydü**:

```
W5500 + magjack, link up     =  495 mW
Sürekli açık                 =  11.9 Wh/gün
Sistemin geri kalanı         =  ~3.5 Wh/gün
                                ─────────────
Tek başına sistemin 3.4 katı
```

RS-485 aynı işi (kablolu, deterministik dış haberleşme) çok daha ucuza yapıyor:

| | Ethernet (W5500) | RS-485 2 tel |
|---|---|---|
| Sürekli tüketim | **495 mW** | 200 mW (izole) · **~3 mW** (izolesiz) |
| Güç kapılanabilir mi? | Evet ama link düşer | Evet, boşta kapatılabilir |
| Kablo | 4–8 telli, RJ45 | **2 tel + GND** |
| Protokol | Modbus TCP | Modbus RTU |
| BOM | ~$3 (W5500 + magjack) | ~$0.20 |
| Kart alanı | Magjack + 25 mm yerleşim kısıtı | Klemens |

### 2.1 Ne kaybediliyor, ne kaybedilmiyor

**Modbus TCP kaybolmuyor** — WiFi üzerinden sunulmaya devam ediyor. ESP32-S3'ün
radyosu zaten var ve S0 durumunda zaten açık.

| İhtiyaç | Çözüm |
|---------|-------|
| Kablolu, düşük enerjili, deterministik | **RS-485 / Modbus RTU** |
| Kablosuz, yüksek bant genişliği, web UI | **WiFi / Modbus TCP** |
| Kablolu Ethernet zorunluysa | **Haberleşme node'u olarak takılır** (§2.2) |

### 2.2 Ethernet bir node olarak

Kablolu Ethernet gerçekten gerekirse, host donanımına değil **bir slota**
takılıyor:

- Kullanıcı ihtiyacı yoksa enerjisini hiç ödemiyor
- Node çıkarıldığında tüketim sıfır
- Host kartı sade ve düşük güçlü kalıyor
- Platform felsefesine uygun: opsiyonel yetenek = opsiyonel node

Bu, modüler mimarinin tam olarak çözmek için var olduğu problem.

### 2.3 Yan kazançlar

| Kazanç | Detay |
|--------|-------|
| 6 GPIO serbest kaldı | SPI + INT + RST |
| **25 mm yerleşim kısıtı ortadan kalktı** | 100BASE-TX diferansiyel izleri yok |
| ~$3 BOM tasarrufu | W5500 + magjack |
| Kart alanı | Magjack hatırı sayılır yer kaplıyordu |
| **2 katman host uygulanabilir hale geldi** | [08 §5](08-emc-koruma.md#5-katman-sayısı-kararı) |

---

## 3. WiFi

| | Değer |
|---|---|
| Radyo | ESP32-S3 dahili (802.11 b/g/n + BLE 5) |
| Anten | **U.FL konnektör + harici anten** (`-1U` node varyantı) |

**PCB anten neden elenmiş:** NeoPLC metal veya metalize endüstriyel kutu içinde
DIN rayına monte edilecek. PCB anten bu ortamda çalışmaz. Node varyantı seçimi
(`-1` PCB anten vs `-1U` U.FL) geri dönülemez bir kart kararıdır — baştan doğru
seçilmeli.

Kullanım: konfigürasyon web UI'ı, OTA, ikincil Modbus TCP erişimi.

---

## 4. RS-485 saha portu

| | Değer |
|---|---|
| Topoloji | 2 tel yarım dupleks |
| İzolasyon | **İzole** — transceiver + izole DC-DC · 🟡 D-07 |
| Klemens | A / B / GND |
| Sonlandırma | DIP ile seçilebilir 120Ω |
| Bias | Fail-safe bias direnç çifti |
| Protokol | Modbus RTU, host/node yazılımdan seçilir |

**İzolasyon gerekçesi:** Ek maliyet ~$2–4. Buna karşılık izolasyonsuz RS-485,
saha ground loop'larında endüstriyel kurulumların en yaygın arıza kaynağıdır.
Endüstriyel güvenilirlik iddiasının en görünür sınandığı nokta burası.

Maliyet baskısı olursa çıkarılabilir bir kalem — ama bilinçli olarak
çıkarılmalı, unutularak değil.

> ⚠️ Bu port, dahili backplane bus'ı ile **karıştırılmamalıdır**. İkisi de
> RS-485 fiziksel katmanı kullanır ama tamamen ayrı hatlardır, ayrı
> protokollerdir ve backplane tarafı izole değildir.

---

## 5. GPIO bütçesi

ESP32-S3-WROOM-1U-N16R8: octal PSRAM GPIO 33–37'yi tüketir, kullanılabilir
≈ 30 GPIO.

| Fonksiyon | Pin |
|-----------|-----|
| RS-485 saha portu (TX, RX, DE) | 3 |
| Backplane bus (TX, RX, DE) | 3 |
| I²C slot expander (SDA, SCL) + INT# | 3 |
| FAULT# wired-OR girişi | 1 |
| SYNC çıkışı | 1 |
| VBUS_RAW gerilim ölçümü (ADC) | 1 |
| Uyandırma girişleri (RTC GPIO) | 2 |
| Fan PWM + tacho | 2 |
| Durum LED'leri | 4 |
| Buton / config DIP | 2 |
| **Ara toplam** | **22** |
| **Yedek** | **~8** |

Ethernet'in düşmesiyle serbest kalan 6 GPIO, karavan bağlamının getirdiği yeni
gereksinimleri (batarya ölçümü, uyandırma, fan kontrolü) fazlasıyla karşılıyor.

Bütçenin rahat olmasının tek sebebi, **slot başına ayrık hatların MCU'ya
çekilmemesidir.** Naif tasarım 32 GPIO isterdi; [06 §3](06-slot-yonetimi.md#3-host-tarafı-io-genişletme)'teki
üç katmanlı çözüm bunu 4 pine indiriyor.

UART tahsisi: UART0 = konsol/debug (native USB üzerinden), UART1 = RS-485 saha,
UART2 = backplane bus.

---

## 6. Modbus register haritası

Dış SCADA'nın düz ve öngörülebilir bir adres uzayı görmesi entegratör deneyimi
için kritik. · 🟡 D-27

```
0x0000 – 0x00FF    Sistem
                     0x0000  Firmware versiyonu
                     0x0002  Slot doluluk haritası (bit N = slot N dolu)
                     0x0003  Slot hata haritası
                     0x0004  Sistem durum bayrakları
                     0x0010  Tarama süresi (µs)
                     0x0012  Hata sayaçları (CRC, timeout)
                     0x0020  Güç bütçesi: tahsis / kullanım

0x1000 + N×0x100   Slot N proses imajı   (N = 0..7)
     +0x00 .. 0x3F   Girişler                      (read)
     +0x40 .. 0x7F   Çıkışlar                      (read/write)
     +0x80 .. 0xBF   Durum / diagnostik            (read)
     +0xC0 .. 0xFF   Node descriptor              (read)
```

Slot başına sabit 0x100'lük blok, node tipi ne olursa olsun adres hesabını
sabit tutuyor: `slot_taban = 0x1000 + slot_no × 0x100`. Entegratör tek formülle
çalışıyor.

---

## 7. Host blok diyagramı

```
   12–48V DC
       │
  ┌────▼─────────────────────────┐
  │ Giriş koruma (bkz. 03 §1)    │
  │ sigorta·CM choke·TVS·FET     │
  └────┬────────────────┬────────┘
       │ VBUS_RAW       │
       │           ┌────▼──────┐
       │           │ Buck      │ 5V @ 3A
       │           │ 12-48→5V  │
       │           └────┬──────┘
       │                │ +5V_SYS
       │                ├──────────────┐
       │                │         ┌────▼─────┐
       │                │         │ 5V→3.3V  │
       │                │         └────┬─────┘
       │                │              │ +3V3
       │                │              │
       │                │        ┌─────▼──────┐
       │                │        │ ESP32-S3   │  WiFi ──→ U.FL anten
       │                │        │ WROOM-1U   │
       │                │        └─┬───┬───┬──┘
       │                │          │   │   │
       │                │          │   │   └─UART1─→ İzole RS-485 ──→ A/B klemens
       │                │          │   │              (güç kapılı)
       │                │          │   └─I²C──→ PCA9555 ──→ 8× PRESENT#
       │                │          │                   └──→ 8× MOD_RST#
       │                │          │
       │                │          └─UART2─→ RS-485 xcvr ─┐
       │                │                            │
  ┌────▼────────────────▼────────────────────────────▼─────┐
  │  BACKPLANE   VBUS_RAW · +5V_SYS · BUS_A/B · ADDR0-3    │
  │              FAULT# · SYNC · BOOT# · PRESENT# · RST#   │
  └──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬────┘
   slot0  slot1  slot2  slot3  slot4  slot5  slot6  slot7
     ↑ her slotta akım sınırlı load switch (+5V_SYS)
```
