# 07 — Firmware Update ve Bootloader

---

## 1. Dağıtım modeli

| Seçenek | Değerlendirme |
|---------|---------------|
| **Host, node FW'ini dahili bus üzerinden yazar** | **Tek web UI'dan tüm raf güncellenir.** FW imajları host'a **Wi-Fi / web UI** üzerinden yüklenir ve host'un 16 MB flash'ında saklanır. *(Kablolu Ethernet yalnız opsiyonel Ethernet haberleşme node'u takılıysa alternatif taşıma kanalı olabilir — D-47.)* |
| Node üzerinde SWD header | Cihazı açmak gerekir. Saha servisi için kabul edilemez. |
| Node başına USB | Maliyet ve pin israfı — K1'i ihlal ediyor |

### Karar: bus üzerinden merkezi güncelleme

ESP32-S3'ün 16MB flash'ı bu modeli mümkün kılıyor
([02 §1](02-host-mimarisi.md#13-bugün-geçerli-gerekçeler-d-01)) — node
firmware imajları host'ta saklanabiliyor.

**Saha senaryosu:** Teknisyen web UI'a bağlanır, yeni node firmware'ini yükler,
"slot 3'ü güncelle" veya "tüm DI node'larını güncelle" der. Hiçbir kapak
açılmaz, hiçbir kablo sökülmez.

---

## 2. Bootloader yapısı

### Seçenekler

Örnek MCU: STM32G030 sınıfı, 64 KB flash.

```
Çift bank:  [BL 16K][App A 24K][App B 24K]    → app başına 24 KB
Tek app:    [BL 16K][App 46K][meta 2K]        → app 46 KB
```

### Karar: tek app + CRC + bootloader penceresi

**Çift bank'in tek gerçek kazancı:** "güncelleme sırasında güç kesilirse eski
sürüme dön."

**Bu senaryonun bizdeki maliyeti düşük:**

- App CRC'si tutmazsa bootloader'da kalır
- Host node'un bootloader'da olduğunu görür
- Host imajı yeniden yazar
- Node fiziksel olarak host'a bağlı — **her zaman erişilebilir**

**Buna karşılık çift bank'in maliyeti yüksek:** ucuz MCU'da app alanını yarıya
indiriyor (46 KB → 24 KB). Bu, node firmware'inin yapabileceklerini doğrudan
sınırlıyor ve daha pahalı MCU'ya zorlayabilir — K1'e aykırı.

> **Koşul:** Bu karar, node MCU'sunun flash kapasitesine bağlı. 128 KB+ flash'lı
> bir MCU seçilirse çift bank yeniden değerlendirilmeli. D-37 (node MCU
> ailesi) kararlaştırıldığında bu karar tekrar gözden geçirilecek.

### 2.1 Flash haritası

```
0x0800 0000  ┌──────────────────────────┐
             │  Bootloader     16 KB    │  ← yazma korumalı
0x0800 4000  ├──────────────────────────┤
             │                          │
             │  Uygulama       46 KB    │
             │                          │
0x0800 F800  ├──────────────────────────┤
             │  Metadata        2 KB    │
             │    · app CRC32           │
             │    · app uzunluğu        │
             │    · app versiyonu       │
             │    · geçerlilik bayrağı  │
0x0801 0000  └──────────────────────────┘
```

### 2.2 Açılış akışı

```
Reset
  ↓
Bootloader başlar
  ↓
~30 ms bus penceresi: "bootloader'da kal" geldi mi?  ──evet──→  Kal
  ↓ hayır
Metadata geçerlilik bayrağı set mi?  ──hayır──→  Bootloader modunda kal
  ↓ evet
App CRC32 hesapla ve karşılaştır  ──uyuşmuyor──→  Bootloader modunda kal
  ↓ uyuşuyor
Uygulamaya atla
```

Üç bağımsız kontrol — hiçbiri tek başına node'u kurtarılamaz hale getirmiyor.

---

## 3. Güncelleme akışı

Fonksiyon kodları 0x20–0x2F ([05 §7](05-dahili-bus.md#7-fonksiyon-kodları)).

```
┌───────────────────────────────────────────────────────────────┐
│ 1. Host: DISABLE(slot N)                                    │
│      → çıkışlar güvenli duruma, node tarama döngüsünden çıkar│
├───────────────────────────────────────────────────────────────┤
│ 2. Host: RST# çek-bırak + pencerede "bootloader'da kal"     │
│      → node bootloader'a girer                               │
├───────────────────────────────────────────────────────────────┤
│ 3. Host: IDENTIFY → bootloader versiyonu ve kapasitesi      │
├───────────────────────────────────────────────────────────────┤
│ 4. Host: ERASE                                              │
│      → metadata geçerlilik bayrağı ÖNCE silinir               │
├───────────────────────────────────────────────────────────────┤
│ 5. Host: WRITE_BLOCK × N   (64 byte payload / blok)         │
│      → her blok kendi CRC'si ile, hatalı blok tekrarlanır     │
├───────────────────────────────────────────────────────────────┤
│ 6. Host: VERIFY → node tüm app CRC32'sini hesaplar         │
├───────────────────────────────────────────────────────────────┤
│ 7. Host: ACTIVATE → metadata yazılır, geçerlilik bayrağı set│
├───────────────────────────────────────────────────────────────┤
│ 8. Host: RST# çek-bırak (pencerede komut yok) → yeni app    │
├───────────────────────────────────────────────────────────────┤
│ 9. Host: IDENTIFY → yeni FW versiyonu doğrulanır            │
├───────────────────────────────────────────────────────────────┤
│ 10. Host: CONFIG + ENABLE → tarama döngüsüne geri alınır    │
└───────────────────────────────────────────────────────────────┘
```

**Adım 4'ün sırası kritik:** Geçerlilik bayrağı flash silinmeden **önce**
temizlenir. Böylece güncelleme herhangi bir noktada kesilirse node asla yarım
bir app'i çalıştırmaya kalkmaz.

### 3.1 Süre tahmini

```
Tipik node app'i          ≈  32 KB
Blok boyutu                =  64 byte
Blok sayısı                =  512

Blok başına süre (500 kbaud):
    WRITE_BLOCK çerçevesi  =  70 byte  ×  20 µs  =  1.40 ms
    ACK                    =   8 byte  ×  20 µs  =  0.16 ms
    flash yazma            ≈                        1.00 ms
                                                   ────────
                                                   ~2.6 ms

Toplam  =  512 × 2.6 ms  ≈  1.3 saniye
```

Kabul edilebilir. 8 node'un tamamı ~11 saniyede güncellenir.

### 3.2 Güncelleme sırasında sistem

**Diğer slotlar çalışmaya devam eder.** Bus paylaşılmış olsa da güncelleme
trafiği normal tarama ile araya girer:

- Host her N blokta bir normal tarama döngüsü yapar
- Tarama süresi geçici olarak uzar (~4.8 ms → ~15 ms)
- Bu, tipik PLC tarama süresinin (10–100 ms) içinde kalıyor

Alternatif — güncelleme sırasında taramayı tamamen durdurmak — daha hızlı biter
ama prosesi durdurur. **Kademeli yaklaşım tercih ediliyor.**

---

## 4. Kurtarma

| Senaryo | Kurtarma yolu |
|---------|---------------|
| Güncelleme sırasında güç kesildi | Geçerlilik bayrağı temiz → bootloader'da kalır → host yeniden yazar |
| App CRC hatası | Bootloader'da kalır → host yeniden yazar |
| App açılıyor ama kilitleniyor | **RST# + bootloader penceresi** → bootloader'a zorla |
| App bus'ı sürekli meşgul ediyor | MOD_RST# ile node reset'te tutulur; gerekirse diğer node'lar da susturulur |
| Bootloader bozuldu | ⚠️ Kurtarılamaz — SWD gerekir |

**Son satır bilinçli bir risktir.** Bootloader yazma korumalı ve asla
güncellenmiyor. Karmaşıklığı sınırlamak için kabul edilen tek kurtarılamaz
senaryo.

> **Tasarım notu:** Node PCB'sinde fabrika programlaması ve son çare kurtarma
> için SWD test noktaları (pad, konnektör değil) bulunmalı. Maliyeti sıfır,
> üretimde zorunlu.

---

## 5. Host OTA

### Karar: ESP32 çift partisyon + rollback

Node'da çift bank'i eledik ama host'ta kullanıyoruz — çelişki değil:

| | Node | Host |
|---|---|---|
| Flash | 64 KB — çift bank app'i yarıya indirir | 16 MB — çift partisyon bedava |
| Erişilebilirlik | Host her zaman yeniden yazabilir | **Host bozulursa kimse kurtaramaz** |
| Ekosistem | Kendi bootloader'ımız | ESP-IDF'in olgun, test edilmiş OTA'sı |

Host'ta rollback'in maliyeti sıfır, kazancı yüksek. Node'da tersi.

```
factory  │  ota_0  │  ota_1  │  nvs  │  spiffs (web UI + node FW imajları)
```

Yeni firmware pasif partisyona yazılır, boot bayrağı değiştirilir, sonraki
açılışta yeni sürüm çalışır. Uygulama kendini "sağlıklı" işaretlemezse ESP-IDF
otomatik olarak eski partisyona döner.

---

## 6. Versiyon uyumluluğu

Host ve node firmware'leri bağımsız güncellenebildiği için uyumsuzluk
kaçınılmaz.

**Kural: protokol versiyonu descriptor'ın ilk baytıdır**
([05 §7.1](05-dahili-bus.md#71-node-descriptorı-identify-yanıtı)).

| Durum | Davranış |
|-------|----------|
| Node protokol versiyonu = host'unki | Normal çalışma |
| Node versiyonu daha eski, host destekliyor | Uyumluluk modunda çalışır |
| Node versiyonu daha yeni veya tanınmıyor | **Node devre dışı, raf çalışmaya devam eder**, Modbus'ta bildirilir |

Host, desteklediği protokol versiyonlarının listesini tutar. Geriye uyumluluk
host'un sorumluluğu — node basit kalır (K1).
