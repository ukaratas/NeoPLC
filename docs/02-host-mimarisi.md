# 02 — Host Mimarisi

## 1. MCU seçimi

> 📎 **§1.1 ve §1.2 tarihseldir.** Aşağıdaki karşılaştırma ve gerekçeler, MCU
> seçiminin yapıldığı dönemde — Ethernet henüz host'ta planlanırken —
> geçerliydi. Ethernet sonradan host'tan çıkarıldı (D-47); **W5500 artık host
> mimarisinin parçası değil.** Seçimin bugün geçerli gerekçeleri §1.3'te.

### 1.1 Karşılaştırma (tarihsel — seçim dönemi)

| | **ESP32-S3 + W5500** | STM32G0/G4 + ESP32-C6 + W5500 | ESP32 + LAN8720 (RMII) | STM32H563 + PHY |
|---|---|---|---|---|
| WiFi | Dahili, **modül** ön sertifikalı | Ayrı modül, sertifikalı | Dahili | Yok — ek modül |
| Ethernet | SPI, donanım TCP/IP | SPI, donanım TCP/IP | RMII 50MHz + yazılım yığını | Dahili MAC + harici PHY |
| 2 katman uyumu | **İyi** | İyi | **Kötü** | Kötü |
| RT determinizmi | Orta → core pinning ile iyi | **Çok iyi** | Orta | Çok iyi |
| Firmware | **Tek image, tek toolchain** | İki image, iki toolchain | Tek | Tek |
| Lojik BOM (yaklaşık) | **~$7** | ~$10 | ~$6 | ~$14 |
| LCSC bulunabilirlik | **Çok yüksek** | Yüksek | Yüksek | Orta |
| Sertifikasyon riski | **Düşük** (hazır RF modülü) | Düşük | Düşük | — |

### 1.2 Seçim dönemindeki gerekçeler (tarihsel)

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

**Gerekçe 3 — hazır RF modülü sertifikasyon riskini alıyor.** WROOM modülü FCC/CE
ön sertifikalı. Kendi RF ön katımızı 2 katmanda tasarlamıyoruz.

**Gerekçe 4 — 16MB flash / 8MB PSRAM.** Web UI + OTA çift partisyon + **node
firmware imajlarının host'ta saklanması** için yeterli. Sonuncusu önemli:
[07](07-firmware-update.md)'deki merkezi güncelleme modelini mümkün kılıyor.

### 1.2.1 Dürüst karşı argümanlar

| Risk | Değerlendirme |
|------|---------------|
| Lockstep / ECC RAM yok | NeoPLC SIL iddiası taşımıyor ([01 §6](01-sistem-genel-bakis.md#6-kapsam-dışı-şimdilik)). Kabul edilebilir. |
| WiFi yığını jitter üretir | Core pinning azaltır, sıfırlamaz. Tarama süresinde 40× marj var ([05 §4](05-dahili-bus.md#4-hız-ve-tarama-süresi)) — bu marj jitter için tampon. |
| Ağ + kontrol tek noktada | Host arızası tüm rafı düşürür. Redundancy kapsam dışı. |
| Endüstriyel sıcaklık | WROOM-1 SKU'sunun -40..+85°C derecelendirmesi sipariş öncesi doğrulanmalı. |

### 1.3 Bugün geçerli gerekçeler · D-01

Ethernet host'tan çıktıktan sonra ESP32-S3-WROOM-1U-N16R8 seçimini ayakta tutan
gerekçeler:

| Gerekçe | Detay |
|---------|-------|
| **Wi-Fi + web UI** | Karavanda telefon kontrol panelidir; radyo modülde hazır ve ön sertifikalı ([§3](#3-wifi)) |
| **16 MB flash / 8 MB PSRAM** | Web UI + OTA çift partisyon + **node firmware imajlarının host'ta saklanması** ([07](07-firmware-update.md)) |
| **Çift çekirdek** | Core 0 ağ/UI, Core 1 backplane bus + Modbus RTU — tarama ağ trafiğinden izole |
| **Olgun OTA + rollback** | ESP-IDF'in çift partisyon mekanizması ([07 §5](07-firmware-update.md#5-host-ota)) |
| **Düşük güç modları** | Light/deep sleep, RTC GPIO uyandırma — enerji bütçesinin temeli ([10 §4](10-enerji-butcesi.md#4-güç-durumları)) |
| **Tedarik** | LCSC'de yüksek stok, düşük maliyet |

**Ethernet bu listede yok** — seçim artık ona bağlı değil.

### 1.4 Geçiş yolu (v2)

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

**Kuzeybound native = Host API (D-78).** Modbus TCP zorunlu değil; SCADA
isterse host adapter olarak eklenebilir. ESP32-S3 radyosu S0'da zaten açık.

| İhtiyaç | Çözüm |
|---------|-------|
| Kablolu, düşük enerjili, deterministik | **Saha RS-485 / Modbus RTU** (D-07) |
| Kablosuz, model/API, web UI | **WiFi / Host API** (D-78) |
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
| **25 mm yerleşim kısıtı ortadan kalktı** | Host'ta yüksek hızlı diferansiyel iz kalmadı |
| ~$3 BOM tasarrufu | W5500 + magjack |
| Kart alanı | Magjack hatırı sayılır yer kaplıyordu |
| **2 katman host uygulanabilir hale geldi** | [08 §5](08-emc-koruma.md#5-katman-sayısı-kararı) |

---

## 3. WiFi

| | Değer |
|---|---|
| Radyo | ESP32-S3 dahili (802.11 b/g/n + BLE 5) |
| Anten | **U.FL → kasa dışı anten** (pigtail / SMA) · 🟢 D-03 · modül `-1U` |
| **Varsayılan durum** | **KAPALI** — talep üzerine açılır · D-65 |

**Standart:** metal/metalize kasa + karavan gövdesi. PCB anten (`-1`) ölür.
U.FL host blade'de; kablo kasadaki SMA'ya. RP-SMA doğrudan PCB'ye yok —
blade çıkarılınca kablo kalır.

Kullanım: konfigürasyon web UI'ı, OTA, **Host API** (D-78).

### 3.1 WiFi neden varsayılan kapalı

| Senaryo | S1 boşta | Gerçekçi gün | Batarya ömrü |
|---------|----------|--------------|--------------|
| WiFi sürekli bağlı | 0.21 W | 3.5 Wh | 170 gün |
| **WiFi talep üzerine** | **0.13 W** | **2.2 Wh** | **273 gün** |
| WiFi tamamen yok (STM32'ye geçiş) | 0.15 W | 1.9 Wh | 320 gün |

**Kritik bulgu:** WiFi'ı tamamen atmakla talep üzerine açmak arasında sadece
**0.3 Wh/gün (%14)** fark var. Yani *WiFi'ın maliyeti varlığı değil, sürekli
bağlı kalması.*

Dahası: WiFi'ı tamamen atmanın kazancının çoğu radyodan değil,
**ESP32'den vazgeçip STM32'ye geçebilmekten** geliyor — bu da D-01'i ve tüm
host firmware yığınını değiştirir.

**Tamamen atmama gerekçesi:** Karavanda telefon kontrol panelidir. WiFi
atılırsa yerine fiziksel HMI/ekran gerekir — bir ekran 200 mW – 1 W çeker,
yani **WiFi'dan pahalıdır.** Enerjiyi WiFi'dan kısıp ekrana harcamak net kayıp.

### 3.2 Uyandırma mekanizması

```
Varsayılan (S1/S2)      :  WiFi kapalı, BLE advertising açık (~1–3 mW) · D-67
Telefon yaklaşır        →  WiFi AP açılır (süre konfigüre)
Kullanıcı butona basar  →  aynı AP, 10 dk (D-65 — yedek)
S3 (anahtar OFF)        :  BLE kapalı — depo bütçesi
```

Süre ve davranış konfigüre edilebilir olmalı — "sürekli açık" seçeneği de
sunulmalı; enerji bedelini kullanıcı görerek seçsin.

Buton ön panelde, host'un RTC GPIO'suna bağlı — S2/S3'ten de uyandırabilmeli
([10 §9.2](10-enerji-butcesi.md#92-uyandırma-kaynakları)). BLE S3'ü **uyandırmaz**;
S3 yalnız anahtar ON veya şarj/şebeke (D-44).

**BLE v1 · D-67.** Ekstra anten yok — WiFi ile aynı U.FL (D-03). Kod firmware
oturumunda; radyo ve anten donanımda hazır.

---

## 4. RS-485 saha portu

| | Değer |
|---|---|
| Topoloji | 2 tel yarım dupleks |
| İzolasyon | **İzole** — transceiver + izole DC-DC · 🟢 D-07 |
| Klemens | A / B / GND |
| Sonlandırma | DIP ile seçilebilir 120Ω |
| Bias | Fail-safe bias direnç çifti |
| Protokol | Modbus RTU, host/node yazılımdan seçilir |

**İzolasyon zorunlu · D-07.** Karavan da olsa saha loop ve invertör/ESS
kaçağı host'u yakar. İzolesiz PLC yok. ~$2–4 + 200 mW; S1/S2'de izole
besleme güç kapılı.

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
| VIN gerilim ölçümü (ADC) | 1 |
| Host sıcaklık (ADC) | 1 |
| Uyandırma: aç-kapa + şarj (RTC GPIO) | 2 |
| Durum LED'leri | 4 |
| Wi-Fi buton / config DIP | 2 |
| **Ara toplam** | **19** |
| **Yedek** | **~11** |

Ethernet'in düşmesiyle serbest kalan GPIO, karavan gereksinimlerini (batarya
ölçümü, uyandırma, sıcaklık) karşılıyor. Fan PWM/tacho yok — pasif soğutma
(D-57).

Bütçenin rahat olmasının tek sebebi, **slot başına ayrık hatların MCU'ya
çekilmemesidir.** Naif tasarım 32 GPIO isterdi; [06 §3](06-slot-yonetimi.md#3-host-tarafı-io-genişletme)'teki
üç katmanlı çözüm bunu 4 pine indiriyor.

UART tahsisi: UART0 = konsol/debug (native USB üzerinden), UART1 = RS-485 saha,
UART2 = backplane bus.

---

## 6. Bilgi modeli ve host API

### Karar: JSON şema + host API proxy · 🟢 D-78

Native sözleşme **düz Modbus ızgarası değil.** Host ve node aynı **JSON
modeller** üzerinden konuşur: tip güvenli, versiyonlu, akıllı req/res.
Şema ayrıntısı firmware oturumunda kilitlenir — burada katmanlar kilit.

```
İstemci  ──JSON / HTTP (veya eşdeğeri)──►  Host API
                                              │  proxy + aggregate
                                              │  model ↔ kompakt payload
Node     ◄── D-30 çerçeve (FUNC+PAYLOAD) ─────┘
```

| Katman | Ne kilitli | Ne firmware'de |
|--------|------------|----------------|
| **Model** | JSON Schema, req/res, node tipi = bir model ailesi | Alanlar, versiyon, hata kodları |
| **Host API** | Dış dünya host'a konuşur; host node'lara **proxy** | REST / WS / auth / OpenAPI |
| **Tel (backplane)** | D-30 ikili, max 70 byte, polling (D-33) | Payload codec (CBOR vb.) |
| **Modbus** | Native değil. SCADA gerekirse host **adapter** üretir | Register projeksiyonu |

**Telde ham JSON yok.** 64 byte payload + STOP node + 20 Hz tarama buna sığmaz.
Model JSON; bus kompakt. 2U = **tek** model örneği (sol elektrik, D-16).

~~D-27~~ (0x1000 + N×0x100 ızgara) **kilitlenmedi** — entegratör adresi değil,
host API kaynağıdır.

---

## 7. Host'un mekanik formu

### Karar: 2U blade, kendi özel slotunda · D-66

Host, şasi içinde ayrı bir bölme değil — **node'larla aynı mekanik forma sahip
bir blade.** 8U node kapasitesine ek olarak kendi 2U slotunu kullanır.

```
2U host + 8 × 1U node  =  35 + 140  =  175 mm   (+ duvarlar ≈ 185 mm)
ayrı bölmeli tasarım                 ≈  250 mm
                                        ─────────
                                         65 mm dar
```

### 7.1 Alan yeterli mi? — hesap

```
Host bileşen alanı toplamı        ≈  2 100 mm²
Routing ve keepout ile            ≈  4 000 – 6 000 mm²

1U blade PCB, tek yüz (75 × 110)  =  8 250 mm²
```

**Alan hiç kısıt değil** — tek yüze bile sığıyor. Blade mimarisinde PCB yüz
alanı slot adımından bağımsız; 17.5 mm *kalınlık* yönüdür, PCB yüzü 75 × 110 mm.

### 7.2 Gerçek kısıt: bileşen yüksekliği

| Bileşen | Yükseklik | 1U (14.4 mm) | 2U (31.9 mm) |
|---------|-----------|--------------|--------------|
| ESP32-S3-WROOM-1U | 3.2 mm | ✓ | ✓ |
| Buck indüktörü | 4–6 mm | ✓ | ✓ |
| İzole DC-DC | 8–12 mm | sınırda | ✓ |
| CM choke | 8–15 mm | ⚠ | ✓ |
| Giriş bulk elektrolitik (63 V) | 11–16 mm | ⚠ | ✓ |

**2U, alan için değil yükseklik için seçildi.** Alçak profilli CM choke ve
polimer kapasitörle 1U da mümkün olabilir; parça seçiminde yeniden
değerlendirilecek.

### 7.3 Uygulama kısıtları

| Kısıt | Gerekçe |
|-------|---------|
| **Host konnektörü node'unkinden farklı** | Slot başına RST#/PRESENT# hatları host'a gidiyor, node konnektöründe yok |
| **Mekanik keying zorunlu** | Node host slotuna, host node slotuna takılamamalı — yanlış takma hasar verir |
| **DC giriş klemensi arka panelde** | 2.5 A giriş akımı kart kenarı fingerlarından geçmemeli; arka panelden doğrudan host blade'ine gider |
| Host çıkardığında sistem durur | Kabul edilen davranış — node'lar reset'te kalır (D-22), çıkışlar güvenli duruma geçer |

### 7.4 Kazançlar

- Host da node gibi **servis edilebilir ve değiştirilebilir**
- Aynı kızak, ön panel ve kapalı vida tooling'i — tek mekanik tasarım
- Host kendi hava kanalını alıyor ([04 §6](04-backplane-mekanik.md#6-hava-akışı-ve-termal))
- Şasi 65 mm daralıyor

---

## 8. Host blok diyagramı

```
   12–48V DC
       │
  ┌────▼─────────────────────────┐
  │ Giriş koruma (bkz. 03 §1)    │
  │ sigorta·CM choke·TVS·FET     │
  └────┬────────────────┬────────┘
       │ VBUS (dahili)  │
       │           ┌────▼──────┐
       │           │ Buck      │ 5V @ 3A
       │           │ 12-48→5V  │
       │           └────┬──────┘
       │                │ +5V
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
  │  BACKPLANE (12 pin)   GND ×2 · +5V ×2 · BUS_A/B        │
  │                       MOD_RST# · PRESENT# · 4× rezerve  │
  └──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬────┘
   slot0  slot1  slot2  slot3  slot4  slot5  slot6  slot7
     ↑ her slotta akım sınırlı load switch (+5V)
```
